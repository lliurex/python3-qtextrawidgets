from PySide6.QtWidgets import QWidget, QPushButton,QScrollArea,QLabel,QHBoxLayout,QDialog,QAbstractItemView,QGridLayout,QTableWidgetItem
from PySide6 import QtGui
from PySide6.QtCore import Qt,Signal,QEvent,QThread,QSize
from QtExtraWidgets import QTableTouchWidget
import os,requests
from functools import partial

class _loadScreenShot(QThread):
	imageReady=Signal("PyObject")
	def __init__(self,*args):
		super().__init__()
		self.img=args[0]
		self.cacheDir=None
		self.dbg=False
		if len(args)>1:
			self.setCacheDir(args[1])
		self.destroyed.connect(partial(self._clean,self.__dict__))
	#def __init__

	def _debug(self,msg):
		if self.dbg==True:
			print("{}".format(msg))
	#def _debug

	@staticmethod
	def _clean(*args):
		pass
	#def _clean
	
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
			pxm=icn.pixmap(512,512)
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
				if ("://") in self.img:
					img=requests.get(self.img,timeout=2)
					pxm.loadFromData(img.content)
					gotImg=True
				else:
					icn=QtGui.QIcon.fromTheme("image-x-generic")
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
		self.imageReady.emit(pxm)
		return True
	#def run
#class _loadScreenShot

class QScreenShotContainer(QWidget):
	def __init__(self,parent=None):
		QWidget.__init__(self, parent)
		self.widget=QWidget()
		self.lay=QHBoxLayout()
		self.outLay=QHBoxLayout()
		self.scroll=QScrollArea()
		self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.widget)
		self.outLay.addWidget(self.scroll)
		self.setLayout(self.outLay)
		self.widget.setLayout(self.lay)
		self.cacheDir=None
		self.th=[]
		self.btnImg={}
		self.destroyed.connect(partial(QScreenShotContainer._cleanThreads,self.__dict__))
	#def __init__

	def setCacheDir(self,cacheDir):
		if os.path.exists(cacheDir)==False:
			try:
				os.makedirs(cacheDir)
			except Exception as e:
				print("mdkdir {0} failed: {1}".format(cacheDir,e))
		if os.path.isdir(cacheDir)==True:
			self.cacheDir=cacheDir
	#def setCacheDir

	def eventFilter(self,source,qevent):
		if isinstance(qevent,QEvent):
			if qevent.type()==QEvent.Type.MouseButtonPress:
				self._carrousel(source)
		return(False)
	#def eventFilter

	def _initWidget(self):
		widget=QTableTouchWidget.QTableTouchWidget()
		widget.setRowCount(1)
		widget.setShowGrid(False)
		widget.verticalHeader().hide()
		widget.horizontalHeader().hide()
		widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		widget.setRowCount(1)
		return(widget)
	#def _initWidget(self):

	def _addImgToWidget(self,img,xSize,ySize):
		self.widget.setColumnCount(self.widget.columnCount()+1)
		container=QWidget()
		lay=QHBoxLayout()
		container.setLayout(lay)
		container.setFixedSize(QSize(xSize,ySize))
		lay.addStretch()
		lay.addWidget(img)
		lay.addStretch()
		self.widget.setCellWidget(0,self.widget.columnCount()-1,container)
		self.widget.setItem(0,self.widget.columnCount()-1,QTableWidgetItem())
		self.widget.setColumnWidth(self.widget.columnCount()-1,xSize)
		self.widget.setRowHeight(self.widget.rowCount()-1,ySize)
	#def _addImgToWidget

	def _carrousel(self,btn="",w=0,h=0):
		dlg=QDialog()	
		dlg.setModal(True)
		#if (w==0) or (h==0):
		#	#sizeObject = QDesktopWidget().screenGeometry(-1) #PySide6
		#	qscr=QtGui.QScreen()
		#	sizeObject = qscr.size() #PySide6
		#	print(sizeObject)
		#	w=int(sizeObject.width()/2)
		#	h=int(sizeObject.height()/2)
		#Workaround for size. Set size between 512<>980
		xSize=512
		maxWidth=980
		ySize=512
		sizes=[]
		self.widget=self._initWidget()
		mainLay=QGridLayout()
		mainLay.setHorizontalSpacing(0)
		selectedImg=""
		arrayImg=[]
		for btnImg,img in self.btnImg.items():
			if isinstance(btnImg,QPushButton)==False:
				continue
			sizes.append(img.size().width())
			lbl=QLabel()
			lbl.setPixmap(img.scaled(xSize,ySize,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
			if btnImg==btn:	
				selectedImg=lbl
			else:
				arrayImg.append(lbl)
		sizes.sort()
		for size in sizes:
			if size>xSize:
				if size<=maxWidth:
					xSize=size
					ySize=(size*ySize)/xSize
		if selectedImg:
			self._addImgToWidget(selectedImg,xSize,ySize)
		for lbl in arrayImg:
			self._addImgToWidget(lbl,xSize,ySize)

		icn=QtGui.QIcon.fromTheme("window-close")
		btnClose=QPushButton()
		btnClose.setIcon(icn)
		btnClose.setIconSize(QSize(24,24))
		icn=QtGui.QIcon.fromTheme("go-previous")
		btnPrev=QPushButton()
		btnPrev.setIcon(icn)
		btnPrev.setIconSize(QSize(24,24))
		icn=QtGui.QIcon.fromTheme("go-next")
		btnNext=QPushButton()
		btnNext.setIcon(icn)
		btnNext.setIconSize(QSize(24,24))
		fontSize=btnPrev.font().pointSize()
		btnClose.clicked.connect(dlg.reject)
		btnPrev.clicked.connect(lambda x:self._scrollContainer("left"))
		btnNext.clicked.connect(lambda x:self._scrollContainer("right"))
		mainLay.addWidget(btnPrev,0,0,1,1,Qt.AlignRight)
		mainLay.addWidget(self.widget,0,1,1,1)
		mainLay.addWidget(btnClose,0,2,1,1,Qt.AlignTop|Qt.AlignRight)
		mainLay.addWidget(btnNext,0,2,1,1,Qt.AlignLeft)
		dlg.setLayout(mainLay)
		dlg.setFixedSize(xSize*1.21,ySize*1.1)
		dlg.exec()
	#def carrousel
	
	def _scrollContainer(self,*args):
		if len(args)==0:
			return
		visible = self.widget.itemAt(20, 20)
		column=1
		if visible==None:
			return()
		column=visible.column()
		if args[0]=="left":
			if column<=0:
				column=self.widget.columnCount()
			self.widget.scrollToItem(self.widget.item(visible.row(), column-1))
		elif args[0]=="right":
			if column>=self.widget.columnCount()-1:
				column=-1
			self.widget.scrollToItem(self.widget.item(visible.row(), column+1))
	#def scrollContainer(self,*args):
	
	def addImage(self,img,cacheDir=""):
		if len(cacheDir)==0:
			cacheDir=self.cacheDir
		scr=_loadScreenShot(img,cacheDir)
		scr.imageReady.connect(self._load)
		self.th.append(scr)
		scr.start()
	#def addImage

	def loadScreenShot(self,img,cacheDir=""):
		if len(cacheDir)==0:
			cacheDir=self.cacheDir
		return(_loadScreenShot(img,cacheDir))
	#def loadScreenShot(self,img,cacheDir="")

	def _load(self,*args):
		img=args[0]
		if isinstance(img,QtGui.QPixmap):
			if img.isNull()==False:
				self.btnImg["btn"]=QPushButton()
				self.btnImg[self.btnImg["btn"]]=img
				self.lay.addWidget(self.btnImg["btn"])
				icn=QtGui.QIcon(img)
				self.btnImg["btn"].setIcon(icn)
				self.btnImg["btn"].setIconSize(QSize(128,128))
				self.scroll.setFixedHeight(self.btnImg["btn"].sizeHint().height()+32)
				self.btnImg["btn"].installEventFilter(self)
				self.btnImg["btn"].show()
	#def load

	def clear(self):
		for th in self.th:
			th.quit()
			th.wait()
		for i in reversed(range(self.lay.count())): 
			self.lay.itemAt(i).widget().deleteLater()
		self.btnImg={}
	#def clear

	@staticmethod
	def _cleanThreads(*args):
		selfDict=args[0]
		for th in selfDict.get("th",[]):
			th.quit()
			th.wait()
	#def _cleanThreads
#class QScreenShotContainer
