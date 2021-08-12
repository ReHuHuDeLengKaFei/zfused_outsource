# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from . import constants


class InputItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent = None):
        super(InputItemDelegate, self).__init__(parent)

        self._spacing = 2
        self._extend_width = 10

    def _paint_task(self, task_id, painter, task_rect):
        _task_handle = zfused_api.task.Task(task_id)
        _rect = task_rect
        #  绘制任务名
        _font = QtGui.QFont("Microsoft YaHei UI", 9)
        _font.setPixelSize(12)
        _font.setBold(True)
        _fm = QtGui.QFontMetrics(_font)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.TASK_TEXT_COLOR), 1))
        _name_code = _task_handle.data()["Name"]
        _name_rect = QtCore.QRectF( _rect.x() + self._spacing,
                                   _rect.y(),
                                   _rect.width() - self._spacing*2,
                                   constants.TASK_HEIGHT )
        painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _name_code)

        #  绘制任务状态
        _status_handle = zfused_api.status.Status(_task_handle.data()["StatusId"])
        _status_code = _status_handle.name_code()
        _status_rect = QtCore.QRectF(
                _rect.x() + _rect.width() - _fm.width(_status_code) - self._extend_width -self._spacing,
                _name_rect.y() + self._spacing,
                _fm.width(_status_code) + self._extend_width,
                20 - self._spacing*2
            )
        painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        painter.setBrush(QtGui.QColor(_status_handle.data()["Color"]))
        painter.drawRoundedRect(_status_rect, 2, 2)
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        painter.drawText(_status_rect, QtCore.Qt.AlignCenter, _status_code)


        # 绘制link
        _link_handle = zfused_api.objects.Objects(_task_handle.data()["Object"], _task_handle.data()["LinkId"])
        if _task_handle.data()["Object"] == "asset":
            _link_full_name = _link_handle.full_name()
        else:
            _link_full_name = _link_handle.full_code()
        _link_rect = QtCore.QRectF(
                _name_rect.x(),
                _name_rect.y() + _name_rect.height() + self._spacing,
                _fm.width(_link_full_name),
                20
            )
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.TASK_TEXT_COLOR), 1))
        painter.drawText(_link_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _link_full_name)
        
        #  绘制任务步骤
        _project_step_handle = zfused_api.step.ProjectStep(_task_handle.data()["ProjectStepId"])
        _step_handle = zfused_api.step.Step(_task_handle.data()["StepId"])
        _step_code = _project_step_handle.name_code()
        _step_rect = QtCore.QRectF(
                _link_rect.x() + _link_rect.width() + self._extend_width,
                _link_rect.y() + self._spacing,
                _fm.width(_step_code) + self._extend_width,
                20 - self._spacing*2
            )
        painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        painter.setBrush(QtGui.QColor(_step_handle.data()["Color"]))
        painter.drawRoundedRect(_step_rect, 2, 2)
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        painter.drawText(_step_rect, QtCore.Qt.AlignCenter, _step_code)

        # 绘制文件
        _versions = _task_handle.versions()
        painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        if _versions:
            painter.setBrush(QtGui.QColor("#0078D7"))
            _text = u"第{}版本 · {}".format(_versions[-1]["Index"], _versions[-1]["Description"])
        else:
            painter.setBrush(QtGui.QColor("#FF0000"))
            _text = u"无版本文件"
        _approval_rect = QtCore.QRectF( _link_rect.x(), 
                                       _link_rect.y() + _link_rect.height() + self._spacing,
                                       _fm.width(_text) + self._spacing*2, 
                                       20 )
        painter.drawRect(_approval_rect)
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        painter.drawText(_approval_rect, QtCore.Qt.AlignCenter, _text) 

    def _paint_input_attr(self, input_attr_id, painter, input_attr_rect):
        #
        _input_attr_handle = zfused_api.inputattr.InputAttr(input_attr_id)
        _rect = input_attr_rect
        painter.setBrush(QtGui.QColor(0,0,0))
        painter.drawRoundedRect(_rect, 0, 0)

        _font = QtGui.QFont("Microsoft YaHei UI", 9)
        _font.setPixelSize(14)
        _font.setBold(True)
        _fm = QtGui.QFontMetrics(_font)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.TASK_TEXT_COLOR), 1))
        _name_code = _input_attr_handle.data()["Name"]
        _name_rect = QtCore.QRectF( _rect.x() + self._spacing,
                                   _rect.y(),
                                   _rect.width() - self._spacing*2,
                                   _rect.height() )
        painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _name_code)


    def paint(self, painter, option, index):
            
        _rect = option.rect

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        _rect = option.rect
        _pen = QtGui.QPen(QtGui.QColor(constants.TASK_TEXT_COLOR), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor(constants.BACKGROUND_COLOR))
        painter.drawRoundedRect(option.rect, 0, 0)

        _data = index.data()
        if isinstance(_data, int):
            # is input attr id
            self._paint_input_attr(_data, painter, _rect)
        elif isinstance(_data, dict):
            # is task
            _task_rect = QtCore.QRectF( _rect.x() + 40,
                                       _rect.y(),
                                       _rect.width() - 40,
                                       _rect.height() )
            self._paint_task(_data["Id"], painter, _task_rect)

        # draw task name
        #_task_name_rect = QtCore.QRectF( _rect.x(),
        #                                _rect.y(),
        #                                _rect.width(),
        #                                constants.TASK_HEIGHT )
        #painter.drawText(_task_name_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, _task_handle.full_name())

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

    def sizeHint(self, option, index):
        """ item size

        :rtype: QtCore.QSize
        """
        _data = index.data()
        if isinstance(_data, int):
            return QtCore.QSize(option.rect.width(), constants.ITEM_HEIGHT/2.0)
        elif isinstance(_data, dict):
            return QtCore.QSize(option.rect.width(), constants.ITEM_HEIGHT)