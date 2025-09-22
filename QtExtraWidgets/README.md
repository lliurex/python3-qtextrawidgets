# python3-extrawidgets
This package contains a set of custom pyside2 widgets.

## QCheckableComboBox
Combobox with checkboxes for items

```
class QCheckableComboBox(QComboBox)
|  Functions:
|    addItem(item,Qt.CheckState) -> bool
|		Inserts item with chkbtn=Qt.CheckState
|
|    setText(text) -> str
|       Sets "text" at index 0 as placeholder
|
|  	 setState(index,Qt.CheckState): -> int,bool
|	    Sets check for item at index
|
|    getITems():
|		Returns array of items
|
|  Signals:
|    clicked
|      Emited when item is clicked
|    closed
|      Emited when popup menu closes
|
```
### TODO:
* Add getState(index) -> int
*  Add signal stateChanged

## QHotkeyButton
QPushButton designed for hotkey assignment
This buttons has an embedded event filter that carries all the logic for the operation.
The assigned hotkey is holded by the text() method of pushbutton.

```
class QHotkeyButton(QPushButton)
|  Functions:
|    revertHotkey():
|		reverts last assignment
|  Signals:
|    hotkeyAssigned({hotkey:str,action:str}):
|		Emited when a hotkey is assigned
```

## QScreenShotContainer
Widget for view images inside a horizontal scrollbar with embedded previewer.
The widget itself loads the images through threads and has its own configurable cache folder for images.

```
|class QScreenShotContainer(QWidget)
|  Functions:
|    setCacheDir(dirpath) -> str
|      Sets cache folder for images
|
|    addImage(filepath) ->str
|      Adds given image to the carrousel
|
|    clear()
|		Removes all content
|
```   
