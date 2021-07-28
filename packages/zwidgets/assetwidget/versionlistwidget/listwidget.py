# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets,QtCore

from . import listmodel
from . import listview
from . import itemdelegate


__all__ = ["ListWidget"]

logger = logging.getLogger(__name__)


class ListWidget(QtWidgets.QFrame):
    
    def __init__(self, parent = None):
        super(ListWidget, self).__init__(parent)
        self._build()
        
    def load_versions(self, versions):
        """
        加载版本

        """
        self.model = listmodel.ListModel(versions)
        self.proxy_model.setSourceModel(self.model)
        self.list_view.setModel(self.proxy_model)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

        #  资产列表
        self.list_view = listview.ListView()
        _layout.addWidget(self.list_view)
        self.proxy_model = listmodel.ListFilterProxyModel()
        self.list_view.setItemDelegate(itemdelegate.ItemDelegate(self.list_view))