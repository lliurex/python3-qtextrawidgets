#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QLabel, QPushButton,QGridLayout,QHBoxLayout,QSizePolicy
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal
from QtExtraWidgets import QTableTouchWidget,QStackedWindowItem,QInfoLabel

class QPushInfoButton(QPushButton):
	clicked=Signal("PyObject")
	def __init__(self,parent=None):
		QPushButton.__init__(self, parent)
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
		if os.path.exists(self.cacheDir)==False:
			os.makedirs(self.cacheDir)
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.label=QLabel()
		self.label.setWordWrap(True)
		self.description=QLabel()
		self.description.setWordWrap(True)
		self.icon=QLabel()
		self.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		lay=QGridLayout()
		lay.addWidget(self.icon,0,0,2,1)
		lay.addWidget(self.label,0,1,1,1)
		lay.addWidget(self.description,1,1,1,1)
		self.setDefault(True)
		self.setLayout(lay)
		self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum))
		self.loadImg("")
	#def __init__

	def loadImg(self,img):
		if os.path.isfile(img):
			icn=QtGui.QPixmap.fromImage(img)
		elif img!='':
			icn2=QtGui.QIcon.fromTheme(img)
			icn=icn2.pixmap(128,128)
		else:
			icn2=QtGui.QIcon.fromTheme("preferences-system")
			icn=icn2.pixmap(128,128)
		if icn:
			wsize=128
			self.icon.setPixmap(icn.scaled(wsize,128,Qt.KeepAspectRatio,Qt.SmoothTransformation))
		self.adjustSize()
	#def loadImg

	def setIcon(self,icon):
		if isinstance(icon,QtGui.QIcon):
			self.icon.setPixmap(icon.pixmap(128,128))
			self.adjustSize()
	#def setIcon

	def text(self):
		return(self.label.text())

	def setText(self,text):
		self.label.setText(text)
		self.label.setStyleSheet("font-weight: bold;")
		self.adjustSize()
	#def setText(self,text)

	def setDescription(self,text):
		self.description.setText(text)
		self.adjustSize()

	def setTooltipText(self,text):
		self.setToolTip("{0}".format(text))
	
	def activate(self):
		self.clicked.emit(self)
	#def activate

	def keyPressEvent(self,ev):
		if ev.key() in [Qt.Key_Return,Qt.Key_Enter,Qt.Key_Space]:
			self.clicked.emit(self)
		ev.ignore()
	#def keyPressEvent(self,ev):

	def mousePressEvent(self,*args):
		self.clicked.emit(self)
	#def mousePressEvent
#class QPushButtonRebostApp
