#!/usr/bin/python3
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QLinearGradient, QColor

class QStyledLabel(QLabel):
	def __init__(self, text="", parent=None):
		super().__init__(text, parent)
		self.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.setStyleSheet("color: rgb(10,20,25);padding:5px")
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Transparent background
		self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent,False)
		self.setAutoFillBackground(True)
		self.colorFrom=QColor(224, 214, 255,50)
		self.colorTo=QColor(128, 100, 228,220)
		self.x1=1.2
		self.x2=1.1
	#def __init__(self, text="", parent=None):

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		gradient = QLinearGradient(self.width()/self.x1, 0, self.width()/self.x2, self.height())
		gradient.setColorAt(0, self.colorFrom)  # Blue
		gradient.setColorAt(1, self.colorTo)  # Purple
		painter.fillRect(self.rect(), gradient)
		super().paintEvent(event)
		painter.end()
	#def paintEvent

	def setGradient(self,colorF,colorT):
		if isinstance(colorF,QColor):
			self.colorFrom=colorF
		else:
			self.colorFrom=QColor(colorF[0],colorF[1],colorF[2],colorF[3])
		if isinstance(colorT,QColor):
			self.colorTo=colorT
		else:
			self.colorTo=QColor(colorT[0],colorT[1],colorT[2],colorT[3])
	#def setGradient

	def setForeground(self,color):
		self.setStyleSheet("color: rgb(%s,%s,%s);padding:5px"%(color[0],color[1],color[2]))
