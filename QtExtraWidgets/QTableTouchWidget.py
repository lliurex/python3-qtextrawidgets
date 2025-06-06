from PySide6.QtWidgets import QScroller,QScrollerProperties,QTableWidget,QWidget,QAbstractItemView
import PySide6

class QTableTouchWidget(QTableWidget):
	def __init__(self,*args,**kwargs):
		parent = kwargs.get('parent')
		if not parent:
			for i in args:
				if isinstance(i,QWidget):
					parent = i
		super().__init__(*args,**kwargs)
#		self.scroller=QScroller()
		self.scroller=QScroller.grabGesture(self.viewport(),QScroller.LeftMouseButtonGesture)
		self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
#		sp=self.scroller.scrollerProperties()
#		sp.setScrollMetric(QScrollerProperties.DragVelocitySmoothingFactor,0.6)
#		sp.setScrollMetric(QScrollerProperties.MinimumVelocity,0.0)
#		sp.setScrollMetric(QScrollerProperties.MaximumVelocity,0.5)
#		sp.setScrollMetric(QScrollerProperties.AcceleratingFlickMaximumTime,0.4)
#		sp.setScrollMetric(QScrollerProperties.AcceleratingFlickSpeedupFactor,1.2)
#		sp.setScrollMetric(QScrollerProperties.SnapPositionRatio,0.2)
#		sp.setScrollMetric(QScrollerProperties.MaximumClickThroughVelocity,0)
#		sp.setScrollMetric(QScrollerProperties.DragStartDistance,0.001)
#		sp.setScrollMetric(QScrollerProperties.MousePressEventDelay,0.5)
#		self.scroller.grabGesture(self.viewport(),QScroller.LeftMouseButtonGesture)
	#def __init__
#class QTableTouchWidget

if __name__=="__main__":
	obj=QTableTouchWidget()

