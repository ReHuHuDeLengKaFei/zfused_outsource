# coding:utf-8
# --author-- lanhua.zhou

""" shading color widget """

from Qt import QtWidgets, QtCore

import maya.cmds as cmds
import maya.mel as mm

from zfused_maya.ui.widgets import window


class ToStandardSurface(window._Window):
    def __init__(self, parent = None):
        super(ToStandardSurface, self).__init__(parent)
        self._build()

        self.convert_button.clicked.connect(self._convert)
        self.listWidget.itemSelectionChanged.connect(self._select_item)

    def _select_item(self):
        selName = self.listWidget.selectedItems()
        try:
            import maya.cmds as cmds
            cmds.select(cl = 1)
            for name in selName:
                cmds.select(name.text(),add = 1)
        except:
            pass

    def showEvent(self, event):
        self._check()
        super(ToStandardSurface, self).showEvent(event)

    def _check(self):
        self.listWidget.clear()
        _default_materials = ["lambert1", "particleCloud1", "standardSurface1"]
        _materials = cmds.ls(mat = True)
        _materials = list( set(_materials) - set(_default_materials))
        _count = 0
        for _material in _materials:
            _type = cmds.nodeType(_material)
            if _type not in ["standardSurface","lambert","phong","blin"]:
                self.listWidget.addItem(_material)
                _count += 1
        if _count:
            self.list_label.setText(u"存在非标准材质: {} 个".format(_count))
            self.list_label.setStyleSheet("QLabel{color:#FF4444}")
        else:
            self.list_label.setText(u"场景无非maya标准材质")
            self.list_label.setStyleSheet("QLabel{color:#007acc}")

    def _convert(self):
        _ais = cmds.ls(type = "aiStandardSurface")
        for _ai in _ais:            
            _replace = cmds.createNode("standardSurface")
            mm.eval("replaceNode {} {};".format(_ai, _replace))
            cmds.delete(_ai)
            cmds.rename( _replace, _ai )
        self._check()

    def _build(self):
        self.resize(600,400)
        self.set_title(u"转换至标准材质(standardSurface)")
        
        _widget = QtWidgets.QFrame()
        self.set_central_widget(_widget)
        _layout = QtWidgets.QVBoxLayout(_widget)

        self.error_label = QtWidgets.QLabel()
        _layout.addWidget(self.error_label)
        self.error_label.setStyleSheet("QLabel{font: bold 14px;background-color:#DD4444;color:#EDEDED;Text-align: center;}")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setText("转换至标准材质前，请另存文件转换，此功能会改变材质球属性！！！\n目前只有arnold aiStandardSurface可有效切换")

        # 
        self.list_label = QtWidgets.QLabel()
        _layout.addWidget(self.list_label)
        self.list_label.setText(u"非标准材质:")
        self.listWidget = QtWidgets.QListWidget()
        _layout.addWidget(self.listWidget)
        self.listWidget.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.listWidget.setStyleSheet("background:rgb(0,0,0)")

        self.convert_button = QtWidgets.QPushButton()
        _layout.addWidget(self.convert_button)
        self.convert_button.setFixedHeight(40)
        self.convert_button.setText(u"转换至标准材质球(standardSurface)")