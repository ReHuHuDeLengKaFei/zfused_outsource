# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

import listmodel,listview,itemdelegate
import operationwidget

# import newentitydialog

__all__ = ["EntityListWidget"]

logger = logging.getLogger(__name__)


class EntityListWidget(QtWidgets.QFrame):
    entity_selected = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(EntityListWidget, self).__init__(parent)
        self._build()

        self._library_id = 0

        self.operation_widget.search_lineedit.search_clicked.connect(self._search)
        self.operation_widget.refresh_button.clicked.connect(self._load)

        self.entity_listview.doubleClicked.connect(self._selected)

    def _selected(self, index):
        print("selected entity {}".format(index.data().get("Id")))
        self.entity_selected.emit(index.data().get("Id"))

    def _search(self, text):
        self.entity_proxy_model.search(text)

    def load_library(self, library_id):
        if self._library_id == library_id:
            return 
        self._library_id = library_id
        self._load()

    def _load(self):
        _librarys = zfused_api.library.entity_cache([self._library_id])
        if not _librarys:
            _librarys = []
        self.entity_model = listmodel.ListModel(_librarys, self.entity_listview)
        self.entity_proxy_model.setSourceModel(self.entity_model)

    def search_name(self, name):
        """ search asset name
        """
        self.entity_proxy_model.search(name)
        self.entity_proxy_model.invalidateFilter()

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

        # 操作
        self.operation_widget = operationwidget.OperationWidget()
        _layout.addWidget(self.operation_widget)

        #  资产列表
        self.entity_listview = listview.ListView()
        _layout.addWidget(self.entity_listview)
        self.entity_proxy_model = listmodel.ListFilterProxyModel(self.entity_listview)
        self.entity_listview.setItemDelegate(itemdelegate.ItemDelegate(self.entity_listview))
        self.entity_listview.setModel(self.entity_proxy_model)

        _layout.addWidget(self.entity_listview)