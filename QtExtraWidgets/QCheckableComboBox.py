from PySide6.QtWidgets import QComboBox,QSizePolicy,QWidget
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import Qt,Signal

class QCheckableComboBox(QComboBox):
	clicked=Signal()
	closed=Signal()
	def __init__(self,*args,**kwargs):
		parent = kwargs.get('parent')
		if not parent:
			for i in args:
				if isinstance(i,QWidget):
					parent = i
		super().__init__(*args,**kwargs)
		self.view().pressed.connect(self._checked)
		self.view().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred)
		self.setSizeAdjustPolicy(self.SizeAdjustPolicy.AdjustToContents)
		self.setModel(QStandardItemModel(self))
		self.checked=False
		self.title=True
		self.exclusive=False
		self.addItem("")
	#def __init__

	def enableTitle(self,state):
		self.title=state

	def _checked(self, index):
		self.checked=True
		first=-1
		if self.title==True:
			first=0
		if index.row()==first:
			return
		if self.exclusive==True:
			for i in range(0,self.count()):
				item = self.model().item(i)
				item.setCheckState(Qt.Unchecked)
		item = self.model().itemFromIndex(index)
		if item.checkState() == Qt.Checked:
			item.setCheckState(Qt.Unchecked)
		else:
			item.setCheckState(Qt.Checked)
		self.clicked.emit()
		return(False)
	#def _checked

	def setText(self,text):
		if self.count()==0:
			self.addItem("")
		item=self.model().item(0)
		item.setText(text)
	#def setText

	def hidePopup(self,*args,close=False):
		self.setCurrentIndex(0)
		if close==False and self.checked==True:
			self.checked=False
			self.closed.emit()
			return close
		super().hidePopup()
	#def hidePopup

	def addItem(self,*args,state=True):
		super().addItem(args[0])
		item=self.model().item(self.count()-1)
		first=0
		if self.title==True:
			first=1
		if self.count()>first:
			if state==True:
				item.setCheckState(Qt.Checked)
			else:
				item.setCheckState(Qt.Unchecked)
		self.setMinimumWidth(self.view().sizeHint().width())
	#	rect=self.view().sizeHint()
	#	Xpos=0
	#	Ypos=rect.height()
	#	self.btn.move(Xpos,Ypos)
	#def addItem

	def getItems(self,*args):
		items=[]
		i=0
		mitem=self.model().item(i)
		while mitem:
			if mitem in items:
				break
			items.append(mitem)
			i+=1
			#print("QCheckablecomboBox: {}".format(i))
			mitem=self.model().item(i)
		return(items)
	#def getItems

	def setState(self,idx,state):
		item=self.model().item(idx)
		if state==True:
			item.setCheckState(Qt.Checked)
		else:
			item.setCheckState(Qt.Unchecked)
	#def setState
#class QCheckableComboBox
