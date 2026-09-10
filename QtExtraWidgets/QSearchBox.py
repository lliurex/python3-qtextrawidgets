from PySide6.QtWidgets import QHBoxLayout,QComboBox,QLineEdit,QPushButton,QWidget,QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt,Signal,QSize

class QSearchBox(QWidget):
	clicked=Signal(str)
	editingFinished=Signal(str)
	returnPressed=Signal(str)
	textChanged=Signal(str)
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
		else:
			self.txtSearch=QLineEdit()
		self.btnSearch=QPushButton()
		icn=QIcon.fromTheme("search")
		self.btnSearch.clicked.connect(self._emitClick)
		self.btnSearch.setIcon(icn)
		self.btnSearch.setIconSize(QSize(24,24))
		if hasattr(self,"cmbSearch"):
			self.cmbSearch.setMinimumHeight(self.btnSearch.sizeHint().height())
			self.cmbSearch.setEditable(True)
			self.cmbSearch.currentIndexChanged.connect(self._emitClick)
			self.txtSearch=self.cmbSearch.lineEdit()
			self.txtSearch.setFrame(False)
			self.txtSearch.setAlignment(Qt.AlignTop)
			lay.addWidget(self.cmbSearch,Qt.Alignment(-1))
			lay.addWidget(self.btnSearch,Qt.AlignLeft|Qt.Alignment(0))
		else:
			lay.addWidget(self.txtSearch,Qt.Alignment(1))
			self.txtSearch.returnPressed.connect(self._emitReturn)
		self.txtSearch.setObjectName("search")
		self.txtSearch.setTextMargins(0,0,0,0)
		self.txtSearch.editingFinished.connect(self._emitEdit)
		self.txtSearch.textChanged.connect(self._emitChange)
		self.setLayout(lay)
	#def __init__

	def _emitClick(self):
		self.clicked.emit(self.txtSearch.text())
	#def _emitClick

	def _emitEdit(self):
		self.editingFinished.emit(self.txtSearch.text())
	#def _emitEdit

	def _emitReturn(self):
		self.returnPressed.emit(self.txtSearch.text())
	#def _emitEdit

	def _emitChange(self):
		self.textChanged.emit(self.txtSearch.text())
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
