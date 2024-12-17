#!/usr/bin/python3
from . import QCheckableComboBox as _QCheckableComboBox
from . import QHotkeyButton as _QHotkeyButton
from . import QInfoLabel as _QInfoLabel
from . import QPushInfoButton as _QPushInfoButton
from . import QScreenShotContainer as _QScreenShotContainer
from . import QScrollLabel as _QScrollLabel
from . import QSearchBox as _QSearchBox
from . import QStackedWindow as _QStackedWindow
from . import QStackedWindowItem as _QStackedWindowItem
from . import QTableTouchWidget as _QTableTouchWidget
from . import QKdeConfigScreen as _QKdeConfigScreen

class QCheckableComboBox(_QCheckableComboBox.QCheckableComboBox):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QHotkeyButton(_QHotkeyButton.QHotkeyButton):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QInfoLabel(_QInfoLabel.QInfoLabel):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QPushInfoButton(_QPushInfoButton.QPushInfoButton):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QScrollLabel(_QScrollLabel.QScrollLabel):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QScreenShotContainer(_QScreenShotContainer.QScreenShotContainer):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QSearchBox(_QSearchBox.QSearchBox):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QStackedWindow(_QStackedWindow.QStackedWindow):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QStackedWindowItem(_QStackedWindowItem.QStackedWindowItem):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QTableTouchWidget(_QTableTouchWidget.QTableTouchWidget):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

class QKdeconfigScreen(_QKdeConfigScreen.QKdeConfigScreen):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

