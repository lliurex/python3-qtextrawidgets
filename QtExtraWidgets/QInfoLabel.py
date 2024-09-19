from PySide2.QtWidgets import QScrollArea,QGridLayout,QLabel,QWidget,QPushButton
from PySide2.QtGui import QIcon,QColor,QPalette
from PySide2.QtCore import Qt,Signal,QSize,QTimer

#Label for notification purposes

class QInfoLabel(QWidget):
	clicked=Signal()
	def __init__(self,*args,**kwargs):
		parent = kwargs.get('parent')
		self.text = kwargs.get('text',"")
		if not parent:
			for i in args:
				if isinstance(i,QWidget):
					parent = i
		super().__init__(*args,**kwargs)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setObjectName("Frame")
		self.setAutoFillBackground(True)
		self._renderGui()
		self.timer=QTimer()
		self.timer.setSingleShot(True)
		self.timer.timeout.connect(self.hide)
		self._applyCss()
	#def __init__

	def _renderGui(self):
		lay = QGridLayout()
		lay.setContentsMargins(3,3,3,3)
		lblIcn=QLabel()
		icn=QIcon.fromTheme("dialog-information")
		icnSize=24
		lblIcn.setPixmap(icn.pixmap(icnSize,icnSize))
		lblIcn.setMaximumWidth(icnSize)
		lblIcn.setMaximumHeight(icnSize)
		lay.addWidget(lblIcn,0,0,1,1,Qt.Alignment(0))
		self.label = QLabel()
		self.label.setAlignment(Qt.AlignLeft)
		lay.addWidget(self.label,0,1,1,1,Qt.AlignTop)
		self.label.setText(self.text)
		self.label.adjustSize()
		self.btn=QPushButton()
		self.btn.setMaximumWidth(icnSize)
		self.btn.setMaximumHeight(icnSize)
		self.btn.clicked.connect(self.hide)
		self.btn.setFlat(True)
		icn=QIcon.fromTheme("dialog-close")
		self.btn.setIcon(icn)
		self.btn.setIconSize(QSize(icnSize,icnSize))
		lay.addWidget(self.btn,0,2,1,1,Qt.AlignTop)
		self.btnAction=QPushButton("")
		self.btnAction.setVisible(False)
		self.btnAction.clicked.connect(self.emitClick)
		lay.addWidget(self.btnAction,1,1,1,2,Qt.AlignLeft)
		self.setLayout(lay)
	#def _renderGui

	def _applyCss(self):
		bcolor=QColor(QPalette().color(QPalette.Active,QPalette.Highlight))
		color=QColor(QPalette().color(QPalette.Inactive,QPalette.Highlight))
		pal=self.palette()
		rgbColor="{0},{1},{2}".format(color.red(),color.green(),color.blue())
		rgbBcolor="{0},{1},{2}".format(bcolor.red(),bcolor.green(),bcolor.blue())
		self.setStyleSheet("""#Frame {
			background-color: rgb(%s); 
			border-style: solid; 
			border-color: rgb(%s); 
			border-width: 1px; 
			border-radius: 2px;}"""%(rgbColor,rgbBcolor))
	#def _applyCss

	def hide(self):
		self.timer.setInterval(0)
		self.setVisible(False)
	#def hide

	def showEvent(self,*args):
		if self.timer.interval()!=0:
			self.timer.start()
	#def showEvent

	def emitClick(self):
		self.clicked.emit()

	def setTimeout(self,timeout):
		if isinstance(timeout,int):
			if timeout<500:
				timeout=timeout*1000
			self.timer.setInterval(timeout)
	#def setTimeout(self,timeout):

	def setText(self,text):
		self.label.setText(text)
		self.label.adjustSize()
	#def setText

	def setActionText(self,text):
		self.btnAction.setText(text)
		self.btnAction.setVisible(True)
	#def setActionText

	def setActionIcon(self,icon,size=0):
		if isinstance(icon,str)==True:
			icon=QIcon.fromTheme(icon)
		self.btnAction.setIcon(icon)
		if size>0:
			self.btnAction.setIconSize(QSize(size,size))
		self.btnAction.setVisible(True)
	#def setActionIcon

	def setWordWrap(self,boolWrap):
		self.label.setWordWrap(boolWrap)
	#def setWordWrap
#class QInfoLabel
