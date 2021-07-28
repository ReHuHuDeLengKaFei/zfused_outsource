#coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
import sys
import os

from Qt import QtWidgets,QtGui,QtCore

from zcore import resource,language

from zwidgets.widgets import lineedit

__all__ = ["DescriptionWidget"]


class DescriptionWidget(QtWidgets.QFrame):
    def __init__(self, entity_type, parent = None):
        super(DescriptionWidget, self).__init__(parent)

        self._entity_type = entity_type

        self._build()

    def clear(self):
        self.description_textedit.setText("")

    def description(self):
        """ return name
        """
        return self.description_textedit.toPlainText()

    def order_widget(self):
        return self.description_textedit

    def _build(self):
        """ build name widget

        """
        self.setObjectName("window_menu_frame")
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(4)
        _layout.setContentsMargins(8,8,8,8)
        self.title_widget = QtWidgets.QWidget()
        self.title_layout = QtWidgets.QVBoxLayout(self.title_widget)
        self.title_layout.setSpacing(0)
        self.title_layout.setContentsMargins(0,0,0,0)
        # title button
        #
        self.title_button = QtWidgets.QPushButton()
        self.title_button.setObjectName("attr_title_button")
        self.title_button.setMinimumWidth(120)
        self.title_button.setIcon(QtGui.QIcon(resource.get("icons", "{}.png".format(self._entity_type))))
        self.title_button.setText("{}{}".format(language.word(self._entity_type), language.word("description")))
        self.title_layout.addWidget(self.title_button)
        self.title_layout.addStretch(True)

        # name lineedit
        #
        self.description_textedit = QtWidgets.QTextEdit()

        _layout.addWidget(self.title_widget)
        _layout.addWidget(self.description_textedit)