# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import cache,color,filefunc

from . import constants

__all__ = ["ItemDelegate"]

logger = logging.getLogger(__name__)


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    THUMBNAIL_PIXMAP = {}
    THUMBNAIL = {}

    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)
        _ThumbnailThread.exec_ = False

        self._last_version_dict = {}

        self._replace_project_step_id = 0

    @property
    def replace_project_step_id(self):
        return self._replace_project_step_id

    @replace_project_step_id.setter
    def replace_project_step_id(self, replace_project_step_id):
        self._replace_project_step_id = replace_project_step_id

    def refresh(self):
        self._last_version_dict = {}

    def __del__(self):
        _ThumbnailThread.exec_ = True

    def paint(self, painter, option, index):
        """ paint 
        """
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        _pen = QtGui.QPen(QtGui.QColor("#343D46"), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor(constants.Constants.BACKGROUND_COLOR))
        painter.drawRect(option.rect)

        _rect = option.rect

        _data = index.data()
        _object = _data["link_object"]
        _object_id = _data["link_id"]
        _object_handle = zfused_api.objects.Objects(_object, _object_id)
        # painter thumbnail
        # _thumbnail_pixmap = None
        # if self.THUMBNAIL_PIXMAP.has_key(_object_id):
        #     _thumbnail_pixmap = self.THUMBNAIL_PIXMAP[_object_id]
        # else:
        #     if self.THUMBNAIL.has_key(_object_id):
        #         _thumbnail = self.THUMBNAIL[_object_id]
        #         if _thumbnail:
        #             _pixmap = QtGui.QPixmap(_thumbnail)
        #             #_pixmap = QtGui.QImageReader(_thumbnail)
        #             _pixmap_size = _pixmap.size()
        #             if _pixmap_size.width() and _pixmap_size.height():
        #                 _label_size = QtCore.QSize( constants.Constants.THUMBNAIL_WIDTH, 
        #                                             constants.Constants.THUMBNAIL_HEIGHT)
        #                 scale = max(float(_label_size.width() / float(_pixmap_size.width())),
        #                             float(_label_size.height()) / float(_pixmap_size.height()))
        #                 _pixmap = _pixmap.scaled(
        #                     _pixmap_size.width() * scale, _pixmap_size.height() * scale)
        #                 #_pixmap = _pixmap.setScaledSize(QtCore.QSize(_pixmap_size.width()*scale, _pixmap_size.height()*scale))
        #                 _thumbnail_pixmap = _pixmap.copy((_pixmap_size.width() * scale - _label_size.width()) / 2.0, (_pixmap_size.height(
        #                 ) * scale - _label_size.height()) / 2.0, _label_size.width(), _label_size.height())
        #                 #_thumbnail_pixmap = _pixmap
        #                 self.THUMBNAIL_PIXMAP[_object_id] = _thumbnail_pixmap
        #     else:
        #         _thumbnail_load = _ThumbnailThread(self)
        #         _thumbnail_load.load_thumbnail(_object_handle, index)

        _pixmap = cache.ThumbnailCache.get_pixmap(_object_handle,  self.parent().parent().update )# partial(self._update, index))

        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize( constants.Constants.THUMBNAIL_WIDTH, 
                                            constants.Constants.THUMBNAIL_HEIGHT)
                scale = max(float(_label_size.width() / float(_pixmap_size.width())),
                            float(_label_size.height()) / float(_pixmap_size.height()))
                _pixmap = _pixmap.scaled( _pixmap_size.width() * scale, 
                                          _pixmap_size.height() * scale,
                                          QtCore.Qt.IgnoreAspectRatio, 
                                          QtCore.Qt.SmoothTransformation )
                _thumbnail_pixmap = _pixmap.copy( (_pixmap_size.width() * scale - _label_size.width()) / 2.0, 
                                                  (_pixmap_size.height() * scale - _label_size.height()) / 2.0, 
                                                  _label_size.width(), 
                                                  _label_size.height() )
                painter.drawPixmap(_rect.x(), _rect.y(), _thumbnail_pixmap)
        else:
            _thumbnail_rect = QtCore.QRect( _rect.x(), 
                                            _rect.y(), 
                                            constants.Constants.THUMBNAIL_WIDTH, 
                                            constants.Constants.THUMBNAIL_HEIGHT - 1)
            painter.setBrush(QtGui.QColor(color.LetterColor.color(_object_handle.data()["Code"].lower()[0])))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)
            painter.setPen(QtGui.QPen(QtGui.QColor(
                0, 0, 0, 255), 0.2, QtCore.Qt.DashLine))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)


        # painter name
        _name_rect = QtCore.QRect(_rect.x() + constants.Constants.THUMBNAIL_WIDTH + 20, 
                                  _rect.y(),
                                  _rect.width() - constants.Constants.THUMBNAIL_WIDTH - 20, 
                                  20)
        #painter.setBrush(QtGui.QColor(constants.Constants.NAME_BACKGROUND_COLOR))
        #painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1))
        #painter.drawRoundedRect(_name_rect, 0, 0)
        _font = QtGui.QFont("Microsoft YaHei UI", 9)
        _font.setPixelSize(constants.Constants.FONT_SIZE)
        #_font.setBold(True)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.NAME_COLOR), 1))
        _name_code = _object_handle.name_code()
        painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _name_code)


        _project_step_rect = QtCore.QRect( _name_rect.x(), 
                                           _name_rect.y() + _name_rect.height(),
                                           _rect.width(),
                                           20)
        # painter project step 
        _project_step_id = _data["project_step_id"]
        _project_step_handle = zfused_api.step.ProjectStep(_project_step_id)
        _project_step_name_code = _project_step_handle.name_code()
        _color = _project_step_handle.color()
        painter.setPen(QtGui.QPen(QtGui.QColor(_color), 1))
        painter.drawText(_project_step_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _project_step_name_code)

        # painter replace project step
        if self._replace_project_step_id:
            _entity_type = _data["link_object"]
            _entity_id = _data["link_id"]
            # _data_handle = zfused_api.asset.Asset(data["Id"])
            _data_handle = zfused_api.objects.Objects(_entity_type,_entity_id)
            _tasks = _data_handle.tasks([self._replace_project_step_id])
            if _tasks:
                for _task in _tasks:
                    _task_handle = zfused_api.task.Task(_task["Id"])
                    _versions = _task_handle.versions()
                    if _versions:
                        _replace_project_step_rect = QtCore.QRect( _name_rect.x(), 
                                                                   _name_rect.y() + _name_rect.height(),
                                                                   _name_rect.width(),
                                                                   20)
                        _project_step_handle = zfused_api.step.ProjectStep( self._replace_project_step_id )
                        _project_step_name_code = _project_step_handle.name_code()
                        _color = _project_step_handle.color()
                        painter.setPen(QtGui.QPen(QtGui.QColor(_color), 1))
                        painter.drawText(_replace_project_step_rect, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter, _project_step_name_code)


        # painter new version
        _task_id = _data["task_id"]
        _task_handle = zfused_api.task.Task(_task_id)
        if _task_id in self._last_version_dict:
            _last_version_id = self._last_version_dict[_task_id]
        else:
            _last_version_id = _task_handle.last_version_id()
            self._last_version_dict[_task_id] = _last_version_id
        _last_version_handle = zfused_api.version.Version(_last_version_id) 
        _last_version_index = _last_version_handle.data()["Index"]
        # painter is approval
        _approval_rect = QtCore.QRect( _name_rect.x(), 
                                       _name_rect.y() + _name_rect.height() + _name_rect.height(),
                                       80, 
                                       20 )
        _version_data = _last_version_handle.data()
        if _version_data["IsApproval"] == 1:
            painter.setBrush(QtGui.QColor("#0078D7"))
            _approval_text = u"审批通过"
        elif _version_data["IsApproval"] == 0:
            painter.setBrush(QtGui.QColor("#F7B55E"))
            _approval_text = u"未审批"
        else:
            painter.setBrush(QtGui.QColor("#FF0000"))
            _approval_text = u"审批未通过"
            painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        painter.drawRect(_approval_rect)
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        painter.drawText(_approval_rect, QtCore.Qt.AlignCenter, _approval_text)

        _new_version_rect = QtCore.QRect( _name_rect.x() + 100, 
                                          _name_rect.y() + _name_rect.height() + _name_rect.height(),
                                          _rect.width(),
                                          20 )
        painter.setPen(QtGui.QPen(QtGui.QColor("#AAAAAA"), 1))
        _last_version_str = u"最新版本 · {}".format(_last_version_index)
        painter.drawText(_new_version_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _last_version_str)

        # painter current version
        _current_version = _data["version"]
        if _current_version != _last_version_index:
            # painter red color
            painter.setPen(QtGui.QPen(QtGui.QColor("#FF2200"), 1))
            _current_version_stt = u"当前版本 · {} <不是最新版本>".format(_current_version)
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor("#4A9BFA"), 1))
            _current_version_stt = u"当前为最新版本 · {}".format(_current_version)
        _current_version_rect = QtCore.QRect( _name_rect.x(), 
                                          _name_rect.y() + _name_rect.height()*3,
                                          _rect.width(),
                                          20 ) 
        painter.drawText(_current_version_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _current_version_stt)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            bgBrush = QtGui.QBrush(QtGui.QColor(200, 200, 200, 50))
            bgPen = QtGui.QPen(QtGui.QColor(60, 60, 60, 0), 0)
            painter.setPen(bgPen)
            painter.setBrush(bgBrush)
            painter.drawRect(option.rect)
        elif option.state & QtWidgets.QStyle.State_Selected:
            bgBrush = QtGui.QBrush(QtGui.QColor(149, 194, 197, 50))
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

    def sizeHint(self, option, index):
        return QtCore.QSize(constants.Constants.ITEM_DELEGATE_SIZE[0], constants.Constants.ITEM_DELEGATE_SIZE[1])




class _ThumbnailThread(QtCore.QThread):
    exec_ = False
    def __init__(self, parent = None):
        super(_ThumbnailThread, self).__init__(parent)

        self._parent = parent
        self._handle = None

    def load_thumbnail(self, handle, index):
        #self.num = 0
        self._handle = handle
        self._index = index
        self.start()

    def run(self):
        self.msleep(1)
        self._parent.THUMBNAIL[self._handle.data()["Id"]] = None
        if self._handle.data:
            _thumbnail_name = self._handle.thumbnail()
            _production_thumbnail = "{}/{}".format(self._handle.production_path(), _thumbnail_name)
            _work_thumbnail = "{}/{}".format(self._handle.work_path(), _thumbnail_name)
            
            _v = filefunc.receive_file(_production_thumbnail, _work_thumbnail)
            if _v:
                _thumbnail = _work_thumbnail
            else:
                _thumbnail = ""
            _thumbnail = _work_thumbnail
            if not _ThumbnailThread.exec_:
                self._parent.THUMBNAIL[self._handle.data()["Id"]] = _thumbnail
                if _thumbnail:
                    self._parent.parent().update(self._index)
        self.quit()