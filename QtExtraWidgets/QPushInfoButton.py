#!/usr/bin/python3
import sys
import os
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout,QHBoxLayout,QLabel
from PySide6 import QtGui
from PySide6.QtCore import Qt,Signal,QSize
from QtExtraWidgets import QTableTouchWidget,QStackedWindowItem,QScrollLabel,QStyledLabel
import requests

ICON_SIZE=128

class QPushInfoButton(QPushButton):
	#clicked=Signal("PyObject")
	def __init__(self,parent=None,overlay=False,scroll=False):
		super().__init__()
		self.cacheDir=os.path.join("/tmp",".cache","imgs")
		if os.path.exists(self.cacheDir)==False:
			os.makedirs(self.cacheDir)
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.overlay=overlay
		self.scroll=scroll
		self.defaultSize=ICON_SIZE
		self.__initGui__()
	#def __init__

	def __initGui__(self,*args):
		self.label=QLabel()
		self.label.setWordWrap(True)
		if self.overlay==True or self.scroll==True:
			self.lblDesc=QScrollLabel.QScrollLabel()
			if self.scroll==True:
				self.label.setStyleSheet("""border:1px;background-color:rgba(50,50,50,200);color:silver;padding:5px""")
				mW=self.font().pointSize()
				self.label.setMaximumWidth(mW*20)
		else:
			self.lblDesc=QLabel()
		self.icon=QLabel()
		self.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
		lay=QGridLayout(self)
		lay.setColumnStretch(0,1)
		lay.setColumnStretch(1,2)
		if self.overlay==True:
			self.lblDesc.hide()
			lay.addWidget(self.icon,0,0,2,1,Qt.AlignLeft|Qt.AlignCenter)
			lay.addWidget(self.label,0,1,2,1)
			lay.addWidget(self.lblDesc,0,0,2,2)
		elif self.scroll==True:
			lay.addWidget(self.label,0,0,1,2,Qt.AlignRight|Qt.AlignTop)
			lay.addWidget(self.icon,0,1,1,1,Qt.AlignCenter|Qt.AlignTop)
			lay.addWidget(self.lblDesc,1,0,1,2)
			lay.setRowStretch(0,0)
			lay.setRowStretch(1,1)
		else:
			lay.addWidget(self.icon,0,0,1,1,Qt.AlignLeft|Qt.AlignCenter)
			lay.addWidget(self.label,0,1,1,1)
			lay.addWidget(self.lblDesc,1,1,1,1)
	#def __initGui__

	def setSpacing(self,spacing):
		self.layout().setSpacing(spacing)
	#def setSpacing

	def loadImg(self,img):
		if img==None:
			img=""
		if os.path.exists(img):
			icn=QtGui.QPixmap(img)
		elif img!='':
			imgName=os.path.basename(img)
			imgCache=os.path.join(self.cacheDir,imgName)
			if os.path.exists(imgCache):
				icn=QtGui.QPixmap(imgCache)
			elif img.startswith("http"):
				try:
					raw=requests.get(img)
				except:
					icn2=QtGui.QIcon.fromTheme("preferences-system")
					icn=icn2.pixmap(self.defaultSize,self.defaultSize)
				else:
					icn=QtGui.QPixmap()
					icn.loadFromData(raw.content)
					icn.save(imgCache)
			else:
				icn2=QtGui.QIcon.fromTheme(img)
				icn=icn2.pixmap(self.defaultSize,self.defaultSize)
		else:
			icn2=QtGui.QIcon.fromTheme("preferences-system")
			icn=icn2.pixmap(self.defaultSize,self.defaultSize)
		wsize=self.defaultSize
		if icn:
			w=icn.width()
			h=icn.height()
			wsize=(w*self.defaultSize)/h
			self.icon.setPixmap(icn.scaled(wsize,self.defaultSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
		self.icon.setFixedSize(QSize(wsize,self.defaultSize))
		self.setIconSize(QSize(wsize,self.defaultSize))
		w=self.icon.size().width()+self.label.sizeHint().width()
		if self.overlay==False:
			h=max(self.icon.size().height()+self.label.sizeHint().height(),self.lblDesc.sizeHint().height()+20+self.label.sizeHint().height()*2)
		else:
			h=self.icon.size().height()
		self.setMinimumSize(QSize(w,h))
		self.label.setMinimumWidth(self.width()/1.1)
	#def loadImg

	def setIcon(self,icon):
		if isinstance(icon,QtGui.QIcon):
			self.icon.setPixmap(icon.pixmap(self.defaultSize,self.defaultSize))
			self.icon.setFixedSize(QSize(self.defaultSize,self.defaultSize))
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
	#def setText(self,text)

	def description(self):
		return(self.lblDesc.text())
	#def description

	def setDescription(self,text):
		self.lblDesc.setText(text)
		self.setAccessibleDescription(text)
	#def setDescription(self,text):

	def setTooltipText(self,text):
		self.setToolTip("{0}".format(text))
	#def setTooltipText(self,text):
	
	def activate(self):
		self.clicked.emit()
	#def activate

	def keyPressEvent(self,ev):
		if ev.key() in [Qt.Key_Return,Qt.Key_Enter,Qt.Key_Space]:
			self.clicked.emit()
		ev.ignore()
	#def keyPressEvent(self,ev):

	def enterEvent(self,*args):
		if self.overlay==True:
			self.lblDesc.show()
	#def _enterEvent

	def leaveEvent(self,*args):
		if self.overlay==True:
			self.lblDesc.hide()
	#def _leaveEvent

	def setCacheDir(self,path):
		if os.path.exists(path)==False:
			try:
				os.makedirs(path)
				self.cacheDir=path
			except:
				print("Error using {}".format(path))
		else:
			self.cacheDir=path
	#def setCacheDir


#	def mousePressEvent(self,*args):
#		self.clicked.emit(self)
#	#def mousePressEvent

#class QPushButtonRebostApp
