# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging
import requests
import operator

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,color,cache

from . import constants

__all__ = ["ItemDelegate"]

logger = logging.getLogger(__name__)

IMAGE_MAX_SIZE = []


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)

        self._spacing = 4
        self._extend_width = 10
        self._font = QtGui.QFont("Microsoft YaHei UI", 9)
        self._background_color = parent.palette().color(parent.backgroundRole())

        self._file_pixmap = QtGui.QPixmap(resource.get("icons", "file_hover.png"))
        self._file_pixmap = self._file_pixmap.scaled(20,20,QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

    def paint(self, painter, option, index):
        _entity_data = index.data()
        _entity_handle = zfused_api.library.LibraryEntity(_entity_data.get("Id"))
        # _name = _entity_handle.name_code().replace("/","_")
        # _id = _entity_handle.id()

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        _rect = option.rect

        _pen = QtGui.QPen(QtGui.QColor("#007acc"), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor(self._background_color))
        painter.drawRoundedRect(_rect, 0, 0)

        # painter thumbnail
        _thumbnail_rect = QtCore.QRectF( _rect.x(), 
                                        _rect.y(), 
                                        _rect.width(), 
                                        constants.Constants.THUMBNAIL_HEIGHT)        
        _pixmap = _pixmap = cache.ThumbnailCache.get_pixmap(_entity_handle, self.parent().parent().update)
        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize( _rect.width(),
                                            constants.Constants.THUMBNAIL_HEIGHT )
                scale = max(float(_label_size.width() / float(_pixmap_size.width())),
                            float(_label_size.height()) / float(_pixmap_size.height()))
                _pixmap = _pixmap.scaled( _pixmap_size.width() * scale, 
                                          _pixmap_size.height() * scale )
                                        #   QtCore.Qt.KeepAspectRatio, 
                                        #   QtCore.Qt.SmoothTransformation )
                _thumbnail_pixmap = _pixmap.copy( (_pixmap_size.width() * scale - _label_size.width()) / 2.0, 
                                                  (_pixmap_size.height() * scale - _label_size.height()) / 2.0, 
                                                  _label_size.width(), 
                                                  _label_size.height() )
            painter.drawPixmap(_rect.x(), _rect.y(), _thumbnail_pixmap)
        else:
            painter.setBrush(QtGui.QColor(color.LetterColor.color(_entity_handle.code().lower()[0])))
            painter.setPen(QtGui.QColor(0, 0, 0, 0))
            painter.drawRoundedRect(_thumbnail_rect, 0, 0)

        path = QtGui.QPainterPath()
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1))
        path.addRect(_thumbnail_rect)
        path.addRoundedRect(_thumbnail_rect, 0, 0)
        painter.setBrush(QtGui.QColor(self._background_color))
        path.setFillRule(QtCore.Qt.OddEvenFill)
        painter.drawPath(path)

        # painter name
        _name_rect = QtCore.QRectF( _rect.x(), 
                                   _rect.y() + constants.Constants.THUMBNAIL_HEIGHT ,
                                   _rect.width(), constants.Constants.INFOMATION_HEIGHT*2 )
        painter.setBrush(QtGui.QColor(constants.Constants.NAME_BACKGROUND_COLOR))
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1))
        painter.drawRoundedRect(_name_rect, 0, 0)
        _font = QtGui.QFont("Microsoft YaHei UI", 12)
        _font.setPixelSize(15)
        _font.setBold(True)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.NAME_COLOR), 1))
        _name = _entity_handle.name().replace("/"," - ")
        _name_rect = QtCore.QRectF( _rect.x() + self._spacing, 
                                   _rect.y() + constants.Constants.THUMBNAIL_HEIGHT ,
                                   _rect.width(), constants.Constants.INFOMATION_HEIGHT )
        painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignBottom, _name)
        _code_rect = QtCore.QRectF( _rect.x() + self._spacing, 
                                   _rect.y() + constants.Constants.THUMBNAIL_HEIGHT + constants.Constants.INFOMATION_HEIGHT ,
                                   _rect.width(), constants.Constants.INFOMATION_HEIGHT )
        _font.setBold(False)
        _font.setPixelSize(12)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.CODE_COLOR), 1))
        _code = _entity_handle.code()
        painter.drawText(_code_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop, _code)

        #  绘制实体类型
        self._font.setPixelSize(12)
        self._font.setBold(True)
        _fm = QtGui.QFontMetrics(self._font)
        painter.setFont(self._font)
        _category_id = _entity_handle.data().get("CategoryId")      
        if _category_id:
            _category_handle = zfused_api.category.Category(_category_id)
            _category_code = _category_handle.name()
            painter.setBrush(QtGui.QColor(_category_handle.color()))
        else:
            _category_code = u"其他"
            painter.setBrush(QtGui.QColor(0, 122, 204, 200))
        _category_rect = QtCore.QRectF( _rect.x() + self._spacing,
                                        _rect.y() + self._spacing,
                                        _fm.width(_category_code) + self._spacing*2,
                                        20 )  
        painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        painter.drawRoundedRect(_category_rect, 2, 2)
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        painter.drawText(_category_rect, QtCore.Qt.AlignCenter, _category_code)

        # 绘制版本数量
        _count = _entity_handle.data().get("Count")
        _count_rect = QtCore.QRectF( _rect.x(),
                                    _rect.y() + _rect.height() - 30,
                                    _rect.width(),
                                    30 )
        painter.setPen(QtGui.QColor(0,0,0,0))
        painter.setBrush(QtGui.QColor("#353535"))
        painter.drawRoundedRect(_count_rect, 0, 0)
        painter.drawPixmap( _count_rect.x() + self._spacing,
                            _count_rect.y() + 5,
                            self._file_pixmap )
        painter.setPen(QtGui.QPen(QtGui.QColor("#DDDDDD"), 1))
        painter.drawText( _count_rect.x() + self._spacing*2 + 20,
                          _count_rect.y(),
                          50,30,
                          QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter,
                          u"{} 文件".format(_count) )

        # _tag_ids = _entity_handle.tag_ids()
        # if _tag_ids:
        #     _tag_x = _rect.x() + constants.Constants.TAG_SPACING
        #     for _tag_id in _tag_ids:
        #         _tag_handle = zfused_api.tag.Tag(_tag_id)
        #         _tag_name_code = _tag_handle.name_code()
        #         _tag_color = _tag_handle.color()
        #         _width = _fm.width(_tag_name_code) + constants.Constants.TAG_SPACING
        #         _tag_rect = QtCore.QRectF( _tag_x,
        #                                   _code_rect.y() + _code_rect.height() + constants.Constants.TAG_SPACING,
        #                                   _width,
        #                                   constants.Constants.TAG_HEIGHT - constants.Constants.TAG_SPACING*2 )
        #         if _tag_x + _width - _rect.x() > _rect.width():
        #             break
        #         painter.setBrush(QtGui.QColor(_tag_color))
        #         painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        #         painter.drawRoundedRect(_tag_rect, 2, 2)
        #         painter.setPen(QtGui.QColor("#ebedef"))
        #         painter.drawText(_tag_rect, QtCore.Qt.AlignCenter, _tag_name_code)
        #         _tag_x += (_fm.width(_tag_name_code) + constants.Constants.TAG_SPACING*2)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.setPen(QtGui.QColor(0, 122, 204, 0))
            painter.setBrush(QtGui.QColor(0, 122, 204, 30))
            painter.drawRect(_rect)
        elif option.state & QtWidgets.QStyle.State_Selected:
            painter.setPen(QtGui.QColor(0, 122, 204, 0))
            painter.setBrush(QtGui.QColor(0, 122, 204, 50))
            painter.drawRect(_rect)
        else:
            painter.setPen(QtGui.QColor(255, 255, 255, 0))
            painter.setBrush(QtGui.QColor(200, 200, 200, 0))
            painter.drawRect(_rect)
        
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(constants.Constants.ITEM_DELEGATE_SIZE[0], constants.Constants.ITEM_DELEGATE_SIZE[1])
