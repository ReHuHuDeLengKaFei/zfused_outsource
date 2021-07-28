#coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
import sys
import os

from Qt import QtWidgets,QtGui,QtCore

from zcore import resource,language

from zwidgets.widgets import lineedit

__all__ = ["ThumbnailWidget"]


class ThumbnailWidget(QtWidgets.QFrame):
    def __init__(self, entity_type, parent = None):
        super(ThumbnailWidget, self).__init__(parent)

        self._entity_type = entity_type

        self._build()

    def color(self):
        """ 
        """
        return self.color_widget.color()

    def order_widget(self):
        return self.color_widget

    def _build(self):
        """ build name widget

        """
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(4)
        _layout.setContentsMargins(8,8,8,8)
        self.title_widget = QtWidgets.QWidget()
        self.title_widget.setFixedWidth(120)
        _layout.addWidget(self.title_widget)
        self.title_layout = QtWidgets.QVBoxLayout(self.title_widget)
        self.title_layout.setSpacing(0)
        self.title_layout.setContentsMargins(0,0,0,0)
        self.title_button = QtWidgets.QPushButton()
        self.title_layout.addWidget(self.title_button)
        self.title_button.setObjectName("attr_title_button")
        self.title_button.setIcon(QtGui.QIcon(resource.get("icons", "{}.png".format(self._entity_type))))
        self.title_button.setText("{}".format(language.word(self._entity_type)))
        self.title_layout.addStretch(True)
