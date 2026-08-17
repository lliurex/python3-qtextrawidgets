#!/usr/bin/python3
import sys
import os
from PySide6.QtWidgets import QLabel, QPushButton,QGridLayout,QHBoxLayout,QLabel
from PySide6 import QtGui
from PySide6.QtCore import Qt,Signal,QSize,QThread
from QtExtraWidgets import QTableTouchWidget,QStackedWindowItem,QScrollLabel,QStyledLabel
import requests

ICON_SIZE=128

class _loadImage(QThread):
	imageReady=Signal("PyObject","PyObject")
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.img=kwargs.get("img",None)
		self.cacheDir=None
		self.dbg=True
		if len(args)>1:
			self.setCacheDir(args[1])
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("{}".format(msg))
	#def _debug

	def setCacheDir(self,cacheDir):
		sureDirs=["/tmp/.cache",os.path.join(os.environ.get('HOME',''),".cache")]
		if isinstance(cacheDir,str)==False:
			cacheDir=''
		for sure in sureDirs:
			if sure in cacheDir:
				sureDirs=[]
				break
		if sureDirs:
			return
		if isinstance(cacheDir,str)==False:
			cacheDir=""
		if os.path.exists(cacheDir)==False:
			try:
				os.makedirs(cacheDir)
			except Exception as e:
				print("mdkdir {0} failed: {1}".format(cacheDir,e))
		if os.path.isdir(cacheDir)==True:
			self.cacheDir=cacheDir
		self._debug("Cache set to {}".format(self.cacheDir))
	#def setCacheDir

	def setImg(self,img):
		self.img=img
	#def setImg

	def run(self,*args):
		gotImg=False
		pxm=None
		stripName=""
		if isinstance(self.img,QtGui.QPixmap):
			pxm=self.img
			gotImg=True
		elif isinstance(self.img,str):
			#Only alnum
			stripName=''.join(ch for ch in os.path.basename(self.img) if ch.isalnum())
			MAX=96
			if (len(stripName)>MAX):
				stripName=os.path.basename(stripName[len(stripName)-MAX:])
			icn=QtGui.QIcon.fromTheme("image-x-generic")
			if stripName.endswith("png"):
				stripName=stripName.replace("png",".png")
			fPath=""
			if os.path.exists(self.img):
				pxm=QtGui.QPixmap()
				try:
					pxm.load(self.img)
					gotImg=True
				except Exception as e:
					print("Loading cache pixmap: {}".format(e))
		if self.cacheDir and gotImg==False:
			fPath=os.path.join(self.cacheDir,stripName)#self.img.split('/')[-1])
			if os.path.isfile(fPath)==True:
				pxm=QtGui.QPixmap()
				try:
					pxm.load(fPath)
					gotImg=True
				except Exception as e:
					print("Loading cache pixmap: {}".format(e))
		if gotImg==False and self.img!="":
			try:
				pxm=QtGui.QPixmap()
				if ("://") in self.img:
					img=requests.get(self.img,timeout=5)
					pxm.loadFromData(img.content)
					gotImg=True
				else:
					icn=QtGui.QIcon.fromTheme(os.path.basename(self.img))
					pxm=icn.pixmap(512,512)
					gotImg=True
			except Exception as e:
				gotImg=False
				print("Screenshot request: {}".format(e))
		if gotImg==True and isinstance(self.img,str): #Save the img
			if self.cacheDir:
				if fPath=="":
					fPath=os.path.join(self.cacheDir,stripName)
				if not os.path.exists(fPath):
					pxm=pxm.scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
					pxm.save(fPath,"PNG")#,quality=5)
		elif pxm==None:
			#Load generic pixmap
			icn=QtGui.QIcon.fromTheme("image-x-generic")
			pxm=icn.pixmap(256,256)
		self.imageReady.emit(pxm,self.img)
		return True
	#def run
#class _loadScreenShot

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
		self.thImg=_loadImage()
		self.thImg.imageReady.connect(self._loadImg)
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
			lay.addWidget(self.icon,0,1,2,2,Qt.AlignRight|Qt.AlignTop)
			lay.addWidget(QLabel("<hr>"),1,1,1,3,Qt.AlignRight|Qt.AlignTop)
			lay.addWidget(self.lblDesc,2,0,1,3)
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

	def _loadImg(self,*args):
		img=args[0]
		wsize=self.defaultSize
		if img:
			w=img.width()
			h=img.height()
			wsize=(w*self.defaultSize)/h
			self.icon.setPixmap(img.scaled(wsize,self.defaultSize,Qt.KeepAspectRatio,Qt.SmoothTransformation))
		self.icon.setFixedSize(QSize(wsize,self.defaultSize))
		self.setIconSize(QSize(wsize,self.defaultSize))
		w=self.icon.size().width()+self.label.sizeHint().width()
		if self.overlay==False:
			h=max(self.icon.size().height()+self.label.sizeHint().height(),self.lblDesc.sizeHint().height()+20+self.label.sizeHint().height()*2)
		else:
			h=self.icon.size().height()
		self.label.setMaximumSize(QSize(w,h))

	def loadImg(self,img):
		if self.overlay==False:
			h=max(self.icon.size().height()+self.label.sizeHint().height(),self.lblDesc.sizeHint().height()+20+self.label.sizeHint().height()*2)
		else:
			h=self.icon.size().height()
		self.setMinimumHeight(self.defaultSize)
		#self.label.setMinimumWidth(self.width()/1.1)
		self.thImg.setImg(img)
		self.thImg.start()
		return
	
	def loadImgSync(self,img):
		if img==None:
			img=""
		if os.path.exists(img):
			icn=QtGui.QPixmap(img)
		elif img!='':
			imgName=os.path.basename(img)
			imgName=imgName.replace("=","").replace("&","").replace("?","").replace(".php","")
			if imgName.count(".")==0:
				imgName+=".png"
			imgCache=os.path.join(self.cacheDir,imgName).replace("=","-").replace("&",".").replace("?","_")
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
	#def loadImgSync

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
		self.thImg.setCacheDir(self.cacheDir)
	#def setCacheDir


#	def mousePressEvent(self,*args):
#		self.clicked.emit(self)
#	#def mousePressEvent

#class QPushButtonRebostApp
