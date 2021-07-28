#coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
import sys
import os

from Qt import QtWidgets,QtGui,QtCore

from zcore import resource,language

from zwidgets import colorcardwidget
from zwidgets.widgets import lineedit

__all__ = ["ColorWidget"]


class ColorWidget(QtWidgets.QFrame):
    def __init__(self, entity_type, parent = None):
        super(ColorWidget, self).__init__(parent)

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

        # name lineedit
        self.color_widget = colorcardwidget.ColorCardWidget()
        _layout.addWidget(self.color_widget)
        
        # # star button
        # self.star_button = QtWidgets.QPushButton()
        # _layout.addWidget(self.star_button)
        # self.star_button.setObjectName("attr_title_button")
        # self.star_button.setIcon(QtGui.QIcon(resource.get("icons", "must.png")))
        # self.star_button.setMaximumSize(20,20)

        
        
        