# coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language,cache,zfile

from zwidgets import newwidgets
from zwidgets.widgets import button


__all__ = ["FileWidget"]

logger = logging.getLogger(__name__)


class FileWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(FileWidget, self).__init__(parent)
        self._build()

        self._entity_id = 0

        self.new_file_button.clicked.connect(self.new_file_widget.showNormal)

    @zfused_api.reset
    def load_entity(self, entity_id):
        self.new_file_widget.clear()
        self.new_file_widget.hide()
        self.new_file_widget.load_entity(entity_id)
        
        # if self._entity_id == entity_id:
        #     return
        
        self._entity_id = entity_id
        self._entity_handle = zfused_api.library.LibraryEntity(entity_id)
        self.new_file_widget.code_widget.code_lineedit.setText(self._entity_handle.code())
        
        # clear
        if self.file_layout.count():
            for i in range(self.file_layout.count()):
                _item = self.file_layout.itemAt(i) # .widget() # .deleteLater()
                if isinstance(_item, QtWidgets.QSpacerItem):
                    self.file_layout.removeItem(_item)
                    del _item
                else:
                    _item.widget().deleteLater()
        # editions
        _editions = zfused_api.zFused.get("library_entity_edition", filter = {"LibraryEntityId": self._entity_id},
                                                                    sortby = ["CreatedTime"], order = ["desc"] )
        if _editions:
            for _edition in _editions:
                _widget = EditionWidget(_edition.get("Id"))
                self.file_layout.addWidget(_widget)
            self.file_layout.addStretch(True)
        else:
            _editions = []
        self.title_label.setText("文件 · {}".format(len(_editions)))

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        self.title_widget = QtWidgets.QWidget()
        self.title_widget.setFixedHeight(30)
        _layout.addWidget(self.title_widget)
        self.title_layout = QtWidgets.QHBoxLayout(self.title_widget)
        self.title_layout.setSpacing(0)
        self.title_layout.setContentsMargins(0,0,0,0)
        self.title_label = QtWidgets.QLabel()
        self.title_label.setText("文件 · 0")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch(True)
        # new file button
        self.new_file_button = button.IconButton( self, 
                                                  resource.get("icons","add.png"),
                                                  resource.get("icons","add_hover.png"),
                                                  resource.get("icons","add_pressed.png") )
        self.new_file_button.setFixedHeight(30)
        self.new_file_button.setText(u"新建版本")
        self.title_layout.addWidget(self.new_file_button)
    
        # scroll widget
        self.scroll_widget = QtWidgets.QScrollArea(self)
        _layout.addWidget(self.scroll_widget)
        self.scroll_widget.setWidgetResizable(True)
        self.scroll_widget.setBackgroundRole(QtGui.QPalette.NoRole)

        self.file_widget = QtWidgets.QFrame()
        self.scroll_widget.setWidget(self.file_widget)
        self.file_layout = QtWidgets.QVBoxLayout(self.file_widget)

        # new file widget
        self.new_file_widget = _NewWidget()
        _layout.addWidget(self.new_file_widget)
        self.new_file_widget.hide()


class EditionWidget(QtWidgets.QFrame):
    def __init__(self, edition_id, parent = None):
        super(EditionWidget, self).__init__(parent)
        self._build()
        self._edition_id = edition_id
        self._edition_handle = zfused_api.library.LibraryEntityEdition(self._edition_id)

        self._spacing = 8

    def paintEvent(self, event):
        super(EditionWidget, self).paintEvent(event)
        if not self._edition_id:
            return

        _rect = self.rect()
        _painter = QtGui.QPainter()
        _painter.begin(self)
        _painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        
        _painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,100)))
        _painter.setBrush(QtGui.QBrush(QtGui.QColor(40, 40, 40)))
        _painter.drawRoundedRect(_rect, 2, 2)

        _font = QtGui.QFont("Microsoft YaHei UI")
        _font.setPixelSize(14)
        _font.setBold(True)
        _painter.setFont(_font)
        _fm = QtGui.QFontMetrics(_font)
    
        # draw code
        _code = self._edition_handle.code()
        _code_width = _fm.width(_code)
        _title_rect = QtCore.QRectF( _rect.x() + self._spacing,
                                    _rect.y(),
                                    _code_width + self._spacing*2,
                                    _rect.height() )
        _painter.setPen(QtGui.QPen(QtGui.QColor(125, 125, 125)))
        _painter.drawText(_title_rect, QtCore.Qt.AlignCenter, _code)

        # software
        _software_handle = zfused_api.software.Software(self._edition_handle.data().get("SoftwareId") )
        _code = _software_handle.code()
        _code_width = _fm.width(_code)
        _software_rect = QtCore.QRectF( _title_rect.x() + _title_rect.width() + self._spacing,
                                      _rect.y(),
                                      _code_width + self._spacing,
                                      _rect.height() )
        _painter.drawText(_software_rect, QtCore.Qt.AlignCenter, _code)

        _painter.end()

    def _build(self):
        self.setFixedHeight(40)
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(2,2,2,2)

        _layout.addStretch(True)

        self.load_button = QtWidgets.QPushButton()
        self.load_button.setText(u"加载")
        self.load_button.setFixedSize(100,30)
        _layout.addWidget(self.load_button)


class _NewWidget(QtWidgets.QFrame):
    publish = QtCore.Signal(dict)
    def __init__(self, parent = None):
        super(_NewWidget, self).__init__(parent)
        self._build()

        self._library_entity_id = 0
        self.publish_button.clicked.connect(self._publish)

    def clear(self):
        self.code_widget.clear()
        self.renderer_widget.clear()
        self.description_widget.clear()

    def load_entity(self, entity_id):
        self._library_entity_id = entity_id

    def _publish(self):
        self.error_label.setText("")
        # # get name
        # _name = self.name_widget.name()
        # if not _name:
        #     self.error_label.setText("name is not exists")
        #     return
        # get code 
        _code = self.code_widget.code()
        if not _code:
            self.error_label.setText("code is not exists")
            return
        # get software
        # get renderer
        _renderer = self.renderer_widget.renderer()
        # get description
        _description = self.description_widget.description()
        if not _description:
            self.error_label.setText("description is not exists")
            return
        # # check edition is exists
        # _editions = zfused_api.zFused.get("library_entity_edition", filter = {"Code": _code, "LibraryEntityId":self._library_entity_id})
        # if _editions:
        #     self.error_label.setText("{} is exists".format(_code))
        #     return
        _library_entity_handle = zfused_api.library.LibraryEntity(self._library_entity_id)
        _publish_info = {
            "library_id": _library_entity_handle.data().get("LibraryId"),
            "library_entity_id": self._library_entity_id,
            "code":_code,
            "renderer": _renderer,
            "description":_description
        }
        self.publish.emit(_publish_info)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)

        # # name widget
        # self.name_widget = newwidgets.NameWidget("version")
        # _layout.addWidget(self.name_widget)

        # code widget
        self.code_widget = newwidgets.CodeWidget("version")
        _layout.addWidget(self.code_widget)

        # step 
    
        # renderer
        self.renderer_widget = newwidgets.RendererWidget("renderer")
        _layout.addWidget(self.renderer_widget)

        # description widget
        self.description_widget = newwidgets.DescriptionWidget("version")
        _layout.addWidget(self.description_widget)
        
        # operation widget
        #  push widget
        self.publish_widget = QtWidgets.QFrame()
        _layout.addWidget(self.publish_widget)
        self.publish_layout = QtWidgets.QHBoxLayout(self.publish_widget)
        self.publish_layout.setContentsMargins(0,0,0,0 )
        # error
        self.error_label = QtWidgets.QLabel()
        self.error_label.setStyleSheet("QLabel{color:#FF0000}")
        self.publish_layout.addWidget(self.error_label)
        # upload button
        self.publish_button = QtWidgets.QPushButton()
        self.publish_button.setMinimumSize(100,30)
        self.publish_button.setObjectName("publish_button")
        self.publish_button.setIcon(QtGui.QIcon(resource.get("icons","publish.png")))
        self.publish_button.setText(u"上传文件")
        self.publish_layout.addStretch(True)
        self.publish_layout.addWidget(self.publish_button)