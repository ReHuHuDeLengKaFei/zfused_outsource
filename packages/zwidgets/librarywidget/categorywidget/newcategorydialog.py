#coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
import sys
import os

from Qt import QtWidgets,QtGui,QtCore

import zfused_api

from zcore import resource,language

from zwidgets.widgets import button, dialog
from zwidgets.newwidgets import namewidget,codewidget,pathwidget,colorwidget,thumbnailwidget,descriptionwidget

__all__ = ["NewCategoryDialog"]


class NewCategoryDialog(dialog.Dialog):
    def __init__(self, library_id, parent = None):
        super(NewCategoryDialog, self).__init__(parent)
        self._build()

        self._library_id = library_id
        self._library_handle = zfused_api.library.Library(self._library_id)
        self.title_button.setText(self._library_handle.name_code())

    @staticmethod
    def new_category(library_id, parent = None):
        """
        """
        dialog = NewCategoryDialog(library_id, parent)
        dialog.show()
        result = dialog.exec_()
        if result:
            return (dialog.create_new_category(), result)
        else:
            return 0, False
            
    def accept(self):
        """ reload accept
        """
        _name = self.name_widget.name()
        if not _name:
            self.set_tip("category name not exist")
            return
        _code = self.code_widget.code()
        if not _code:
            self.set_tip("category code not exist")
            return
        _color = self.color_widget.color()
        if not _color:
            self.set_tip("color not exist")
            return
        # if zfused_api.zFused.get("category", filter = {"EntityType": "library", "Code": _code}):
        #     self.set_tip("{} is exists".format(_code))
        #     return
        super(NewCategoryDialog, self).accept()

    def create_new_category(self):
        _name = self.name_widget.name()
        _code = self.code_widget.code()
        _color = self.color_widget.color()
        _description = self.description_widget.description()
        _value, _err = self._library_handle.new_category(_name, _code, _color, _description)
        return _value

    def _build(self):

        self.resize(400,600)
        self.set_title(language.word("new category"), resource.get("icons", "category.png"))
        
        # library title
        self.title_button = QtWidgets.QPushButton()
        self.add_content_widget(self.title_button)

        # content widgets
        self.content_widget = QtWidgets.QWidget()
        self.add_content_widget(self.content_widget)
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)

        # name widget
        self.name_widget = namewidget.NameWidget("category")
        self.content_layout.addWidget(self.name_widget)
        
        # code widget
        self.code_widget = codewidget.CodeWidget("category")
        self.content_layout.addWidget(self.code_widget)
        
        # color widget
        self.color_widget = colorwidget.ColorWidget("color")
        self.color_widget.setFixedHeight(200)
        self.content_layout.addWidget(self.color_widget)

        #  description widget
        self.description_widget = descriptionwidget.DescriptionWidget("category")
        self.content_layout.addWidget(self.description_widget)

        self.content_layout.addStretch(True)

        # tab order 
        self.setTabOrder(self.name_widget.order_widget(), self.code_widget.order_widget())
        # self.setTabOrder(self.code_widget.order_widget(), self.type_widget.order_widget())
        # self.setTabOrder(self.type_widget.order_widget(), self.status_widget.order_widget())
        # self.setTabOrder(self.status_widget.order_widget(), self.description_widget.order_widget())