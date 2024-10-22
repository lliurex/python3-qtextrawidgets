import os
from PySide6.QtWidgets import QPushButton,QWidget
from PySide6.QtCore import Qt,Signal,QEvent
from PySide6.QtGui import QKeySequence

class QHotkeyButton(QPushButton):
	keybind_signal=Signal("PyObject")
	hotkeyAssigned=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		text=""
		parent = kwargs.get('parent')
		if not parent:
			for i in args:
				if isinstance(i,QWidget):
					parent = i
				if isinstance(i,str):
					text=i
		super().__init__(*args)
		text = kwargs.get('text',text)
		self.alternate=kwargs.get('alternate',"")
		self.installEventFilter(self)
		self.keymap={}
#		for key,value in vars(Qt).items():
#			if key=="Key":
#				print(value)
#				self.keymap[value]=key.partition('_')[2]
#		print("****")
#		print(self.keymap)
#		print("****")
		self.keymap={
					Qt.KeyboardModifier.ControlModifier: "Control",
					Qt.KeyboardModifier.AltModifier: "Alt",
					Qt.KeyboardModifier.ShiftModifier: "Shift",
					Qt.KeyboardModifier.MetaModifier: "Meta",
					Qt.KeyboardModifier.GroupSwitchModifier: "AltGr",
					Qt.KeyboardModifier.KeypadModifier: "NumLock"
					}
		self.processed=False
		self.setText(text)
		self.originalText=text
		self.setAttribute(Qt.WA_KeyCompression,False)
		self.sw_mod=False
		self.keypressed=0
		self.seq=[]
	#def __init__

	def setIconSize(self,*args):
		pass
	#def setIconSize(self,*args):

	def mousePressEvent(self, ev):
		self.originalText=self.text()
		self.setText(self.alternate)
		self.processed=False
		self._grab_alt_keys()
	#def mousePressEvent

	def eventFilter(self,source,event):
		if (event.type()==QEvent.KeyPress):
			if event.key() not in self.seq:
				self.seq.append(event.key())
			self.keypressed=len(self.seq)
		if (event.type()==QEvent.KeyRelease):
			self.keypressed-=1
			if self.keypressed>0:
				return(False)
			if len(self.seq)>2:
				seq=QKeySequence(self.seq[0],self.seq[1],self.seq[2])
			elif len(self.seq)>1:
				seq=QKeySequence(self.seq[0],self.seq[1])
			else:
				seq=QKeySequence(self.seq[0])
			if seq.toString() in self.keymap.values():
				self.seq=[]
				self.releaseKeyboard()
				return(False)
			self.keybind_signal.emit(seq.toString().replace(", ","+"))
			self.releaseKeyboard()
			self.seq=[]
			if self.processed==False:
				action=self.getSettingForHotkey()
				retVal={"hotkey":self.text(),"action":action}
				self.hotkeyAssigned.emit(retVal)
			self.processed=True

		return False
	#def eventFilter

	def _grab_alt_keys(self,*args):
		self.keybind_signal.connect(self._set_config_key)
		self.grabKeyboard()
	#def _grab_alt_keys

	def _set_config_key(self,keypress):
		keypress=keypress.replace("Control","Ctrl")
		self.setText(keypress)
	#def _set_config_key

	def getSettingForHotkey(self):
		hotkey=self.text()
		kfile="kglobalshortcutsrc"
		action=""
		sourceFolder=os.path.join(os.environ.get('HOME',"/usr/share/acccessibility"),".config")
		kPath=os.path.join(sourceFolder,kfile)
		with open(kPath,"r") as f:
			lines=f.readlines()
		for line in lines:
			if len(line.split(","))>2:
				if hotkey.lower()==line.split(",")[-2].lower():
					action=line.split(",")[-1]
					break
				elif line.startswith("_launch"):
					if hotkey.lower()==line.replace("_launch=","").split(",")[0].lower():
						action=line.split(",")[-1]
						break
		return(action.replace("\n",""))
	#def getSettingForHotkey

	def revertHotkey(self):
		self.setText(self.originalText)
	#def revertHotkey
#class QHotkeyButton
