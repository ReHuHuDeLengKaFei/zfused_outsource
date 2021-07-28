# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

from zwidgets.widgets import lineedit,button

from . import listview,listmodel,itemdelegate

# from . import newlibrarydialog

__all__ = ["LibraryListWidget"]

logger = logging.getLogger(__name__)


class LibraryListWidget(QtWidgets.QFrame):
    library_selected = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(LibraryListWidget, self).__init__(parent)
        self._build()

        self.refresh_button.clicked.connect(self.load_config)
        self.list_view.clicked.connect(self._select_library)

    def _select_library(self, index):
        _data = index.data()
        if index:
            self.library_selected.emit(_data.id())

    def filter_record(self):
        return self._filter_record

    def _check_all(self, is_checked):
        # 
        _items = self.list_model.items(recursive = True)
        if _items:
            for _item in _items:
                _item.set_checked(is_checked)
            self.list_view.update()

    def load_config(self):
        _librarys = zfused_api.library.cache()
        if _librarys:
            _datas = [zfused_api.library.Library(_library["Id"]) for _library in _librarys]
            self.list_model = listmodel.ListModel(_datas)
            self.list_proxy_model.setSourceModel(self.list_model)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        self.head_widget = QtWidgets.QFrame()
        _layout.addWidget(self.head_widget)
        self.head_widget.setMinimumHeight(30)
        self.head_widget.setObjectName("attr_frame")
        self.head_layout = QtWidgets.QHBoxLayout(self.head_widget)
        self.head_layout.setSpacing(0)
        self.head_layout.setContentsMargins(0,0,0,0)
        # name 
        self.name_button = QtWidgets.QPushButton()
        self.name_button.setObjectName("icon_button")
        self.name_button.setText(language.word("library"))
        self.name_button.setIcon(QtGui.QIcon(resource.get("icons", "library.png")))
        self.name_button.setFixedHeight(30)
        self.head_layout.addWidget(self.name_button)
        self.head_layout.addStretch(True)
        # 刷新
        self.refresh_button = button.IconButton( self, 
                                                 resource.get("icons", "refresh.png"),
                                                 resource.get("icons", "refresh_hover.png"),
                                                 resource.get("icons", "refresh_pressed.png") )
        self.refresh_button.setFixedSize(30,30)
        self.head_layout.addWidget(self.refresh_button)
        
        # search lineedit
        self.search_lineedit = lineedit.SearchLineEdit()
        _layout.addWidget(self.search_lineedit)
        self.search_lineedit.setFixedHeight(30)

        # tree view
        self.list_view = listview.ListView()
        self.list_view.setItemDelegate(itemdelegate.ItemDelegate(self.list_view))
        _layout.addWidget(self.list_view)
        self.list_model = listmodel.ListModel([])
        self.list_proxy_model = listmodel.ListFilterProxyModel()
        self.list_view.setModel(self.list_proxy_model)
