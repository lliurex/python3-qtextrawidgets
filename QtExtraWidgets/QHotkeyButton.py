import os
from PySide2.QtWidgets import QPushButton,QWidget
from PySide2.QtCore import Qt,Signal,QEvent

class QHotkeyButton(QPushButton):
	keybind_signal=Signal("PyObject")
	hotkeyAssigned=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		parent = kwargs.get('parent')
		if not parent:
			for i in args:
				if isinstance(i,QWidget):
					parent = i
		super().__init__(*args,**kwargs)
		text = kwargs.get('text',"")
		self.installEventFilter(self)
		self.keymap={}
		for key,value in vars(Qt).items():
			if isinstance(value, Qt.Key):
				self.keymap[value]=key.partition('_')[2]
		self.modmap={
					Qt.ControlModifier: self.keymap[Qt.Key_Control],
					Qt.AltModifier: self.keymap[Qt.Key_Alt],
					Qt.ShiftModifier: self.keymap[Qt.Key_Shift],
					Qt.MetaModifier: self.keymap[Qt.Key_Meta],
					Qt.GroupSwitchModifier: self.keymap[Qt.Key_AltGr],
					Qt.KeypadModifier: self.keymap[Qt.Key_NumLock]
					}
		self.processed=False
		self.setText(text)
		self.originalText=text
	#def __init__

	def setIconSize(self,*args):
		pass
	#def setIconSize(self,*args):

	def mousePressEvent(self, ev):
		self.originalText=self.text()
		self.setText("")
		self.processed=False
		self._grab_alt_keys()
	#def mousePressEvent

	def eventFilter(self,source,event):
		sw_mod=False
		keypressed=[]
		if (event.type()==QEvent.KeyPress):
			for modifier,text in self.modmap.items():
				if event.modifiers() & modifier:
					sw_mod=True
					keypressed.append(text)
			key=self.keymap.get(event.key(),event.text())
			if key not in keypressed:
				if sw_mod==True:
					sw_mod=False
				keypressed.append(key)
			if sw_mod==False:
				self.keybind_signal.emit("+".join(keypressed))
		if (event.type()==QEvent.KeyRelease):
			self.releaseKeyboard()
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
