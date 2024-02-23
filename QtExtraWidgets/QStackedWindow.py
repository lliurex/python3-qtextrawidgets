#!/usr/bin/env python3
import sys
import os
import importlib
import inspect
import time
import traceback
from PySide2.QtWidgets import QLabel, QWidget, QGridLayout,QListWidget,QListWidgetItem,QStackedWidget
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal

QString=type("")
QInt=type(0)

class QStackedWindow(QWidget):
	def __init__(self,*args,**kwargs):
		parent=kwargs.get("parent")
		if parent==None:
			for i in args:
				if isinstance(i,QWidget):
					parent=i
		super(QStackedWindow,self).__init__(parent)
		self.dbg=False
		self.current=-1
		self.referer=-1
		self.setAttribute(Qt.WA_DeleteOnClose, True)
		self.lblBanner=QLabel()
		self.lstPortrait=QListWidget()
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
	#def _endSave

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
	#def addStack(self,stack,**kwargs):
	
	def _importModuleFromFile(self,fmodule):
		module=None
		if fmodule.endswith(".py") and os.path.basename(fmodule)!='__init__.py':
			sys.path.append( os.path.dirname(fmodule))
			modName=os.path.basename(fmodule.replace(".py","")).replace("/",".")
			try:
				modpackage=os.path.basename(os.path.dirname(fmodule))
				spec = importlib.util.spec_from_file_location("{}.{}".format(modpackage,modName),fmodule,submodule_search_locations=[os.path.dirname(fmodule)])
				module = importlib.util.module_from_spec(spec)
			except Exception as e:
				self._debug("Unable to load {0} (perhaps aux lib): {1}".format(module,str(e)))
				module=None
				traceback.print_exc()
			try:
				spec.loader.exec_module(module)
			except Exception as e:
				print("ERROR on {}: {}".format(module,e))
				module=None
				traceback.print_exc()
		return(module)
	#def _importModuleFromFile

	def _getClassFromMod(self,module):
		moduleClass=None
		for includedClass in inspect.getmembers(module, predicate=inspect.isclass):
			name,obj=(includedClass)
			if name.lower()==module.__name__.split(".")[-1].lower():
				test=includedClass[1]
				try:
					moduleClass=test(parent=self)
				except Exception as e:
					self._debug("Unable to import {0}: {1}".format(module,str(e)))
					traceback.print_exc()
				else:
					break
		if moduleClass!=None:
			if hasattr(moduleClass,"enabled"):
				if moduleClass.enabled==False:
					moduleClass=None
		return(moduleClass)
	#def _getClassFromMod

	def addStacksFromFolder(self,dpath="stacks"):
		if os.path.isdir(dpath)==False:
			print("addStacksFromFolder: ./{} not found".format(dpath))
			return
		modulesByIndex={}
		for plugin in os.scandir(dpath):
			module=self._importModuleFromFile(plugin.path)
			if module!=None:
				moduleClass=self._getClassFromMod(module)
				if moduleClass!=None:
					props=moduleClass.getProps()
					modulesByIndex[props.get("index",1)]=moduleClass
		for mod in sorted(modulesByIndex.keys()):
			self.addStack(modulesByIndex[mod])
		if len(modulesByIndex)<=1:
			self.disableNavBar(True)
		else:
			self.generatePortrait()
	#def _importStacks(self):

	def _linkStack(self,*args):
		if len(args)>0:
			idx=int(args[0])
		else:
			idx=self.lstPortrait.currentRow()
		self.lstNav.setCurrentRow(idx)
		self.setCurrentStack()
	#def _linkStack

	def generatePortrait(self):
		txt=[]
		#lay=QGridLayout()
		for idx in range(self.lstNav.count()):
			item=self.lstNav.item(idx)
			lbl=QLabel("&nbsp;&nbsp;<a href=\"{0}\"><span style=\"font-weight:bold;text-decoration:none\">{1}</span></a>".format(idx,item.toolTip()))
			lbl.setTextFormat(Qt.RichText)
			lbl.setAlignment(Qt.AlignTop)
			lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
			lbl.linkActivated.connect(self._linkStack)
			itm=QListWidgetItem()
			self.lstPortrait.addItem(itm)
			self.lstPortrait.setItemWidget(itm,lbl)
		#self.lstPortrait.setText("<br>".join(txt))
		self.lstPortrait.itemSelectionChanged.connect(self._linkStack)
		#lay.addWidget(lst,0,0,1,1)
		#self.lstPortrait.setLayout(lay)
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
