#!/usr/bin/env python3
import sys
from functools import partial
import os
import importlib
import inspect
import time
from queue import Queue
import traceback
from PySide6.QtWidgets import QApplication,QLabel, QWidget, QGridLayout,QListWidget,QListWidgetItem,QStackedWidget,QHeaderView
from PySide6 import QtGui
from PySide6.QtCore import Qt,Signal,QRunnable,Slot,QThreadPool,QObject,QSize
from QtExtraWidgets import QPushInfoButton as qinfo,QTableTouchWidget as qtouch
import notify2
QString=type("")
QInt=type(0)

class signalsLoader(QObject):
	finished = Signal("PyObject")
#class signalsLoader

class moduleLoader(QRunnable):
	def __init__(self,path,queue,parent=None):
		QRunnable.__init__(self, parent)
		self.path=path
		self.queue=queue
		self.signals=signalsLoader()
	#def __init__

	@Slot()
	def run(self):
		module=None
		spec=None
		index=-1
		if self.path.endswith(".py") and os.path.basename(self.path)!='__init__.py':
			if os.path.dirname(self.path) not in sys.path:
				sys.path.append( os.path.dirname(self.path))
			modName=os.path.basename(self.path.replace(".py","")).replace("/",".")
			try:
				modpackage=os.path.basename(os.path.dirname(self.path))
				spec = importlib.util.spec_from_file_location("{}.{}".format(modpackage,modName),self.path,submodule_search_locations=[os.path.dirname(self.path)])
				module = importlib.util.module_from_spec(spec)
			except Exception as e:
				self._debug("Unable to load {0} (perhaps aux lib): {1}".format(module,str(e)))
				module=None
				traceback.print_exc()
		self.queue.put((module,spec))
	#def run
#class moduleLoader

class QStackedWindow(QWidget):
	def __init__(self,*args,**kwargs):
		self.wparent=kwargs.get("parent")
		if self.wparent==None:
			for i in args:
				if isinstance(i,QWidget):
					self.wparent=i
		super(QStackedWindow,self).__init__(self.wparent)
		self.setParent(self.wparent)
		self.dbg=True
		self.current=-1
		self.referer=-1
		self.setAttribute(Qt.WA_DeleteOnClose, True)
		self.lblBanner=QLabel()
		#self.lstPortrait=QListWidget()
		self.lstPortrait=qtouch.QTableTouchWidget()
		self.lstNav=QListWidget()
		self.stkPan=QStackedWidget()
		self.rsrc="/usr/share/appconfig"
		self.notify=notify2
		self.destroyed.connect(partial(QStackedWindow._onDestroy,self.__dict__))
		self._renderGui()
		self.showPortrait()
	#def init

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]
		if "stkPan" in selfDict:
			for c in range(0,selfDict["stkPan"].count()):
				w=selfDict["stkPan"].widget(c)
				selfDict["stkPan"].removeWidget(w)
				w.deleteLater()
	#def _onDestroy
	
	def _debug(self,msg):
		if self.dbg:
			print("StackedWindow: {}".format(msg))
	#def _debug

	def _renderGui(self):
		lay=QGridLayout()
		lay.setContentsMargins(1,1,2,1)
		lay.addWidget(self.lblBanner,0,0,1,2,Qt.AlignCenter)
		lay.addWidget(self.lstNav,1,0,1,1)
		self.lstNav.activated.connect(self.setCurrentStack)
		self.lstNav.itemClicked.connect(self.setCurrentStack)
		lay.addWidget(self.stkPan,1,1,1,1)
		lay.setColumnStretch(1,1)
		lay.addWidget(self.lstPortrait,1,1,1,1)
		self.setLayout(lay)
	#def _renderGui

	def getCurrentStackIndex(self):
		return(self.current)
	#def getCurrentStack

	def getCurrentStack(self):
		return(self.stkPan.currentWidget())
	#def getCurrentStack

	def widget(self,idx):
		return(self.stkPan.widget(idx))
	#def widget
	
	def _getRowForIdx(self,idx):
		row=0
		for cont in range(0,self.lstNav.count()):
			w=self.lstNav.item(cont)
			if w.data(Qt.UserRole)==idx:
				row=cont
				break
		return(row)
	#def _getRowForIdx

	def _endSetCurrentStack(self,idx,parms=None):
		self.referer=self.current
		if idx<0:
			idx=self.lstNav.currentRow()
		else:
			idx=self._getRowForIdx(idx)
		self.lstNav.setCurrentRow(idx)
		self.current=idx
		if parms!=None:
			self.stkPan.widget(self.current).setParms(parms)
			#self.curStack.updateScreen()
		self.stkPan.setCurrentIndex(self.current)
		self.setCursor(self.oldcursor)
	#def _endSetCurrentStack

	def setCurrentStack(self,*args,**kwargs):
		self.showPortrait(False)
		self.oldcursor=self.cursor()
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		parms=kwargs.get("parms",None)
		idx=kwargs.get("idx",-1)
		if idx<0:
			for arg in args:
				if isinstance(arg,int):
					idx=arg
					break
		widget=self.stkPan.currentWidget()
		if hasattr(widget,"btnAccept"):
			if widget.btnAccept.isEnabled()==True and widget.btnAccept.isVisible()==True:
				if hasattr(widget,"dlgPendingChanges"):
					cont=widget.dlgPendingChanges()
					if cont<0:
						self.lstNav.setCurrentRow(self.current)
						self.setCursor(self.oldcursor)
						return
					elif cont==0:
						widget.btnAccept.clicked.emit()
						widget.updated.connect(lambda: self._endSetCurrentStack(idx,parms))
						return
		self._endSetCurrentStack(idx,parms)
	#def setCurrentStack

	def setIcon(self,ficon):
		#Wayland only:
		# setwindowIcon doesn't works under Wayland
		# so the standar expects icon from .desktop
		# as a dirty hack the assumption is that a desktop file with the ficon name must exists
		# ex: "repoman" icon -> net.lliurex.repoman.desktop
		# so desktop file search could be avoided
		#IMPORTANT: desktop file must match convention of reverse domain standard (xx.xx.xxxxx.desktop)
		if isinstance(ficon,str):
			icon=self._getIconFromPath(ficon)
			if icon.isNull()==True:
				icon=QtGui.QIcon.fromTheme(ficon)
		elif isinstance(ficon,QtGui.QIcon):
			icon=ficon
		elif isinstance(ficon,QtGui.QPixmap):
			icon=QtGui.QIcon.addPixmap(ficon,QtGui.QIcon.Mode.Normal)
		desktopFile=self._getDesktopFromIcon(icon,ficon)
		#QtGui.QGuiApplication.setDesktopFileName(os.path.basename(desktopFile))
		QtGui.QGuiApplication.setDesktopFileName(desktopFile)
		self.setWindowIcon(icon)
		super(QStackedWindow,self).setWindowIcon(icon)
	#def setIcon(self,ficon):

	def _getIconFromPath(self,ficon):
		self._debug("Icon from: {}".format(ficon))
		icon=QtGui.QIcon()
		if os.path.isfile(ficon):
			icon.addFile(ficon)
		return(icon)
	#def _getIconFromPath

	def _getDesktopFromIcon(self,icon,ficon):
		self._debug("Search desktop for icon: {} (name: {})".format(icon,icon.name()))
		iconName=icon.name()
		if icon.isNull() and isinstance(ficon,str):
			iconName=os.path.basename(ficon)
		desktopPaths=["/usr/share/applications",os.path.join(os.environ["HOME"],".local","share","applications")]
		dFile=""
		for dpath in desktopPaths:
			tfile=os.path.join(dpath,"{}.desktop".format(iconName))
			cfile=os.path.join(dpath,"net.lliurex.{}.desktop".format(iconName))
			if os.path.isfile(tfile):
				dFile=tfile
				break
			elif os.path.isfile(cfile):
				dFile=cfile
				break
		if os.path.exists(dFile)==False:
			dFile=self._deepSearchDesktopFromIcon(iconName)
		dFile=os.path.basename(dFile).replace(".desktop","")
		self._debug("Desktop: {}".format(dFile))
		return(dFile)
	#def _getDesktopFromIcon

	def _deepSearchDesktopFromIcon(self,iconName):
		self._debug("DeepSearch desktop for icon: {}".format(iconName))
		desktopPaths=["/usr/share/applications",os.path.join(os.environ["HOME"],".local","share","applications")]
		dFile=""
		for dpath in desktopPaths:
			if os.path.exists(dpath):
				for fpath in os.scandir(dpath):
					if fpath.path.endswith("{}.desktop".format(iconName)):
						dFile=fpath.path
						break
			if dFile!="":
				break
		if dFile=="":
			for dpath in desktopPaths:
				for fpath in os.scandir(dpath):
					if fpath.is_file()==False:
						continue
					try:
						with open(fpath.path,"r") as f:
							for fline in f.read().split("\n"):
								if iconName in fline and fline.lower().startswith("icon"):
									dFile=fpath.path
									break
					except:
						continue
					if dFile!="":
						break
				if dFile!="":
					break
		return(dFile)
	#def _deepSearchDesktopFromIcon

	def setBanner(self,banner):
		pxm=banner
		if not os.path.isfile(banner):
			if os.path.isfile(os.path.join(self.rsrc,banner)):
				banner=os.path.join(self.rsrc,banner)
			else:
				banner=""
				self._debug("Banner not found at {}".format(self.rsrc))
		if os.path.isfile(banner):
			pxm=QtGui.QPixmap(QtGui.QImage(banner))
			
		if isinstance(pxm,QtGui.QPixmap) or isinstance(pxm,QtGui.QImage):
			self.lblBanner.setPixmap(pxm)
	#def setBanner

	def disableNavBar(self,state):
		if isinstance(state,bool)==False:
			state=True
		self.lstNav.setVisible(not state)
		self.showPortrait(not state)
	#def disableNavBar

	def addStack(self,stack,**kwargs):
		callback=kwargs.get("callback",stack.__initScreen__)
		props=stack.getProps()
		stack.parent=self
		icon=QtGui.QIcon.fromTheme(props.get("icon"))
		self.stkPan.insertWidget(props.get("index"),stack)
		item=QListWidgetItem(icon,props.get("shortDesc"))
		self.lstNav.setIconSize(QSize(24,24))
		item.setToolTip(props.get("tooltip"))
		idx=props.get("index")
		item.setData(Qt.UserRole,idx)
		item.setData(Qt.AccessibleDescriptionRole,props.get("longDesc"))
		#item.setIcon(icon)
		self.lstNav.insertItem(idx,item)
		if props.get("visible",True)==False:
			item.setHidden(True)
		callback()
	#def addStack

	def _inspectModule(self,module,spec):
		index=-1
		moduleClass=None
		try:
			spec.loader.exec_module(module)
		except Exception as e:
			print("ERROR on {}: {}".format(module,e))
			module=None
			#traceback.print_exc()
		if module:
			for includedClass in inspect.getmembers(module, predicate=inspect.isclass):
				name,obj=(includedClass)
				if name.lower()==module.__name__.split(".")[-1].lower():
					test=includedClass[1]
					try:
						moduleClass=test(parent=self)
					except Exception as e:
						traceback.print_exc()
						continue
					if hasattr(moduleClass,"enabled"):
						if moduleClass.enabled==False:
							moduleClass=None
							continue
					props=moduleClass.getProps()
					index=props.get("index",-1)
		return(index,moduleClass)
	#def _inspectModule

	def addStacksFromFolder(self,dpath="stacks"):
		if os.path.isdir(dpath)==False:
			print("addStacksFromFolder: ./{} not found".format(dpath))
			return
		modulesByIndex={}
		self.queue=Queue()
		self.threadpool = QThreadPool()
		for plugin in os.scandir(dpath):
			self._debug("Inspecting file {}".format(plugin.path))
			loader=moduleLoader(plugin.path,self.queue)
			self.threadpool.start(loader)
		self.threadpool.waitForDone()
		while self.queue.empty()==False:
			moduleClass=None
			(module,spec)=self.queue.get()
			(index,moduleClass)=self._inspectModule(module,spec)
			if moduleClass!=None:
				if index==-1:
					index=len(modulesByIndex)
				modulesByIndex.update({index:moduleClass})
		for mod in sorted(modulesByIndex.keys()):
			self.addStack(modulesByIndex[mod])
		if len(modulesByIndex)<=1:
			self.disableNavBar(True)
		else:
			self.generatePortrait()
	#def _importStacks(self):

	def _linkStack(self,*args):
		idx=-1
		if len(args)>0:
			if isinstance(args[0],int):
				idx=args[0]
			elif isinstance(args[0],str):
				if args[0].isnumeric()==True:
					idx=int(args[0])
			if idx==-1:
				cRow=self.lstPortrait.currentRow()
				cCol=self.lstPortrait.currentColumn()
				idx=(cRow*cCol)+cCol
		else:
			idx=self.lstPortrait.currentRow()
		self.lstNav.setCurrentRow(idx)
		self.setCurrentStack()
	#def _linkStack

	def _fillGrid(self):
		cols=self.tblGrid.columnCount()
		curCol=0
		for idx in range(self.lstNav.count()):
			item=self.lstNav.item(idx)
			if curCol==cols or self.lstPortrait.rowCount()==0:
				curCol=0
				self.lstPortrait.setRowCount(self.lstPortrait.rowCount()+1)
				self.lstPortrait.verticalHeader().setSectionResizeMode(self.lstPortrait.rowCount()-1,QHeaderView.ResizeToContent)
				self.lstPortrait.horizontalHeader().setSectionResizeMode(self.lstPortrait.ColumnCount()-1,QHeaderView.Stretch)
			btn=qinfo.QPushInfoButton()
			btn.setText(item.text())
			icn=item.icon()
			btn.setIcon(icn)
			btn.setDescription(item.toolTip())
			btn.clicked.connect(self._linkStack)
			#("&nbsp;&nbsp;<a href=\"{0}\"><span style=\"font-weight:bold;text-decoration:none\">{1}</span></a>".format(idx,item.toolTip()))
			self.lstPortrait.setCellWidget(self.lstPortrait.rowCount()-1,curCol,btn)
			curCol+=1
	#def _fillGrid(self):

	def _fillList(self):
		self.lstPortrait.setColumnCount(1)
		self.lstPortrait.setShowGrid(False)
		for idx in range(self.lstNav.count()):
			item=self.lstNav.item(idx)
			self.lstPortrait.setRowCount(self.lstPortrait.rowCount()+1)

			txt=item.data(Qt.AccessibleDescriptionRole)
			if len(txt)<=0:
				txt=item.toolTip()
			lbl=QLabel("&nbsp;&nbsp;<a href=\"{0}\"><span style=\"font-weight:bold;text-decoration:none\">{1}</span></a>".format(idx,txt))
			lbl.setTextFormat(Qt.RichText)
			lbl.setAlignment(Qt.AlignTop)
			lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
			lbl.linkActivated.connect(self._linkStack)
			lbl.setAccessibleName(item.text())
			lbl.setAccessibleDescription(item.toolTip())
			self.lstPortrait.setCellWidget(self.lstPortrait.rowCount()-1,0,lbl)
	#def fillList(self):

	def generatePortrait(self,mode="list",cols=1):
		txt=[]
		#lay=QGridLayout()
		self.lstPortrait.setRowCount(0)
		self.lstPortrait.setColumnCount(3)
		self.lstPortrait.verticalHeader().hide()
		self.lstPortrait.horizontalHeader().hide()
		self.lstPortrait.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		if mode=="grid":
			self._fillGrid()
		else:
			self._fillList()
	#def generatePortrait

	def showPortrait(self,show=True):
		self.lstPortrait.setVisible(show)
		self.stkPan.setVisible(not show)
	#def showPortrait
			
	def setWiki(self,url):
		desc=("Wiki")
		lbl_wiki=QLabel("<a href=\"{0}\"><span style=\"text-align: right;\">{1}</span></a>".format(url,desc))
		lbl_wiki.setOpenExternalLinks(True)
		lbl_wiki.setToolTip(url)
		self.layout().addWidget(lbl_wiki,0,1,Qt.AlignTop|Qt.AlignRight)
	#def setWiki

	def showNotification(self,title="",summary="",text="",icon="",timeout=0):
		if self.notify.is_initted()==False:
			self.notify.init(title)
		else:
			self.notify.appname=title
		self._debug("Sending {}".format(text))
		notify=self.notify.Notification(summary,text,icon)
		if timeout>0:
			notify.timeout=timeout
		notify.show()
	#def showNotification
#class QStackedWindow
