import qprop
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class Example(QtGui.QWidget):
	def __init__(self):
		super(Example, self).__init__()
		self.prop = qprop.QPropWidget(self)

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	main = Example()
	main.show()
	app.exec_()

