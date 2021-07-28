#coding:utf-8
#--author-- lanhua.zhou

import logging

from Qt import QtWidgets,QtGui,QtCore

from zcore import resource,language

from zwidgets.widgets import button,lineedit

__all__ = ["OperationWidget"]

logger = logging.getLogger(__name__)


class OperationWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(OperationWidget, self).__init__(parent)
        self._build()
            
    def _build(self):
        """ build widget
        """
        self.setFixedHeight(40)
        self.setObjectName("library_operation_frame")

        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)
        
        # # new button
        # self.new_button = button.IconButton( self, 
        #                                               resource.get("icons", "add.png"),
        #                                               resource.get("icons", "add_hover.png"),
        #                                               resource.get("icons", "add_pressed.png"))
        # self.new_button.setText(language.word("new object"))
        # self.new_button.setMaximumHeight(25)
        # _layout.addWidget(self.new_button)

        _layout.addStretch(True)

        # search lineedit
        self.search_lineedit = lineedit.SearchLineEdit()
        self.search_lineedit.setFixedSize(200, 25)
        _layout.addWidget(self.search_lineedit)

        # refresh button 
        self.refresh_button = button.IconButton( self, 
                                                 resource.get("icons", "refresh.png"),
                                                 resource.get("icons", "refresh_hover.png"),
                                                 resource.get("icons", "refresh_pressed.png"))
        #self.refresh_button.setText(language.word("refresh"))
        self.refresh_button.setFixedSize(30,30)
        _layout.addWidget(self.refresh_button)

        #  add line
        _line = QtWidgets.QFrame()
        _line.setMinimumWidth(1)
        _line.setStyleSheet("QFrame{background-color: #E6E7EA}")
        _layout.addWidget(_line)