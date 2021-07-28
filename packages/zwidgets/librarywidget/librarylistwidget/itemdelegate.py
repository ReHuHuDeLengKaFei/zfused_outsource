# coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language,cache

from . import constants

__all__ = ["ItemDelegate"]

logger = logging.getLogger(__name__)

# THUMBNAIL_SIZE = [96,54]
THUMBNAIL_SIZE = [80,45]


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent = None, edit = False):
        self._edit = edit
        super(ItemDelegate, self).__init__(parent)

        self._spacing = 8

        self._background_color = parent.palette().color(parent.backgroundRole())

    def _update_index(self, index):
        self.parent().update()

    def paint(self, painter, option, index):
        """ paint name

        """
        _data = index.data(0)
        if isinstance(_data, list):
            _data = zfused_api.objects.Objects(_data[0], _data[1])
        _rect = option.rect
        _rect = QtCore.QRectF( _rect.x(),
                              _rect.y(),
                              _rect.width(),
                              _rect.height() - constants.INTERSTICE)
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # draw background color
        # painter.setPen(QtGui.QPen(QtGui.QColor(60, 60, 60, 0), 0))
        # painter.setBrush(QtGui.QBrush(QtGui.QColor(constants.SELECT_BACKGROUND_COLOR)))
        # painter.drawRect(option.rect)
        # painter.setBrush(QtGui.QBrush(QtGui.QColor(constants.BACKGROUND_COLOR)))
        # painter.drawRect(_rect)

        if option.rect.contains(constants.MousePoint.pos):
            if option.state & QtWidgets.QStyle.State_Selected:
                _rect = QtCore.QRectF( _rect.x(),
                                     _rect.y(), 
                                     _rect.width() - constants.DELEGATE_HEIGHT/2.0, 
                                     _rect.height())

        # draw thumbnail
        _thumbnail_rect = QtCore.QRectF( _rect.x() + self._spacing,
                                        _rect.y() + (_rect.height() - THUMBNAIL_SIZE[1])/2,
                                        THUMBNAIL_SIZE[0],
                                        THUMBNAIL_SIZE[1] )

        _pixmap = cache.ThumbnailCache.get_pixmap( _data, self.parent().update )
        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize(_thumbnail_rect.width(),_thumbnail_rect.height())
                scale = max(float(_label_size.width() / float(_pixmap_size.width())),
                            float(_label_size.height()) / float(_pixmap_size.height()))
                _pixmap = _pixmap.scaled( _pixmap_size.width() * scale, 
                                            _pixmap_size.height() * scale,
                                            QtCore.Qt.KeepAspectRatio, 
                                            QtCore.Qt.SmoothTransformation )
                _thumbnail_pixmap = _pixmap.copy((_pixmap_size.width() * scale - _label_size.width()) / 2.0, 
                                                    (_pixmap_size.height() * scale - _label_size.height()) / 2.0, 
                                                    _label_size.width(), 
                                                    _label_size.height())
        else:
            _thumbnail_pixmap = None                        
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0.2, QtCore.Qt.DashLine))
        if _thumbnail_pixmap:
            painter.drawPixmap(_thumbnail_rect.x(), _thumbnail_rect.y(), _thumbnail_pixmap)
            path = QtGui.QPainterPath()
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1))
            path.addRect(_thumbnail_rect)
            path.addRoundedRect(_thumbnail_rect, 4, 4) #addEllipse(_rect)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(self._background_color)))
            path.setFillRule(QtCore.Qt.OddEvenFill)
            painter.drawPath(path)
        else:
            painter.setBrush(QtGui.QBrush(QtGui.QColor(_data.color())))
            painter.drawRoundedRect(_thumbnail_rect, 4, 4)

        _font = painter.font()
        #_font = QtGui.QFont("Microsoft YaHei UI")
        _font.setPixelSize(16)
        _font.setBold(True)
        painter.setPen(QtCore.Qt.DashDotLine)
        painter.setFont(_font)
        painter.setPen(QtGui.QColor(_data.color()))
        _name = _data.name()
        _name_rect = QtCore.QRectF( _rect.x() + THUMBNAIL_SIZE[0] + self._spacing*2,
                                   _rect.y(),
                                   _rect.width() - THUMBNAIL_SIZE[0] - self._spacing,
                                   _rect.height()/2)
        painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignBottom, _name)
        _font.setPixelSize(14)
        _font.setBold(False)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor("#888888"), 1, QtCore.Qt.SolidLine))
        _code = _data.code()
        _code_rect = QtCore.QRectF( _name_rect.x(),
                                   _rect.y() + _rect.height()/2,
                                   _name_rect.width(),
                                   _rect.height()/2)
        painter.drawText(_code_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop, _code)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            bgBrush = QtGui.QBrush(QtGui.QColor(200, 200, 200, 150))
            bgPen = QtGui.QPen(QtGui.QColor(60, 60, 60, 0), 0)
            painter.setPen(bgPen)
            painter.setBrush(bgBrush)
            painter.drawRect(option.rect)
        elif option.state & QtWidgets.QStyle.State_Selected:
            bgBrush = QtGui.QBrush(QtGui.QColor(149, 194, 197, 150))
            bgPen = QtGui.QPen(QtGui.QColor(160, 60, 60, 0), 0)
            painter.setPen(bgPen)
            painter.setBrush(bgBrush)
            painter.drawRect(option.rect)
        else:
            bgBrush = QtGui.QBrush(QtGui.QColor(200, 200, 200, 0))
            bgPen = QtGui.QPen(QtGui.QColor(160, 60, 60, 0), 0)
            painter.setPen(bgPen)
            painter.setBrush(bgBrush)
            painter.drawRect(option.rect)
            
        painter.restore()
        # # draw icon


    def sizeHint(self, option, index):
        return QtCore.QSize(130,constants.DELEGATE_HEIGHT)
