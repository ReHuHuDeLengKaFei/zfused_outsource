# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function


class Item(object):
    """
    数据类
    """

    def __init__(self, object, id, parent=None):
        self._parent_item = parent
        self._object = object
        self._id = id
        self._item_handle = None
        self._child_items = []

    def set_parent(self, parent):
        self._parent_item = parent

    def object(self):
        """
        itemdata object

        """
        return self._object

    def id(self):
        """
        return id

        """
        return self._id

    def append_child(self, item):
        self._child_items.append(item)
        item.set_parent(self)

    def child(self, row):
        return self._child_items[row]

    def children(self, allDescendents=False):
        if not allDescendents:
            return self._child_items

    def child_count(self, allDescendents=False):
        """
        return all child count

        rtype: int
        """
        if not allDescendents:
            return len(self._child_items)

        all_child = []

        def count(item, all_child):
            children = item.children()
            if children:
                all_child.append(item.children())
                for _item in children:
                    count(_item, all_child)
        count(self, all_child)

        return len(all_child)

    def parent(self):
        return self._parent_item

    def row(self):
        if self._parent_item:
            return self._parent_item._child_items.index(self)
        return 0