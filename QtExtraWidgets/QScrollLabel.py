from PySide6.QtWidgets import QScrollArea,QVBoxLayout,QLabel,QWidget
from PySide6.QtCore import Qt,Signal

class QScrollLabel(QScrollArea):
	linkActivated=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		parent = kwargs.get('parent')
		text = kwargs.get('text',"")
		if not parent:
			for i in args:
				if isinstance(i,QWidget):
					parent = i
		super().__init__(*args,**kwargs)
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		content = QWidget(self)
		self.setWidget(content)
		lay = QVBoxLayout(content)
		self.label = QLabel(content)
		self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
		self.label.linkActivated.connect(self._emitLink)
		self.label.setWordWrap(True)
		lay.addWidget(self.label)
		self.label.setText(text)
		self.label.adjustSize()
#		self.setFixedWidth(self.label.sizeHint().width())
#		self.setFixedHeight(self.label.sizeHint().height()/2)
	#def __init__

	def text(self):
		return(self.label.text())
	#def text

	def setText(self,text):
		self.label.setText(text)
#		self.setFixedWidth(self.label.sizeHint().width())
#		self.setFixedHeight(self.label.sizeHint().height())
		self.label.adjustSize()
	#def setText

	def setWordWrap(self,boolWrap):
		self.label.setWordWrap(boolWrap)
	#def setWordWrap

	def adjustWidth(self,width):
		if self.width()<width-50:
			self.setFixedWidth(width-50)
	#def adjustWidth

	def adjustHeight(self,height):
		if self.height()<height-50:
			self.setFixedHeight(height-50)
	#def adjustHeight

	def _emitLink(self,*args):
		self.linkActivated.emit(args)
#class QScrollLabel
