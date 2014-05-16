
from PyQt4 import QtGui

class QPropWidget(QtGui.QWidget):
	def __init__(self, obj, parent=None):
		super(QPropWidget, self).__init__(parent)
		self.obj = obj
