#!/usr/bin/env python3
import os
from functools import partial
import traceback
from PySide2.QtWidgets import QDialog,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QLabel,QPushButton,QLineEdit,\
	QRadioButton,QCheckBox,QComboBox,QTableWidget,QSlider,QScrollArea,QMessageBox,QCalendarWidget
from PySide2 import QtGui
#from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt,QUrl,QObject, Slot, Signal, Property,QThread,QSize,QTimer
from QtExtraWidgets.QInfoLabel import QInfoLabel
import logging
import gettext
try:
	confText=gettext.translation("python3-qtextrawidgets")
	_ = confText.gettext
except:
	gettext.textdomain('python3-qtextrawidgets')
	_ = gettext.gettext
#_ = nullTrans.gettext

class QStackedWindowItem(QWidget):
	updated=Signal()
	destroyed=Signal()
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		if kwargs.get("parent","")!="":
			self.parent=kwargs["parent"]
		else:
			for i in args:
				if isinstance(i,QWidget):
					self.parent=i
					break
		self.dbg=False
		self.props={"icon":'shell',
			"shortDesc":_("Configure stack"),
			"longDesc":_("Configure custom stack"),
			"tooltip":_("From here you can configure something"),
			"index":1,
			"enabled":True,
			"visible":True,
			"changed":False
		}
		self.changes=False
		self.level='user'
		#self.stack=stack
		self.textdomain='python3-qtextrawiggets'
		self.btnAccept=QPushButton(_("Apply"))
		self.btnCancel=QPushButton(_("Undo"))
		self.btnCancel.clicked.connect(self.updateScreen)
		self.statusMsg=QInfoLabel()
		self.connectWdgs=[]
		self.__init_stack__()
		self.updateScreen=self.decoratorUpdateScreen(self.updateScreen)
		self.__initScreen__=self.decoratorInitScreen(self.__initScreen__)
		self.destroyed.connect(partial(QStackedWindowItem._onDestroy,self.__dict__))
	#def __init__

	@staticmethod
	def _onDestroy(*args):
		selfDict=args[0]

	def __init_stack__(self):
		raise NotImplementedError("__init_stack not implemented")
	#def __init_stack__

	def parent(self):
		return(self.parent)
	#def parent
	
	def _debug(self,msg):
		desc="current"
		if self.dbg:
			if hasattr(self,"description"):
				desc=self.description
			print("Stack {0}: {1}".format(desc,msg))
	#def _debug

	def dlgPendingChanges(self):
		txt=_("Current configuration has changed")
		txt2=_("Do you wish to apply or to discard changes?")
		msgBox=QMessageBox()
		msgBox.setText(txt)
		msgBox.setInformativeText(txt2)
		msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
		msgBox.setDefaultButton(QMessageBox.Save)
		ret=msgBox.exec()
		if ret==QMessageBox.Save:
			ret=0
		elif ret==QMessageBox.Discard:
			ret=1
		elif ret==QMessageBox.Cancel:
			ret=-1
		return(ret)
	#def pendingChanges

	def decoratorInitScreen(self,func):
		def states():
			func()
			layout=self.layout()
			if layout:
				self._recursiveSetupEvents(layout)
				box_btns=QHBoxLayout()
				box_btns.addWidget(self.statusMsg)
				self.statusMsg.setVisible(False)
				box_btns.insertStretch(1)
				box_btns.addWidget(self.btnAccept)
				box_btns.addWidget(self.btnCancel)
				if isinstance(layout,QGridLayout):
					idx=layout.rowCount()
				align=Qt.AlignBottom|Qt.AlignRight
				if self.btnAccept.isEnabled()==False:
					idx=0
				if isinstance(layout,QGridLayout):
					layout.addLayout(box_btns,idx,0,1,layout.columnCount(),Qt.AlignTop|Qt.AlignRight)
				elif isinstance(layout,QVBoxLayout) or isinstance(layout,QHBoxLayout):
					layout.addLayout(box_btns,Qt.AlignBottom|Qt.AlignRight)
		return (states)
	#def decoratorInitScreen

	def __initScreen__(self):
		print("__initScreen__ method not implemented in this stack")
		raise NotImplementedError()
	#def __initScreen(self)__:

	def _resetScreen(self):
		self.updateScreen()
		#self.setChanged(False)
	#def _reset_screen

	def decoratorUpdateScreen(self,func):
		def states(*args):
			self._debug("Updating screen: Disconnecting signals")
			self._debug("Settting events from layout {0} to {1}".format(self.layout,True))
			self._recursiveSetupEvents(self.layout(),block=True)
			func(*args)
			self._debug("Updated screen: Connecting signals")
			self._debug("Settting events from layout {0} to {1}".format(self.layout,False))
			self._recursiveSetupEvents(self.layout(),block=False)
			self.setChanged(False)
			self.updated.emit()
		return (states)
	#def decoratorUpdateScreen

	def updateScreen(self):
		raise NotImplementedError("updateScreen method not implemented in this stack")
	#def updateScreen

	def _recursiveBlockEvents(self,widget,block=True):
		if widget==None or widget in [self.btnAccept,self.btnCancel]:
			return
		widget.blockSignals(block)
		if isinstance(widget,QTableWidget):
			for x in range (0,widget.rowCount()):
				for y in range (0,widget.columnCount()):
					tableWidget=widget.cellWidget(x,y)
					self._recursiveBlockEvents(tableWidget,block)
		if isinstance(widget,QScrollArea):
			wdg=widget.widget()
			if wdg:
				self._recursiveBlockEvents(wdg,block)
			else:
				lay=widget.layout()
				if lay:
					self._recursiveBlockEvents(lay,block)
		else:
			if type(widget) in [QGridLayout,QVBoxLayout,QHBoxLayout]:
				self._recursiveSetupEvents(widget,block=block)
			else:
				try:
					if widget.layout():
						self._recursiveSetupEvents(widget.layout())
				except:
						self._recursiveSetupEvents(widget,block=block)
	#def _recursiveBlockEvents(widget):

	def _getSignalForConnection(self,widget):
		if isinstance(widget,QCheckBox):
			#widget.stateChanged.connect(self.setChanged,Qt.UniqueConnection)
			widget.stateChanged.connect(lambda x: self.setChanged(True,widget),Qt.AutoConnection)
			self.connectWdgs.append(widget)
		if isinstance(widget,QRadioButton):
			widget.toggled.connect(lambda x: self.setChanged(True,widget),Qt.AutoConnection)#self.setChanged,Qt.UniqueConnection)
			self.connectWdgs.append(widget)
		elif isinstance(widget,QComboBox):
			widget.currentTextChanged.connect(lambda x: self.setChanged(True,widget),Qt.AutoConnection)#(self.setChanged,Qt.UniqueConnection)
			self.connectWdgs.append(widget)
		elif isinstance(widget,QLineEdit):
			widget.textChanged.connect(lambda x: self.setChanged(True,widget),Qt.AutoConnection)#(self.setChanged,Qt.UniqueConnection)
			self.connectWdgs.append(widget)
		elif isinstance(widget,QSlider):
			widget.valueChanged.connect(lambda x: self.setChanged(True,widget),Qt.AutoConnection)#(self.setChanged,Qt.UniqueConnection)
			self.connectWdgs.append(widget)
		elif isinstance(widget,QCalendarWidget):
			widget.selectionChanged.connect(lambda: self.setChanged(True,widget),Qt.AutoConnection)#(self.setChanged,Qt.UniqueConnection)
			self.connectWdgs.append(widget)
		elif isinstance(widget,QPushButton):
			if widget.menu():
				widget.menu().triggered.connect(lambda x: self.setChanged(True,widget),Qt.AutoConnection)#(self.setChanged,Qt.UniqueConnection)
			else:
				widget.clicked.connect(lambda x: self.setChanged(True,widget),Qt.AutoConnection)#(self.setChanged,Qt.UniqueConnection)
			self.connectWdgs.append(widget)
		elif 'dropButton' in str(widget):
			widget.drop.connect(lambda x: self.setChanged(True,widget),Qt.AutoConnection)#(self.setChanged,Qt.UniqueConnection)
			self.connectWdgs.append(widget)
		elif isinstance(widget,QTableWidget):
			widget.cellChanged.connect(lambda x: self.setChanged(True,widget),Qt.AutoConnection)#(self.setChanged,Qt.UniqueConnection)
		widget.blockSignals(False)
	#def _getSignalForConnection

	def _recursiveExploreWidgets(self,widget):
		if widget==None or widget in [self.btnAccept,self.btnCancel]:
			return
		self._getSignalForConnection(widget)
		if isinstance(widget,QTableWidget):
			for x in range (0,widget.rowCount()):
				for y in range (0,widget.columnCount()):
					tableWidget=widget.cellWidget(x,y)
					self._recursiveExploreWidgets(tableWidget)
		if isinstance(widget,QScrollArea):
			wdg=widget.widget()
			if wdg:
				self._recursiveExploreWidgets(wdg)
			else:
				lay=widget.layout()
				if lay:
					self._recursiveExploreWidgets(lay)
		else:
			if type(widget) in [QGridLayout,QVBoxLayout,QHBoxLayout]:
				self._recursiveSetupEvents(widget)
			else:
				try:
					if widget.layout():
						self._recursiveSetupEvents(widget.layout())
				except:
					self._recursiveExploreWidgets(widget)
				#	self._recursiveSetupEvents(widget)
		return
	#def _recursiveExploreWidgets(widget):

	def _recursiveSetupEvents(self,layout,block=None):
		if layout==None:
			return
		for idx in range(0,layout.count()):
			widget=layout.itemAt(idx).widget()
			if widget!=None:
				if widget in self.connectWdgs:
					continue	
			if isinstance(widget,QWidget):
				if block==None:
					self._recursiveExploreWidgets(widget)
				else:
					self._recursiveBlockEvents(widget,block)

			elif layout.itemAt(idx).layout():
				self._recursiveSetupEvents(layout.itemAt(idx).layout(),block)
	#def _recursiveSetupEvents

	def showEvent(self,event):
		try:
			self.updateScreen()
		except NotImplementedError as e:
			print("updateScreen method is not implemented in this stack")
			traceback.print_exc()
		except Exception as e:
			print("{}".format(e))
			traceback.print_exc()
	#def showEvent

	def hideControlButtons(self):
		self.btnAccept.hide()
		self.btnAccept.setEnabled(False)
		self.btnCancel.hide()
	#def hideControlButtons(self):

	def setChanged(self,state=True,*args):
		if (self.btnAccept.isVisible() or self.btnCancel.isVisible())==False:
			return
		if state!=self.btnAccept.isEnabled():
			self.btnAccept.setEnabled(state)
		if state!=self.btnCancel.isEnabled():
			self.btnCancel.setEnabled(state)
		if state!=self.props["changed"]:
			self.props["changed"]=state
			self._debug("New State: {}".format(state))
	#def setChanged

	def getChanges(self):
		self._debug("Read state: {}".format(self.props["changed"]))
		return(self.props["changed"])
	#def getChanges

	def setParms(self,parms):
		return
	#def setParms

	def setProps(self,*args,**kwargs):
		self.props["icon"]=kwargs.get("icon",self.props.get("icon"))
		self.props["shortDesc"]=kwargs.get("shortDesc",self.props.get("shortDesc"))
		self.props["longDesc"]=kwargs.get("longDesc",self.props.get("longDesc"))
		self.props["tooltip"]=kwargs.get("tooltip",self.props.get("tooltip"))
		self.props["index"]=kwargs.get("index",self.props.get("index"))
		self.props["enabled"]=kwargs.get("enabled",self.props.get("enabled"))
		self.props["visible"]=kwargs.get("visible",self.props.get("visible"))
	#def __setProps__

	def getProps(self):
		return(self.props)
	#def getProps

	def showMsg(self,*args,**kwargs):
		text=""
		timeout=0
		if len(args)>0:
			for arg in args:
				if isinstance(arg,str) and text=="":
					text=arg
				if isinstance(arg,int) and timeout==0:
					timeout=arg
		if kwargs.get("text","")!="":
			text=kwargs["text"]
		if kwargs.get("timeout",0)!=0:
			timeout=kwargs["timeout"]
		if kwargs.get("summary","")!="":
			text="<STRONG>{0}</STRONG><br>{1}".format(kwargs["summary"],text)
		self.statusMsg.setText(text)
		self.statusMsg.setTimeout(timeout)
		self.statusMsg.setVisible(True)
	#def showMsg

	def hideMsg(self):
		self.statusMsg.setVisible(False)
	#def hideMsg

	def sendNotify(self,**kwargs):
		if self.parent!=None:
			if hasattr(self.parent,"showNotification"):
				notifyIcon=self.props["icon"]
				if isinstance (kwargs.get("icon",None),str):
					if os.path.exists(kwargs["icon"]):
						notifyIcon=kwargs["icon"]
				self.parent.showNotification(kwargs.get("title",
												self.props["shortDesc"]),
												kwargs.get("summary",""),
												kwargs.get("text",""),
												notifyIcon,
												kwargs.get("timeout",0))
	#def showMsg
#class QStackedWindowItem
