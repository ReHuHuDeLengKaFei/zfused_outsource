#coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
import sys
import os

from Qt import QtWidgets,QtGui,QtCore

from zcore import resource, language

from zwidgets.widgets import lineedit

__all__ = ["NameWidget"]


class NameWidget(QtWidgets.QFrame):
    def __init__(self, entity_type, parent = None):
        super(NameWidget, self).__init__(parent)

        self._entity_type = entity_type
        self._build()

    def clear(self):
        self.name_lineedit.setText("")

    def name(self):
        """ return name
        """
        return self.name_lineedit.text()

    def order_widget(self):
        return self.name_lineedit

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
        self.title_button.setIcon(QtGui.QIcon(resource.get("icons", "{}.png").format(self._entity_type)))
        self.title_button.setText("{}{}".format(language.word(self._entity_type), language.word("name")))

        # name lineedit
        self.name_lineedit = lineedit.LineEdit()
        _layout.addWidget(self.name_lineedit)
        self.name_lineedit.set_tip(language.word("required"))

        # star button
        self.star_button = QtWidgets.QPushButton()
        _layout.addWidget(self.star_button)
        self.star_button.setObjectName("attr_title_button")
        self.star_button.setIcon(QtGui.QIcon(resource.get("icons", "must.png")))
        self.star_button.setMaximumSize(20,20)

        
        
        