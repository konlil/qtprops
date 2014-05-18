#coding: gbk
from PyQt4 import QtGui, QtCore

PROP_INT = 1
PROP_FLOAT = 2
PROP_STRING = 3
PROP_BOOL = 4
PROP_VECTOR3 = 5

HORIZONTAL_HEADERS = ("Property", "Value")

class PropItem(object):
	def __init__(self, name, ptype, desc, default):
		self._name = name
		self._ptype = ptype
		self._desc = desc
		self._default = default
		self._data = default
		self._children = []

	@property
	def value(self):
		return self._data

	@property
	def key(self):
		return self._name

	@property
	def desc(self):
		return self._desc

class GroupItem(PropItem):
	def __init__(self, name, ptype, desc):
		super(GroupItem, self).__init__(name, ptype, desc, None)
		self._children = []

	@property
	def value(self):
		self._data = []
		for child in self._children:
			self._data.append(child.value)
		return self._data

	@property
	def children(self):
		return self._children

	def append(self, name, ptype, desc, default):
		child = PropItem(name, ptype, desc, default)
		self._children.append(child)
		return self

class TreeItem(object):
	def __init__(self, prop, parent):
		self.prop = prop
		self.parent = parent
		self.childs = []

	def appendChild(self, item):
		self.childs.append(item)

	def child(self, row):
		return self.childs[row]

	def childCount(self):
		return len(self.childs)

	def columnCount(self):
		return 2

	def data(self, column):
		if isinstance(self.prop, GroupItem):
			if column == 0:
				return QtCore.QVariant(self.prop.desc)
			elif column == 1:
				return QtCore.QVariant(str(self.prop.value))
		else:
			if column == 0:
				return QtCore.QVariant(self.prop.desc)
			elif column == 1:
				return QtCore.QVariant(self.prop.value)
		return QtCore.QVariant()

	def parent(self):
		return self.parent

	def row(self):
		if self.parent:
			return self.parent.childs.index(self)
		return 0

class QPropModel(QtCore.QAbstractItemModel):
	def __init__(self, parent=None):
		super(QPropModel, self).__init__(parent)
		self._data = []
		self.root = TreeItem(None, None)
		self.parents = {0: self.root}
#		self.regParam('pos', PROP_VECTOR3, {'x':0, 'y':0, 'z':0})
#		self.regParam('yaw', PROP_FLOAT, 0.0)
#		self.regParam('name', PROP_STRING, 'test')
#		self.setupModelData()

	def addProp(self, prop):
		self._data.append(prop)

	def index(self, row, column, parent):
		if not self.hasIndex(row, column, parent):
			return QtCore.QModelIndex()
		if not parent.isValid():
			parent = self.root
		else:
			parent = parent.internalPointer()

		child = parent.child(row)
		if child:
			return self.createIndex(row, column, child)
		else:
			return QtCore.QModelIndex()

	def parent(self, index):
		if not index.isValid():
			return QtCore.QModelIndex()
		child = index.internalPointer()
		if not child:
			return QtCore.QModelIndex()
		parent = child.parent
		if parent == self.root:
			return QtCore.QModelIndex()
		return self.createIndex(parent.row(), 0, parent)

	def rowCount(self, parent):
		if parent.column() > 0:
			return 0
		if not parent.isValid():
			pitem = self.root
		else:
			pitem = parent.internalPointer()
		return pitem.childCount()

	def setupModelData(self):
		for prop in self._data:
			if not isinstance(prop, GroupItem):
				newItem = TreeItem(prop, self.root)
				self.root.appendChild(newItem)
			else:
				newGroup = TreeItem(prop, self.root)
				self.root.appendChild(newGroup)
				for child in prop.children:
					newItem = TreeItem(child, newGroup)
					newGroup.appendChild(newItem)

	def columnCount(self, parent=None):
		if parent and parent.isValid():
			return parent.internalPointer().columnCount()
		else:
			return len(HORIZONTAL_HEADERS)

	def data(self, index, role):
		if not index.isValid():
			return QtCore.QVariant()
		item = index.internalPointer()
		if role == QtCore.Qt.DisplayRole:
			return item.data(index.column())
		elif role == QtCore.Qt.UserRole:
			if item:
				return item.person
		return QtCore.QVariant()

	def headerData(self, column, orientation, role):
		if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole):
			try:
				return QtCore.QVariant(HORIZONTAL_HEADERS[column])
			except IndexError:
				pass
		return QtCore.QVariant()

class QPropWidget(QtGui.QWidget):
	def __init__(self, parent=None):
		super(QPropWidget, self).__init__(parent)

		model = QPropModel()
		pos = GroupItem('pos', PROP_VECTOR3, u'位置')
		pos.append('x', PROP_FLOAT, 'x', 0.0) \
			.append('y', PROP_FLOAT, 'y', 0.0) \
			.append('z', PROP_FLOAT, 'z', 0.0)
		model.addProp(pos)
		model.addProp(PropItem('yaw', PROP_FLOAT, u'方向', 0.0))
		model.setupModelData()
		self.tree = QtGui.QTreeView(self)
		self.tree.setModel(model)
		self.tree.setAlternatingRowColors(True)


class Example(QtGui.QWidget):
	def __init__(self):
		super(Example, self).__init__()
		layout = QtGui.QVBoxLayout(self)
		self.setLayout(layout)

		prop = QPropWidget()
		layout.addWidget(prop)

import sys
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	main = Example()
	main.resize(300, 400)
	main.show()
	app.exec_()

