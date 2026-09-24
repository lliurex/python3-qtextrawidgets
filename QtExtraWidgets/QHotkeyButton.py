import os
from PySide2.QtWidgets import QPushButton,QWidget
from PySide2.QtCore import Qt,Signal,QEvent
from PySide2.QtGui import QKeySequence

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
		self.seq=[]
	#def __init__

	def setIconSize(self,*args):
		pass
	#def setIconSize(self,*args):

	def mousePressEvent(self, ev):
		self.originalText=self.text()
		self.setText(self.alternate)
		self.processed=False
		self.seq=[]
		self._grab_alt_keys()
	#def mousePressEvent

	def eventFilter(self,source,event):
		if (event.type()==QEvent.KeyPress):
			if event.key() not in self.seq:
				self.seq.append(event.key())
		if (event.type()==QEvent.KeyRelease):
			self.releaseKeyboard()
			if len(self.seq)>2:
				seq=QKeySequence(self.seq[0],self.seq[1],self.seq[2])
			elif len(self.seq)>1:
				seq=QKeySequence(self.seq[0],self.seq[1])
			else:
				self.seq=[]
				return(False)
			if seq.toString() in self.keymap.values():
				self.seq=[]
				return(False)
			self.keybind_signal.emit(seq.toString().replace(", ","+"))
			if self.processed==False:
				action=self.getSettingForHotkey()
				retVal={"hotkey":self.text(),"action":action}
				self.hotkeyAssigned.emit(retVal)
			self.processed=True
			self.seq=[]
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

	def _readKGlobal(self):
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
		return(action)
	#def _readKGlobal
		
	def _readKHotkeys(self):
		hotkey=self.text()
		kfile="khotkeysrc"
		action=""
		sourceFolder=os.path.join(os.environ.get('HOME',"/usr/share/acccessibility"),".config")
		kPath=os.path.join(sourceFolder,kfile)
		with open(kPath,"r") as f:
			lines=f.readlines()
		for line in lines:
			if len(line.split("="))>1:
				if hotkey.lower()==line.split("=")[-1].lower().strip().removeprefix("\n"):
					action=line.split("=")[-1].strip()
					break
		return(action)
	#def _readKHotkeys

	def getSettingForHotkey(self):
		action=self._readKGlobal().strip()
		if action=="":
			action=self._readKHotkeys()
		return(action.replace("\n",""))
	#def getSettingForHotkey

	def revertHotkey(self):
		self.setText(self.originalText)
	#def revertHotkey
#class QHotkeyButton
