#### FROM FlowLayout QT EXAMPLES ####

from PySide6.QtWidgets import QScroller,QScrollerProperties,QWidget,QAbstractItemView,QLayout,QLabel,QSizePolicy,QScrollArea
from PySide6.QtCore import Qt,QSize,QRect,QPoint,QEvent,Property,Signal
import PySide6
import time

class _layout(QLayout):
	currentItemChanged=Signal("PyObject","PyObject")
	def __init__(self, parent=None,fastMode=False):
		super().__init__(parent)
		self._previousItem=None
		self._currentItem=None
		self._currentIndex=-1
		self._itemList = []
		self._widgetList = []
		self._cache={}
		self.oldRect=QRect(0,0,0,0)
		self.prevItem=None
		if parent is not None:
			self.setContentsMargins(0, 0, 0, 0)
		self.fastMode=fastMode
	#def __init__

	def __del__(self):
		try:
			item = self.takeAt(0)
			while item:
				item = self.takeAt(0)
		except Exception as e:
			print(e)
	#def __del__

	def currentItem(self):
		return(self._currentItem)
	#def currentItem

	def previousItem(self):
		return(self._previousItem)
	#def previousItem

	def setCurrentItem(self,item,force=False):
		if item!=self._currentItem and force==True:
			self._previousItem=self._currentItem
		self._currentItem=item
		self._currentItem.setFocus()
		self._currentIndex=self.indexOf(self._currentItem)
		self.currentItemChanged.emit(self._previousItem,self._currentItem)
	#def setCurrentItem

	def addItem(self, item):
		if item!=None:
			self._itemList.append(item)
			self._widgetList.append(item.widget())
			item.widget().installEventFilter(self)
	#def addItem

	def eventFilter(self,*args,**kwargs):
		events=[QEvent.Type.Enter,QEvent.Type.FocusIn]
		if (args[1].type() in events) and args[0]!=None:
			force=False
			if args[1].type()==QEvent.Type.Enter:
				force=True
			self.setCurrentItem(args[0],force)
		return(False)
	#def eventFilter

	def count(self):
		return len(self._itemList)+len(self._cache)
	#def count

	def currentIndex(self):
		return(self._currentIndex)
	#def currentIndex

	def indexOf(self,item):
		try:
			if item in self._cache.keys():
				idx=list(self._cache.keys()).index(item)
			elif item in self._itemList:
				idx=self._itemList.index(item)
			elif item in self._widgetList: 
				idx=self._widgetList.index(item)
			else:
				idx=-1
				for cItem,cWdg in self._cache.items():
					if cWdg==item:
						idx=list(self._cache.keys()).index(cItem)
		except Exception as e:
			print(e)
		return(idx)
	#def indexOf

	def itemAt(self, index):
		try:
			if 0 <= index < len(self._cache):
				return list(self._cache.keys())[index]
			else:
				index=index-len(self._cache)
				if 0 <= index < len(self._itemList):
					return self._itemList[index]
		except Exception as e:
			print(e)
		return None
	#def itemAt

	def takeAt(self, index):
		try:
			if 0 <= index < len(self._cache):
				item=list(self._cache.keys())[index]
				self._cache.pop(item)
				return(item)
			else:
				index=index-len(self._cache.keys())
				if 0 <= index < len(self._itemList):
					self._widgetList.pop(index)
					return self._itemList.pop(index)
		except Exception as e:
			print(e)
		return None
	#def takeAt

	def expandingDirections(self):
		return Qt.Orientation(0)
	#def expandingDirections

	def hasHeightForWidth(self):
		return True
	#def hasHeightForWidth

	def heightForWidth(self, width):
		height = self.doLayout(QRect(0, 0, width, 0), True)
		return height
	#def heightForWidth

	def setGeometry(self, rect):
		super(_layout, self).setGeometry(rect)
		self.doLayout(rect, False)
	#def setGeometry

	def sizeHint(self):
		return self.minimumSize()
	#def sizeHint

	def minimumSize(self):
		size = QSize()
		for item in self._itemList:
			size = size.expandedTo(item.minimumSize())
		size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
		return size
	#def minimumSize

	def _doLayoutFast(self, rect):
		x = rect.x()
		y = rect.y()
		spacing = self.spacing()
		itemList=self._itemList
		try:
			if len(itemList)>0:
				item=itemList[-1]
				#if item.widget()!=self.prevItem:
				if item.widget()==None:
					self._itemList.remove(item)
					self._widgetList.remove(item.widget())
				else:
					prevItem=None
					if len(itemList)>1:
						prevItem=itemList[-2].widget()
						while len(self._itemList)>2:
							self._cache.update({self._itemList.pop(0):self._widgetList.pop(0)})
					if prevItem!=None:
						x = prevItem.x()+item.sizeHint().width()
						y = prevItem.y()
						x+=spacing
					if x>rect.right():
						x=0
						y = item.sizeHint().height()+y
						y+=spacing
					item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
		except Exception as e:
				print(e)
		return (y-rect.y())
	#def _doLayoutFast

	def _doLayout(self, rect, test_only):
		x = rect.x()
		y = rect.y()
		line_height = 0
		spacing = self.spacing()
		itemList=self._itemList
		for item in itemList:
			if item.widget()==None:
				self._itemList.remove(item)
				continue
			style = item.widget().style()
			layout_spacing_x = style.layoutSpacing(
				QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
				Qt.Orientation.Horizontal
			)
			layout_spacing_y = style.layoutSpacing(
				QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
				Qt.Orientation.Vertical
			)
			space_x = spacing + layout_spacing_x
			space_y = spacing + layout_spacing_y
			next_x = x + item.sizeHint().width() + space_x
			if next_x - space_x > rect.right() and line_height > 0:
				x = rect.x()
				y = y + line_height + space_y
				next_x = x + item.sizeHint().width() + space_x
				line_height = 0

			if not test_only:
				item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

			x = next_x
			line_height = max(line_height, item.sizeHint().height())

		return y + line_height - rect.y()
	#def _doLayout
	
	def doLayout(self, rect, test):
		if self.fastMode==True:
		   return(self._doLayoutFast(rect))
		else:
		   return(self._doLayout(rect,test))
	#def doLayout
#class _layout

class QFlowTouchWidget(QScrollArea):
	def __init__(self, parent=None,fastMode=False):
		super().__init__(parent)
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.content = QWidget(self)
		self.setWidget(self.content)
		self.flowLayout=_layout(self.content,fastMode)
		self.cleaning=False

	#def __init__

	def addWidget(self, item):
		if self.cleaning==True:
			return
		self.flowLayout.addWidget(item)
	#def addWidget
	
	def addItem(self, item):
		if self.cleaning==True:
			return
		self.flowLayout.addItem(item)
	#def addItem

	def count(self):
		return(self.flowLayout.count())
	#def count

	def currentItem(self):
		return self.flowLayout.currentItem()
	#def currentIndex

	def previousItem(self):
		return self.flowLayout.previousItem()
	#def currentIndex

	def currentIndex(self):
		return self.flowLayout.currentIndex()
	#def currentIndex

	def itemAt(self, index):
		return self.flowLayout.itemAt(index)
	#def itemAt

	def takeAt(self, index):
		return(self.flowLayout.takeAt(index))
	#def takeAt

	def expandingDirections(self):
		return self.flowLayout.expandingDirections
	#def expandingDirections

	def hasHeightForWidth(self):
		return True
	#def hasHeightForWidth

	def heightForWidth(self, width):
		return(self.flowLayout.heightForWidth(width))
	#def heightForWidth

	def setGeometry(self, rect):
		self.setGeometry(rect)
	#def setGeometry

	def sizeHint(self):
		return(self.flowLayout.sizeHint())
	#def sizeHint

	def minimumSize(self):
		return(self.flowLayout.minimumSize())
	#def minimumSize

	def clean(self):
		self.cleaning=True
		wdg=QWidget()
		wdg.setLayout(self.content.layout())
		wdg.deleteLater()
		self.flowLayout=_layout(self.content)
		self.cleaning=False
	#def clean
#class QFlowTouchWidget

if __name__=="__main__":
	obj=QFlowTouchWidget()

