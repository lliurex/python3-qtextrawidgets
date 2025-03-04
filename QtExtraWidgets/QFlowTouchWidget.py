#### FROM FlowLayout QT EXAMPLES ####

from PySide2.QtWidgets import QScroller,QScrollerProperties,QWidget,QAbstractItemView,QLayout,QLabel,QSizePolicy,QScrollArea
from PySide2.QtCore import Qt,QSize,QRect,QPoint
import PySide2

class _layout(QLayout):
	def __init__(self, parent=None):
		super().__init__(parent)
		self._itemList = []
		if parent is not None:
			self.setContentsMargins(0, 0, 0, 0)
	#def __init__

	def __del__(self):
		item = self.takeAt(0)
		while item:
			item = self.takeAt(0)
	#def __del__

	def addItem(self, item):
		self._itemList.append(item)
	#def addItem

	def count(self):
		return len(self._itemList)
	#def count

	def itemAt(self, index):
		if 0 <= index < len(self._itemList):
			return self._itemList[index]
		return None
	#def itemAt

	def takeAt(self, index):
		if 0 <= index < len(self._itemList):
			return self._itemList.pop(index)
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

	def doLayout(self, rect, test_only):
		x = rect.x()
		y = rect.y()
		line_height = 0
		spacing = self.spacing()

		for item in self._itemList:
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
	#def doLayout
#class _layout


class QFlowTouchWidget(QScrollArea):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.content = QWidget(self)
		self.setWidget(self.content)
		self.flowLayout=_layout(self.content)

	def addWidget(self, item):
		self.flowLayout.addWidget(item)

	def addItem(self, item):
		self.flowLayout.addItem(item)

	def count(self):
		return(self.flowLayout.count())

	def itemAt(self, index):
		return self.flowLayout.itemAt(index)

	def takeAt(self, index):
		return(self.flowLayout.takeAt(index))

	def expandingDirections(self):
		return self.flowLayout.expandingDirections

	def hasHeightForWidth(self):
		return True

	def heightForWidth(self, width):
		return(self.flowLayout.heightForWidth(width))

	def setGeometry(self, rect):
		self.setGeometry(rect)

	def sizeHint(self):
		return(self.flowLayout.sizeHint())

	def minimumSize(self):
		return(self.flowLayout.minimumSize())

	def clean(self):
		for idx in reversed(range(0,self.content.layout().count())):
			self.content.layout().itemAt(idx).widget().setParent(None)
#class QFlowTouchWidget

if __name__=="__main__":
	obj=QFlowTouchWidget()

