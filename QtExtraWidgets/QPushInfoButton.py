#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QLabel, QPushButton,QGridLayout,QHBoxLayout,QSizePolicy
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QSize
from QtExtraWidgets import QTableTouchWidget,QStackedWindowItem,QInfoLabel
import requests

ICON_SIZE=128

class QPushInfoButton(QPushButton):
	#clicked=Signal("PyObject")
	def __init__(self,parent=None):
		super().__init__()
		self.cacheDir=os.path.join(os.environ.get('HOME'),".cache","rebost","imgs")
		if os.path.exists(self.cacheDir)==False:
			os.makedirs(self.cacheDir)
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.label=QLabel()
		self.label.setWordWrap(True)
		self.lblDesc=QLabel()
		self.lblDesc.setWordWrap(True)
		self.icon=QLabel()
		self.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		lay=QGridLayout()
		lay.setColumnStretch(0,0)
		lay.setColumnStretch(1,1)
		lay.addWidget(self.icon,0,0,2,1,Qt.AlignLeft)
		lay.addWidget(self.label,0,1,1,1)
		lay.addWidget(self.lblDesc,1,1,1,1)
		self.defaultSize=ICON_SIZE
		self.setDefault(True)
		self.setLayout(lay)
		self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum))
		self.loadImg("")
	#def __init__

	def loadImg(self,img):
		if os.path.exists(img):
			icn=QtGui.QPixmap(img)
		elif img!='':
			if img.startswith("http"):
				raw=requests.get(img)
				icn=QtGui.QPixmap()
				icn.loadFromData(raw.content)
			else:
				icn2=QtGui.QIcon.fromTheme(img)
				icn=icn2.pixmap(self.defaultSize,self.defaultSize)
		else:
			icn2=QtGui.QIcon.fromTheme("preferences-system")
			icn=icn2.pixmap(self.defaultSize,self.defaultSize)
		if icn:
			wsize=self.defaultSize
			self.icon.setPixmap(icn.scaled(wsize,self.defaultSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
		self.icon.setFixedSize(QSize(self.defaultSize,self.defaultSize))
		self.adjustSize()
	#def loadImg

	def setIcon(self,icon):
		if isinstance(icon,QtGui.QIcon):
			self.icon.setPixmap(icon.pixmap(self.defaultSize,self.defaultSize))
			self.icon.setFixedSize(QSize(self.defaultSize,self.defaultSize))
			self.adjustSize()
	#def setIcon

	def text(self):
		return(self.label.text())
	#def text

	def setText(self,text):
		self.label.setText(text)
		self.setAccessibleName(text)
		font=self.label.font()
		font.setBold(True)
		self.label.setFont(font)
		#self.label.setStyleSheet("font-weight: bold;")
		self.adjustSize()
	#def setText(self,text)

	def description(self):
		return(self.lblDesc.text())
	#def description

	def setDescription(self,text):
		self.lblDesc.setText(text)
		self.setAccessibleDescription(text)
		self.adjustSize()

	def setTooltipText(self,text):
		self.setToolTip("{0}".format(text))
	
	def activate(self):
		self.clicked.emit()
	#def activate

	def keyPressEvent(self,ev):
		if ev.key() in [Qt.Key_Return,Qt.Key_Enter,Qt.Key_Space]:
			self.clicked.emit()
		ev.ignore()
	#def keyPressEvent(self,ev):

#	def mousePressEvent(self,*args):
#		self.clicked.emit(self)
#	#def mousePressEvent

#class QPushButtonRebostApp
