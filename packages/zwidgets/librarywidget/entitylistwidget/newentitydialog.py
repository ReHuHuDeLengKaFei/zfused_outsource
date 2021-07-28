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

__all__ = ["NewEntityDialog"]


class NewEntityDialog(dialog.Dialog):
    def __init__(self, library_id, parent = None):
        super(NewEntityDialog, self).__init__(parent)
        self._build()

        self._library_id = library_id
        self._library_handle = zfused_api.library.Library(self._library_id)
        self.title_button.setText(self._library_handle.name_code())

    @staticmethod
    def new_entity(library_id, parent = None):
        """
        """
        dialog = NewEntityDialog(library_id, parent)
        dialog.show()
        result = dialog.exec_()
        if result:
            return (dialog.create_new_entity(), result)
        else:
            return 0, False
            
    def accept(self):
        """ reload accept
        """
        _name = self.name_widget.name()
        if not _name:
            self.set_tip("asset name not exist")
            return
        _code = self.code_widget.code()
        if not _code:
            self.set_tip("asset code not exist")
            return
        super(NewEntityDialog, self).accept()

    def create_new_entity(self):
        _name = self.name_widget.name()
        _code = self.code_widget.code()
        _description = self.description_widget.description()
        _value, _err = zfused_api.library.new_entity(_name, _code, self._library_id, 0, _description)
        if not _err:
            self.set_tip(_value)
            return 0
        return _value

    def _build(self):
        """ build ass user widget
        
        """
        self.resize(400,600)
        self.set_title(language.word("new library entity"), resource.get("icons", "library.png"))
        
        # library title
        self.title_button = QtWidgets.QPushButton()
        self.add_content_widget(self.title_button)

        # content widgets
        self.content_widget = QtWidgets.QWidget()
        self.add_content_widget(self.content_widget)
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)

        # name widget
        self.name_widget = namewidget.NameWidget("library entity")
        self.content_layout.addWidget(self.name_widget)
        
        # code widget
        self.code_widget = codewidget.CodeWidget("library entity")
        self.content_layout.addWidget(self.code_widget)
        
        # category widget
        # self.category_widget = categorywidget

        #  description widget
        self.description_widget = descriptionwidget.DescriptionWidget("library entity")
        self.content_layout.addWidget(self.description_widget)

        self.content_layout.addStretch(True)

        # tab order 
        self.setTabOrder(self.name_widget.order_widget(), self.code_widget.order_widget())
        # self.setTabOrder(self.code_widget.order_widget(), self.type_widget.order_widget())
        # self.setTabOrder(self.type_widget.order_widget(), self.status_widget.order_widget())
        # self.setTabOrder(self.status_widget.order_widget(), self.description_widget.order_widget())