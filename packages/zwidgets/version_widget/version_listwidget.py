# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets,QtCore

from ._version_listwidget import version_listmodel
from ._version_listwidget import version_listview
from ._version_listwidget import version_itemdelegate


__all__ = ["VersionListWidget"]

logger = logging.getLogger(__name__)


class VersionListWidget(QtWidgets.QFrame):
    clicked = QtCore.Signal(QtCore.QModelIndex)
    def __init__(self, parent = None):
        super(VersionListWidget, self).__init__(parent)
        self._build()

        self.list_view.clicked.connect(self.clicked.emit)
        
    def load_versions(self, versions):
        self.model = version_listmodel.VersionListModel(versions)
        self.proxy_model.setSourceModel(self.model)
        self.list_view.setModel(self.proxy_model)
        self.update()

    def index(self):
        return self.list_view.currentIndex()

    def set_mode(self):
        pass

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

        #  资产列表
        self.list_view = version_listview.VersionListView()
        _layout.addWidget(self.list_view)
        self.proxy_model = version_listmodel.VersionListFilterProxyModel()
        self.list_view.setItemDelegate(version_itemdelegate.VersionItemDelegate(self.list_view))