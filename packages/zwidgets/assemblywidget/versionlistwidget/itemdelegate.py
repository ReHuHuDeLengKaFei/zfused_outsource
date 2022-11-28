# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import requests
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import cache,color

from . import constants


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    THUMBNAIL_PIXMAP = {}
    THUMBNAIL = {}

    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        _version_data = index.data()
        _version_id = _version_data["Id"]
        _version_handle = zfused_api.version.Version(_version_id, _version_data)

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        _rect = option.rect

        _font = QtGui.QFont("Microsoft YaHei UI", 9)
        _font.setPixelSize(constants.Constants.FONT_SIZE)
        #_font.setBold(True)
        painter.setFont(_font)
        _pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor("#5C5C5C"))
        painter.drawRoundedRect(option.rect, 0, 0)

        _fm = QtGui.QFontMetrics(painter.font())

        # painter index
        _index_str = "%04d"%(_version_handle.data()["Index"])
        _index_rect = QtCore.QRectF(_rect.x(),
                                   _rect.y(),
                                   _fm.width(_index_str) + constants.Constants.SPACING,
                                   _rect.height()
                                    )
        painter.drawText(_index_rect, QtCore.Qt.AlignCenter, _index_str)

        # painter thumbnail
        _thumbnail_rect = QtCore.QRectF(_index_rect.x() + _index_rect.width() + constants.Constants.SPACING,
                                       _rect.y(),
                                       constants.Constants.THUMBNAIL_SIZE[0],
                                       constants.Constants.THUMBNAIL_SIZE[1])

        _pixmap = cache.ThumbnailCache.get_pixmap(_version_handle, self.parent().parent().update ) # partial(self.parent().update, index))
        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize( constants.Constants.THUMBNAIL_SIZE[0], 
                                            constants.Constants.THUMBNAIL_SIZE[1] )
                scale = max(float(_label_size.width() / float(_pixmap_size.width())),
                            float(_label_size.height()) / float(_pixmap_size.height()))
                _pixmap = _pixmap.scaled( _pixmap_size.width() * scale, 
                                          _pixmap_size.height() * scale,
                                          QtCore.Qt.KeepAspectRatio, 
                                          QtCore.Qt.SmoothTransformation )
                _thumbnail_pixmap = _pixmap.copy( (_pixmap_size.width() * scale - _label_size.width()) / 2.0, 
                                                  (_pixmap_size.height() * scale - _label_size.height()) / 2.0, 
                                                  _label_size.width(), 
                                                  _label_size.height() )
                painter.drawPixmap(_thumbnail_rect.x(), _thumbnail_rect.y(), _thumbnail_pixmap)
        else:
            painter.setBrush(QtGui.QColor(color.LetterColor.color(_version_data["Name"].lower()[0])))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)
            painter.setPen(QtGui.QPen( QtGui.QColor(0, 0, 0, 255), 
                                       0.2, 
                                       QtCore.Qt.DashLine))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)
            
        # painter time
        _pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 0.1)
        painter.setPen(_pen)
        _create_time_text = _version_handle.created_time().strftime("%Y-%m-%d %H:%M:%S")
        _time_rect = QtCore.QRectF(_thumbnail_rect.x() + _thumbnail_rect.width() + constants.Constants.SPACING,
                                  _rect.y(),
                                  _fm.width(_create_time_text) + constants.Constants.SPACING,
                                  _rect.height())
        painter.drawText(_time_rect, QtCore.Qt.AlignCenter, _create_time_text)

        # # painter user
        # _user_id = _version_handle.data()["CreatedBy"]
        # _user_handle = zfused_api.user.User(_user_id)
        # _user_name_text = _user_handle.full_name_code()
        # _name_rect = QtCore.QRectF(_time_rect.x() + _time_rect.width() + constants.Constants.SPACING,
        #                           _rect.y(),
        #                           _fm.width(_user_name_text),
        #                           _rect.height() )
        # painter.drawText(_name_rect, QtCore.Qt.AlignCenter, _user_name_text)

        _name_rect = QtCore.QRectF( _time_rect.x() + _time_rect.width() + constants.Constants.SPACING,
                                    _rect.y(),
                                    0, # _fm.width(_user_name_text),
                                    _rect.height() )

        # painter description
        _description = _version_handle.description()
        _description_rect = QtCore.QRectF(  _name_rect.x() + _name_rect.width() + constants.Constants.SPACING,
                                            _rect.y(),
                                            _fm.width(_description),
                                            _rect.height() )
        painter.drawText(_description_rect, QtCore.Qt.AlignCenter, _description)
        
        # # painter is approval
        # _approval_rect = QtCore.QRectF( _rect.x() + _rect.width() - 100, 
        #                                _rect.y() + 8,
        #                                80, 
        #                                20 )
        # if _version_data["IsApproval"] == 1:
        #     painter.setBrush(QtGui.QColor("#0078D7"))
        #     _approval_text = u"审批通过"
        # elif _version_data["IsApproval"] == 0:
        #     painter.setBrush(QtGui.QColor("#F7B55E"))
        #     _approval_text = u"未审批"
        # else:
        #     painter.setBrush(QtGui.QColor("#FF0000"))
        #     _approval_text = u"审批未通过"
        # painter.drawRect(_approval_rect)
        # painter.drawText(_approval_rect, QtCore.Qt.AlignCenter, _approval_text)

        if option.state & QtWidgets.QStyle.State_Selected:
            bgBrush = QtGui.QBrush(QtGui.QColor(149, 194, 197, 150))
            bgPen = QtGui.QPen(QtGui.QColor(160, 60, 60, 0), 0)
            painter.setPen(bgPen)
            painter.setBrush(bgBrush)
            painter.drawRect(option.rect)
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            bgBrush = QtGui.QBrush(QtGui.QColor(200, 200, 200, 50))
            bgPen = QtGui.QPen(QtGui.QColor(60, 60, 60, 0), 0)
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

    def sizeHint(self, option, index):
        return QtCore.QSize(constants.Constants.ITEM_DELEGATE_SIZE[0], constants.Constants.ITEM_DELEGATE_SIZE[1])
