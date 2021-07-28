# coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

from zwidgets.widgets import button


__all__ = ["CategoryWidget"]

logger = logging.getLogger(__name__)


class CategoryWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(CategoryWidget, self).__init__(parent)
        self._build()

        self._library_id = 0

    #     self.new_button.clicked.connect(self._new_category)

    # def _new_category(self):
    #     if not self._library_id:
    #         return
    #     _id,_status = assigncategorydialog.AssignCategoryDialog.get_category("library" ,self)
    #     if _status:
    #         _library_handle = zfused_api.library.Library(self._library_id)
    #         _library_handle.set_category(_id)
    #         self._load()

    def load_library(self, library_id):
        if self._library_id == library_id:
            return 
        self._library_id = library_id
        self._load()

    def _load(self):
        for i in range(self.category_layout.count()):
            self.category_layout.itemAt(i).widget().deleteLater()
        _library_categorys = zfused_api.zFused.get("library_category", filter = {"LibraryId": self._library_id})
        if _library_categorys:
            for _library_category in _library_categorys:
                _item = _category_item_widget(_library_category.get("CategoryId"))
                self.category_layout.addWidget(_item)
        _item = _category_item_widget(0)
        self.category_layout.addWidget(_item)

    def _build(self):
        """ build widget
        """
        self.setFixedHeight(40)

        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(4)
        _layout.setContentsMargins(2,2,2,2)

        self.all_button = button.IconButton( self,
                                             resource.get("icons","category.png"),
                                             resource.get("icons","category_hover.png"),
                                             resource.get("icons","category_pressed.png") )
        self.all_button.setText("选择所有")
        _layout.addWidget(self.all_button)

        #  add line
        _line = QtWidgets.QFrame()
        _line.setMinimumWidth(1)
        _line.setStyleSheet("QFrame{background-color: #E6E7EA}")
        _layout.addWidget(_line)

        self.category_layout = QtWidgets.QHBoxLayout()
        _layout.addLayout(self.category_layout)
        self.category_layout.setSpacing(2)
        self.category_layout.setContentsMargins(0,0,0,0)

        #  add line
        _line = QtWidgets.QFrame()
        _line.setMinimumWidth(1)
        _line.setStyleSheet("QFrame{background-color: #E6E7EA}")
        _layout.addWidget(_line)

        _layout.addStretch(True)



class _category_item_widget(QtWidgets.QFrame):
    is_checked = QtCore.Signal(int, bool)
    def __init__(self, category_id, parent = None):
        super(_category_item_widget, self).__init__(parent)
        self._category_id = category_id
        if category_id:
            self._category_handle = zfused_api.category.Category(self._category_id)
        self._build()

        self.set_checked(True)
        self.select_checkbox.stateChanged.connect(self._is_checked)
        
    def _is_checked(self, is_checked):
        self.is_checked.emit(self._category_id, is_checked)
        self.set_checked(is_checked)

    def name_code(self):
        if not self._category_id:
            return "其他(other)"
        else:
            return self._category_handle.name_code()

    def name(self):
        if not self._category_id:
            return "其他"
        else:
            return self._category_handle.name()

    def code(self):
        if not self._category_id:
            return "other"
        else:
            return self._category_handle.code()

    def set_checked(self, is_check = True):
        if self._category_id:
            _selected_color = self._category_handle.color()
        else:
            _selected_color = "#FF0000"
        self.select_checkbox.setChecked(is_check)
        if is_check:
            self.setStyleSheet("QCheckBox{color:%s}"%(_selected_color))
        else:
            self.setStyleSheet("QCheckBox:unchecked{ color: #666666; }")

    def _build(self):
        """
        """
        # self.setFixedWidth(100)
        _layout = QtWidgets.QHBoxLayout(self)
        # _layout.setSpacing(2)
        _layout.setContentsMargins(4,0,4,0)

        self.select_checkbox = QtWidgets.QCheckBox(self)
        # self.select_checkbox.setObjectName("working_checkbox")
        _layout.addWidget(self.select_checkbox)

        self.select_checkbox.setText(self.name())

        # # title button
        # self.title_button = QtWidgets.QPushButton()
        # _layout.addWidget(self.title_button)
        # self.title_button.setObjectName("attr_title_button")
        # # self.title_button.setMinimumWidth(120)
        # #self.title_button.setIcon(QtGui.QIcon(resource.get("icons", "{}.png".format(self._category_handle.code()))))
        # self.title_button.setText(self.name_code())
        
        # _layout.addStretch(True)

