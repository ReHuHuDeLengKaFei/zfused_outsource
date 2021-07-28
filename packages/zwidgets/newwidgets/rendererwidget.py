#coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
import sys
import os

from Qt import QtWidgets,QtGui,QtCore

from zcore import resource,language

from zwidgets.widgets import lineedit

__all__ = ["RendererWidget"]

renderers = [
    "vray",
    "redshift",
    "arnold",
    "renderman"
]


class RendererWidget(QtWidgets.QFrame):
    def __init__(self, entity_type, parent = None):
        super(RendererWidget, self).__init__(parent)

        self._entity_type = entity_type

        self._build()

    def clear(self):
        _button = self.renderer_group.checkedButton()
        if _button:
            self.renderer_group.setExclusive(False)
            _button.setChecked(False)
            self.renderer_group.setExclusive(True)

    def renderer(self):
        _button = self.renderer_group.checkedButton()
        if _button:
            return _button.text()
        return ""

    def order_widget(self):
        return self.code_lineedit

    def _build(self):
        """ build name widget
        """
        self.setObjectName("window_menu_frame")
        _layout = QtWidgets.QHBoxLayout(self)

        _layout.setSpacing(4)
        _layout.setContentsMargins(8,8,8,8)

        # title button
        self.title_button = QtWidgets.QPushButton()
        _layout.addWidget(self.title_button)
        self.title_button.setObjectName("attr_title_button")
        self.title_button.setMinimumWidth(120)
        #self.title_button.setIcon(QtGui.QIcon(resource.get("icons", "{}.png".format(self._entity_type))))
        #self.title_button.setText("{}{}".format(language.word(self._entity_type), language.word("code")))
        self.title_button.setText(u"渲染器")

        self.renderer_group = QtWidgets.QButtonGroup()
        # name lineedit
        for _renderer in renderers:
            _renderer_checkbox = QtWidgets.QCheckBox()
            _renderer_checkbox.setText(_renderer)
            _layout.addWidget(_renderer_checkbox)
            self.renderer_group.addButton(_renderer_checkbox)

        _layout.addStretch(True)
        # self.code_lineedit = lineedit.LineEdit()
        # _layout.addWidget(self.code_lineedit)
        # self.code_lineedit.set_tip(language.word("required"))
        # _code_reg_exp = QtCore.QRegExp("[A-Za-z0-9_]{6,30}")
        # _pReg =  QtGui.QRegExpValidator(_code_reg_exp)
        # self.code_lineedit.setValidator(_pReg)
        
        # # star button
        # self.star_button = QtWidgets.QPushButton()
        # _layout.addWidget(self.star_button)
        # self.star_button.setObjectName("attr_title_button")
        # self.star_button.setIcon(QtGui.QIcon(resource.get("icons", "must.png")))
        # self.star_button.setMaximumSize(20,20)

        
        
        