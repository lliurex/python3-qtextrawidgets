from PySide6.QtWidgets import QGridLayout,QLabel,QWidget,QPushButton,QCheckBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt,Signal

class QItemDescCheck(QWidget):
	stateChanged=Signal("bool")
	def __init__(self,parent=None):
		QWidget.__init__(self, parent)
		self.file=""
		lay=QGridLayout()
		self.lbltext=QLabel()
		self.lbltext.setStyleSheet("font: bold large;")
		font=self.lbltext.font()
		font.setPointSize(font.pointSize()+2)
		self.lbltext.setFont(font)
		self.name=""
		self.desc=QLabel()
		self.chkState=QCheckBox()
		self.chkState.stateChanged.connect(self.setChanged)
		lay.addWidget(self.lbltext,0,0,1,1,Qt.AlignLeft)
		lay.addWidget(self.desc,1,0,2,1,Qt.AlignLeft)
		lay.addWidget(self.chkState,0,2,1,1,Qt.AlignRight|Qt.AlignCenter)
		lay.setColumnStretch(2,1)
		self.changed=False
		self.setLayout(lay)
		self.md5=""
		parent=self.parent
	#def __init__

	def setChanged(self,changed=True):
		if isinstance(changed,bool)==False:
			changed=True
		self.changed=changed

	def isChecked(self):
		return(self.chkState.isChecked())
	#def isChecked

	def setFile(self,file):
		self.file=file
	#def setFile

	def setText(self,txt):
		self.name=txt
		dsptxt=txt
		if ".list" in txt:
			dsptxt=txt.split(".list")[0]
		self.lbltext.setText("{}".format(dsptxt))
		restricted=["lliurex 23","lliurex mirror","ubuntu jammy"]
		self.lbltext.adjustSize()
	#def setText

	def setDesc(self,txt):
		self.desc.setText("<i>{}</i>".format(txt))
		self.desc.adjustSize()
	#def setDesc

	def setState(self,state):
		self.chkState.setChecked(state)
	#def setState
	
	def setBtnIcn(self,icon):
		pass
	#def setBtnIcn

	def text(self):
		return(self.name)
	#def text
#class QItemDescCheck
