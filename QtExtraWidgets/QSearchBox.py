from PySide2.QtWidgets import QHBoxLayout,QComboBox,QLineEdit,QPushButton,QWidget,QSizePolicy
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt,Signal,QSize

class QSearchBox(QWidget):
	clicked=Signal()
	editingFinished=Signal()
	returnPressed=Signal()
	textChanged=Signal()
	def __init__(self,*args,**kwargs):
		parent = kwargs.get('parent')
		if not parent:
			for i in args:
				if isinstance(i,QWidget):
					parent = i
		self.history=kwargs.get('history',True)
		super().__init__(*args)
		lay=QHBoxLayout()
		self.setStyleSheet('''QPushButton{margin-left:0px;} QComboBox{margin-right:0px}''')
		lay.setContentsMargins(0, 0, 0, 0)
		lay.setSpacing(0)
		if self.history==True:
			self.cmbSearch=QComboBox()
			self.cmbSearch.setEditable(True)
			self.cmbSearch.currentIndexChanged.connect(self._emitClick)
			self.txtSearch=self.cmbSearch.lineEdit()
			self.txtSearch.setAlignment(Qt.AlignTop)
			lay.addWidget(self.cmbSearch,Qt.Alignment(-1))
		else:
			self.txtSearch=QLineEdit()
			lay.addWidget(self.txtSearch,Qt.Alignment(-1))
		self.txtSearch.setObjectName("search")
		self.txtSearch.setFrame(False)
		self.txtSearch.setTextMargins(0,0,0,0)
		self.txtSearch.editingFinished.connect(self._emitEdit)
		self.txtSearch.returnPressed.connect(self._emitReturn)
		self.txtSearch.textChanged.connect(self._emitChange)
		self.btnSearch=QPushButton()
		icn=QIcon.fromTheme("search")
		self.btnSearch.clicked.connect(self._emitClick)
		self.btnSearch.setIcon(icn)
		self.btnSearch.setIconSize(QSize(24,24))
		if hasattr(self,"cmbSearch"):
			self.cmbSearch.setMinimumHeight(self.btnSearch.sizeHint().height())
		lay.addWidget(self.btnSearch,Qt.AlignLeft|Qt.Alignment(0))
		self.setLayout(lay)
	#def __init__

	def _emitClick(self):
		self.clicked.emit()
	#def _emitClick

	def _emitEdit(self):
		self.editingFinished.emit()
	#def _emitEdit

	def _emitReturn(self):
		self.returnPressed.emit()
	#def _emitEdit

	def _emitChange(self):
		self.textChanged.emit()
	#def _emitEdit

	def text(self):
		return(self.txtSearch.text())
	#def text

	def setText(self,text):
		self.txtSearch.setText(text)
	#def setText

	def setPlaceholderText(self,text):
		self.txtSearch.setPlaceholderText(text)
	#def setPlaceholderText
#class QSearchBox
