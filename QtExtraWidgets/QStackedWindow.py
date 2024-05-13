#!/usr/bin/env python3
import sys
import os
import importlib
import inspect
import time
from queue import Queue
import traceback
from PySide2.QtWidgets import QLabel, QWidget, QGridLayout,QListWidget,QListWidgetItem,QStackedWidget,QHeaderView
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QRunnable,Slot,QThreadPool,QObject
from QtExtraWidgets import QPushInfoButton as qinfo,QTableTouchWidget as qtouch
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
		self.parent=kwargs.get("parent")
		if self.parent==None:
			for i in args:
				if isinstance(i,QWidget):
					self.parent=i
		super(QStackedWindow,self).__init__(self.parent)
		self.dbg=True
		self.current=-1
		self.referer=-1
		self.setAttribute(Qt.WA_DeleteOnClose, True)
		self.lblBanner=QLabel()
		#self.lstPortrait=QListWidget()
		self.lstPortrait=qtouch.QTableTouchWidget()
		self.lstNav=QListWidget()
		self.stkPan=QStackedWidget()
		self.curStack=None
		self.rsrc="/usr/share/appconfig"
		self._renderGui()
		self.showPortrait()
	#def init
	
	def _debug(self,msg):
		if self.dbg:
			print("StackedWindow: {}".format(msg))
	#def _debug

	def _renderGui(self):
		lay=QGridLayout()
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
	
	def _getRowForIdx(self,idx):
		row=0
		for cont in range(0,self.lstNav.count()):
			w=self.lstNav.item(cont)
			if w.data(Qt.UserRole)==idx:
				row=cont
				break
		return(row)
	#def _getRowForIdx

	def _endSetCurrentStack(self,idx,oldcursor,parms=None):
		if self.curStack!=None:
			lay=self.layout()
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
		self.curStack=self.getCurrentStack()
		self.setCursor(oldcursor)
	#def _endSetCurrentStack

	def setCurrentStack(self,*args,**kwargs):
		self.showPortrait(False)
		oldcursor=self.cursor()
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
			if widget.btnAccept.isEnabled()==True and widget.btnAccept.isVisible==True:
				if hasattr(widget,"dlgPendingChanges"):
					cont=widget.dlgPendingChanges()
					if cont<0:
						self.lstNav.setCurrentRow(self.current)
						self.setCursor(oldcursor)
						return
					elif cont==0:
						widget.btnAccept.clicked.emit()
						widget.updated.connect(lambda: self._endSetCurrentStack(idx,oldcursor,parms))
						return
		self._endSetCurrentStack(idx,oldcursor,parms)
	#def setCurrentStack

	def setIcon(self,ficon):
		self._debug("Icon: {}".format(ficon))
		if os.path.isfile(ficon):
			icon=QtGui.QIcon(ficon)
		else:
			icon=QtGui.QIcon.fromTheme(ficon)
		self.setWindowIcon(icon)
	#def setIcon

	def setBanner(self,banner):
		if not os.path.isfile(banner):
			if os.path.isfile(os.path.join(self.rsrc,banner)):
				banner=os.path.join(self.rsrc,banner)
			else:
				banner=""
				self._debug("Banner not found at {}".format(self.rsrc))
		self.lblBanner.setPixmap(banner)
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
		item.setToolTip(props.get("tooltip"))
		idx=props.get("index")
		item.setData(Qt.UserRole,idx)
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
			lbl=QLabel("&nbsp;&nbsp;<a href=\"{0}\"><span style=\"font-weight:bold;text-decoration:none\">{1}</span></a>".format(idx,item.toolTip()))
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
#class QStackedWindow
