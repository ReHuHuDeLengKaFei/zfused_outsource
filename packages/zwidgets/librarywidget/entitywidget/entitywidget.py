# coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from . import thumbnailwidget
from . import previewwidget
from . import filewidget

__all__ = ["EntityWidget"]

logger = logging.getLogger(__name__)


class EntityWidget(QtWidgets.QFrame):
    publish = QtCore.Signal(dict)
    def __init__(self, parent = None):
        super(EntityWidget, self).__init__(parent)
        self._build()

        self._entity_id = 0

        self.file_widget.new_file_widget.publish.connect(self.publish.emit)

    @zfused_api.reset
    def load_entity(self, entity_id):
        # if self._entity_id == entity_id:
        #     return 
        self._entity_id = entity_id
        self.thumbnail_widget.load_entity(entity_id)
        self.preview_widget.load_entity(entity_id)
        self.file_widget.load_entity(entity_id)
    
    @zfused_api.reset
    def reload(self):
        self.preview_widget.load_entity(self._entity_id)
        self.file_widget.load_entity(self._entity_id)

    def _build(self):
        """ build widget
        """
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        self.thumbnail_widget = thumbnailwidget.ThumbnailWidget()
        _layout.addWidget(self.thumbnail_widget)

        self.preview_widget = previewwidget.PreviewWidget()
        _layout.addWidget(self.preview_widget)
        
        self.file_widget = filewidget.FileWidget()
        _layout.addWidget(self.file_widget)

        
