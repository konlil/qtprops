#coding: gbk
from PyQt4 import QtGui, QtCore

PROP_INT = 1
PROP_FLOAT = 2
PROP_STRING = 3
PROP_BOOL = 4
PROP_VECTOR3 = 5
PROP_VECTOR4 = 6

HORIZONTAL_HEADERS = ("Property", "Value")

class PropItem(object):
	def __init__(self, name, ptype, desc, default, rmin=None, rmax=None):
		self._name = name
		self._ptype = ptype
		self._desc = desc
		self._default = default
		self._data = default
		self._range = (rmin, rmax)
		self._children = []

	def toQVariant(self):
		return QtCore.QVariant(self._data)

	@property
	def value(self):
		return self._data

	@value.setter
	def value(self, v):
		self._data = v

	@property
	def limit(self):
		if self._range[0] is not None and self._range[1] is not None:
			return self._range
		return None

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
	
	def toQVariant(self):
		if self._ptype == PROP_VECTOR3:
			v = self.value
			obj = QtGui.QVector3D(v[0], v[1], v[2])
			return QtCore.QVariant(obj)
		elif self._ptype == PROP_VECTOR4:
			v = self.value
			obj = QtGui.QVector4D(v[0], v[1], v[2], v[3])
			return QtCore.QVariant(obj)
		else:
			return QtCore.QVariant(self._data)

	@property
	def value(self):
		self._data = []
		for child in self._children:
			self._data.append(child.value)
		return self._data

	@value.setter
	def value(self, v):
		self._data = v

	@property
	def children(self):
		return self._children

	def append(self, name, ptype, desc, default, rmin=None, rmax=None):
		child = PropItem(name, ptype, desc, default, rmin, rmax)
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

	def ptype(self):
		return self.prop._ptype

	def setPropValue(self, v):
		limit = self.prop.limit
		if limit and not (v >= limit[0] and v <= limit[1]):
			return False
		self.prop.value = v
		return True

	def getProp(self):
		return self.prop

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

	def addProp(self, prop):
		self._data.append(prop)

	def index(self, row, column, parent=QtCore.QModelIndex()):
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

	def flags(self, index):
		flag = super(QPropModel, self).flags(index)
		return flag | QtCore.Qt.ItemIsEditable

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

	def rowCount(self, parent=QtCore.QModelIndex()):
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

	def data(self, index, role=QtCore.Qt.UserRole):
		if not index.isValid():
			return QtCore.QVariant()
		item = index.internalPointer()
		if role == QtCore.Qt.DisplayRole:
			return item.data(index.column())
		elif role == QtCore.Qt.EditRole:
			return item.data(index.column())
		elif role == QtCore.Qt.UserRole:
			if item:
				return item.getProp()
		return QtCore.QVariant()

	def getData(self):
		data = {}
		rows = self.rowCount()
		for r in xrange(rows):
			idx = self.index(r, 0)
			prop = self.data(idx)
			data[prop.key] = prop.value
		return data

	def setData(self, index, value, role=QtCore.Qt.EditRole):
		if not index.isValid():
			return False

		success = False
		item = index.internalPointer()
		if role == QtCore.Qt.EditRole:
			if item.ptype() == PROP_FLOAT:
				v_float, ok = value.toDouble()
				success = item.setPropValue( v_float )
			elif item.ptype() == PROP_INT:
				v_int, ok = value.toInt()
				success = item.setPropValue( v_int )
			elif item.ptype() == PROP_BOOL:
				v_bool = value.toBool()
				success = item.setPropValue( v_bool )
			elif item.ptype() == PROP_VECTOR3:
				v_str = str(value.toString())
				value = eval(v_str)
				for i in xrange(len(value)):
					ok = item.child(i).setPropValue(value[i])
					if not ok:
						success = False
						break
		if success:
			self.dataChanged.emit(index, index)
			return True
		return False

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

		color = GroupItem('color', PROP_VECTOR4, u'颜色')
		color.append('red', PROP_INT, 'red', 0, 0, 255) \
			.append('green', PROP_INT, 'green', 0, 0, 255) \
			.append('blue', PROP_INT, 'blue', 0, 0, 255) \
			.append('alpha', PROP_INT, 'alpha', 255, 0, 255)
		model.addProp(color)
		model.addProp(PropItem('yaw', PROP_FLOAT, u'方向', 0.0))
		model.addProp(PropItem('pub', PROP_BOOL, u'发布', True))
		model.setupModelData()
		self.tree = QtGui.QTreeView(self)
		self.tree.setModel(model)
		self.tree.setAlternatingRowColors(True)
		
		self.model = model

class Example(QtGui.QWidget):
	def __init__(self):
		super(Example, self).__init__()
		layout = QtGui.QVBoxLayout(self)
		self.setLayout(layout)

		self.prop = QPropWidget()
		layout.addWidget(self.prop)

		button = QtGui.QPushButton()
		button.setText('get data')
		layout.addWidget(button)
		button.clicked.connect(self.buttonClicked)

	def buttonClicked(self):
		print self.prop.model.getData()

import sys
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	main = Example()
	main.resize(300, 400)
	main.show()
	app.exec_()

