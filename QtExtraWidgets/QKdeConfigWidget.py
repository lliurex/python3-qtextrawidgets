#!/usr/bin/python3
import os,subprocess
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QTableWidget,QScrollArea,QLabel,QGroupBox
from PySide2.QtCore import QFile, QIODevice
from PySide2.QtGui import QColor
import gettext
_=gettext.gettext

#Widget that loads the configuration file config.ui from a kwin script.
#Uses main configuration from script

class QKdeConfigWidget(QWidget):
	def __init__(self,uiFile,*args,**kwargs):
		parent = kwargs.get('parent')
		if not parent:
			for i in args:
				if isinstance(i,QWidget):
					parent = i
		super().__init__(*args,**kwargs)
		self.plugType="Effect"
		self.wlayout=QGridLayout()
		self.confFile=os.path.join(os.path.dirname(os.path.dirname(uiFile)),"config","main.xml")
		QUiFile = QFile(uiFile)
		if not QUiFile.open(QIODevice.ReadOnly):
			print(f"Cannot open {uiFile}: {QUiFile.errorString()}")
		else:
			self._setTranslationDomain(uiFile)
			self.uiId=self.getId(uiFile)
			loader = QUiLoader()
			window = loader.load(QUiFile)
			QUiFile.close()
			if not window:
				print(loader.errorString())
				sys.exit(-1)
			layout=window.layout()
			self.configWidgets=self._recursiveSetupEvents(layout)
			self.readConfig()
			self._retranslate()
			self.wlayout.addWidget(window)
			if isinstance(window.children()[-1],QLabel):
				window.children()[-1].setVisible(False)
		self.setLayout(self.wlayout)
	#def __init__

	def _retranslate(self):
		for name,wdg in self.configWidgets:
			if hasattr(wdg,"text"):
				i18nText=_(wdg.text())
				if i18nText!=wdg.text():
					wdg.setText(i18nText)
			elif hasattr(wdg,"count"):
				for row in range(0,wdg.count()):
					if hasattr(wdg,"setItemText"):
						wdg.setItemText(row,_(wdg.itemText(row)))
			elif hasattr(wdg,"title"):
				if len(wdg.title())>0:
					title=_(wdg.title())
					wdg.setTitle(title)
	#def _retranslate

	def _getSignalForConnection(self,widget):
		name=widget.objectName()
		if name.startswith("kcfg_"):
			return(name)
		return("")
	#def _getSignalForConnection

	def _recursiveExploreWidgets(self,widget):
		if widget==None:
			return
		name=self._getSignalForConnection(widget)
		if isinstance(widget,QTableWidget):
			for x in range (0,widget.rowCount()):
				for y in range (0,widget.columnCount()):
					tableWidget=widget.cellWidget(x,y)
					self._recursiveExploreWidgets(tableWidget)
		elif isinstance(widget,QScrollArea):
			wdg=widget.widget()
			if wdg:
				self._recursiveExploreWidgets(wdg)
			else:
				lay=widget.layout()
				if lay:
					self._recursiveExploreWidgets(lay)
		else:
			if type(widget) in [QGridLayout,QVBoxLayout,QHBoxLayout]:
				self._recursiveSetupEvents(widget)
			else:
				try:
					if widget.layout():
						self._recursiveSetupEvents(widget.layout())
				except:
					self._recursiveSetupEvents(widget)
		return(name,widget)
	#def _recursiveExploreWidgets

	def _recursiveSetupEvents(self,layout):
		if layout==None:
			return
		configWidgets=[]
		for idx in range(0,layout.count()):
			widget=layout.itemAt(idx).widget()
			if isinstance(widget,QWidget):
				if isinstance(widget,QGroupBox):
					if widget not in configWidgets:
						configWidgets.append(("",widget))
					for rad in widget.children():
						wdg=self._recursiveExploreWidgets(rad)
						if wdg not in configWidgets:
							configWidgets.append(wdg)
				else:
					wdg=self._recursiveExploreWidgets(widget)
				if wdg not in configWidgets:
					configWidgets.append(wdg)
			elif layout.itemAt(idx).layout():
				self._recursiveSetupEvents(layout.itemAt(idx).layout(),block)
		return(configWidgets)
	#def _recursiveSetupEvents

	def readConfig(self):
		if "effect" in self.uiId:
			self.plugType="Effect"
		else:
			self.plugType="Script"
		if len(self.configWidgets)>0:
			for name,wdg in self.configWidgets:
				if len(name)==0:
					continue
				#if hasattr(wdg,"text"):
				key=name.replace("kcfg_","")
				cmd=["kreadconfig5","--file","kwinrc","--group","{0}-{1}".format(self.plugType,self.uiId),"--key",key]
				out=subprocess.check_output(cmd,universal_newlines=True,encoding="utf8")
				value=out.strip()
				if len(value)<=0:
					value=self._getDefaultValue(key)
				if isinstance(wdg,QPushButton):
					hasKcolor=wdg.property("color")
					if hasKcolor!=None:
						kcolor=value.split(",")
						newcolor=QColor.fromRgb(int(kcolor[0]),int(kcolor[1]),int(kcolor[2]))
						wdg.setProperty("color",newcolor)
					wdg.setText(value)
				elif hasattr(wdg,"checkState"):
					state=True
					if value!="true":
						state=False
					wdg.setChecked(state)
				elif hasattr(wdg,"isChecked"):
					state=True
					if value!="true":
						state=False
					wdg.setChecked(state)
				elif hasattr(wdg,"setCurrentIndex") and value.isnumeric():
					wdg.setCurrentIndex(int(value))
				elif hasattr(wdg,"setValue") and value.isnumeric():
					wdg.setValue(int(value))
				elif hasattr(wdg,"setText"):
					wdg.setText(value)
	#def readConfig

	def _getDefaultValue(self,key):
		value=""
		if os.path.exists(self.confFile):
			with open(self.confFile,"r") as f:
				fcontent=f.readlines()
			sw=False
			for fline in fcontent:
				if "entry name=\"{}\"".format(key) in fline:
					sw=True
					continue
				if sw==True:
					value=fline.strip().removeprefix("<default>").removesuffix("</default>")
					break
		return(value)
	#def _getDefaultValue

	def _generateCommand(self,plugType,uiId,key,text):
		cmd=[]
		cmd=["kwriteconfig5","--file","kwinrc","--group","{0}-{1}".format(plugType,uiId),"--key",key,str(text)]
		return(cmd)
	#def _generateCommand

	def saveChanges(self):
		cmd=""
		if "effect" in self.uiId:
			self.plugType="Effect"
		else:
			self.plugType="Script"
		for name,wdg in self.configWidgets:
			if isinstance(wdg,QLabel):
				continue
			if len(name)==0:
				continue
			key=name.replace("kcfg_","")
			hasKcolor=wdg.property("color")
			if hasKcolor!=None:
				color="{0},{1},{2}".format(hasKcolor.red(),hasKcolor.green(),hasKcolor.blue())
				cmd=self._generateCommand(self.plugType,self.uiId,key,color)
			elif hasattr(wdg,"checkState") or hasattr(wdg,"group"):
				state=wdg.isChecked()
				cmd=self._generateCommand(self.plugType,self.uiId,key,str(state).lower())
			elif hasattr(wdg,"currentIndex"):
				cmd=self._generateCommand(self.plugType,self.uiId,key,str(wdg.currentIndex()))
			elif hasattr(wdg,"value"):
				cmd=self._generateCommand(self.plugType,self.uiId,key,str(wdg.value()))
			elif hasattr(wdg,"text"):
				cmd=self._generateCommand(self.plugType,self.uiId,key,str(wdg.text()))
			if len(cmd)>0:
				subprocess.run(cmd)
	#def saveChanges

	def getId(self,UiFile):
		#search for a metadata file
		end=False
		path=UiFile
		uiId=""
		while end==False:
			path=os.path.dirname(path)
			for f in os.scandir(path):
				if f.name.startswith("metadata")==True:
					end=True
					path=f.path
			if path.count("/")<=2:
				end=True
		if path.endswith("json") or path.endswith("desktop"):
			with open(path,"r") as f:
				fcontent=f.readlines()
			for l in fcontent:
				if l.replace(" ","").startswith("\"Id\""):
					uiId=l.split(":")[-1]
					uiId=uiId.replace(" ","").replace("\"","").replace(",","").strip()
		return(uiId)
	#def getId

	def _setTranslationDomain(self,UiFile):
		path=UiFile
		end=False
		domain=""
		while end==False:
			path=os.path.dirname(path)
			for f in os.scandir(path):
				if f.name.startswith("metadata")==True:
					end=True
					path=f.path
					break
			if path.count("/")<=2:
				end=True
		if path.endswith("json") or path.endswith("desktop"):
			with open(path,"r") as f:
				fcontent=f.readlines()
			for l in fcontent:
				if l.lstrip().startswith("\"X-KWin-Config-TranslationDomain\""):
					domain=l.split(":")[-1]
					domain=domain.replace(" ","").replace("\"","").replace(",","").strip()
		if len(domain)>0:
			domainPath=os.path.join(os.path.dirname(path),"contents","locale")
			gettext.bindtextdomain(domain,domainPath)
			gettext.textdomain(domain)
		return(domain)
#class QKdeConfigWidget

if __name__=="__main__":
	obj=QKdeConfigWidget()
