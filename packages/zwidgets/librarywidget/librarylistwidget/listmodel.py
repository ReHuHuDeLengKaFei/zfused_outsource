# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import sys
import logging

from Qt import QtGui, QtCore

import zfused_api

__all__ = ["ListFilterProxyModel", "ListModel"]

_logger = logging.getLogger(__name__)


class ListFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ListFilterProxyModel, self).__init__(parent)

        # 状态删选列表
        self._search_text = ""

    def search(self, text):
        self._search_text = text
        self.invalidateFilter()

    def _search(self, data):
        if not self._search_text:
            return True
        _in_name = self._search_text.lower() in data.full_name_code().lower()
        _link_handle = zfused_api.objects.Objects(data.data()["Object"], data.data()["LinkId"])
        _in_link_name = self._search_text.lower() in _link_handle.full_name_code().lower()
        if _in_name or _in_link_name:
            return True
        return False

    def filterAcceptsRow(self, sourceRow, sourceParent):
        assignedTo_index = self.sourceModel().index(sourceRow, 0, sourceParent)
        _data = self.sourceModel().data(assignedTo_index)
        return ( self._search(_data) )


class ListModel(QtCore.QAbstractListModel):
    """
    asset model

    """

    def __init__(self, data = [], parent = None):
        super(ListModel, self).__init__(parent)
        self._items = data

    def rowCount(self, parent = QtCore.QModelIndex()):
        """
        return len asset
        """
        if self._items:
            return len(self._items)
        return 0

    def data(self, index, role=0):
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        if role == 0:
            return self._items[index.row()]

