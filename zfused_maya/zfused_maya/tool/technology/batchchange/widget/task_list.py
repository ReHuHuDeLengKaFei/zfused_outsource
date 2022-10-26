# -*- coding: UTF-8 -*-
"""
@Time    : 2022/10/17 16:39
@Author  : Jerris_Cheng
@File    : task_list.py
@Description:
"""

from __future__ import print_function

import os

from PySide2 import QtCore, QtWidgets,QtGui

import zfused_api
from zfused_maya.core import record

import time
class TaskListWidget(QtWidgets.QFrame):
    def __init__(self, filtrate_str, project_id,company_id,project_step_id,project_entity_type, _output_attr_id,check_path):
        super(TaskListWidget, self).__init__()
        self.filtrate_str = filtrate_str
        self.setFixedWidth(1160)
        self.current_company_id = company_id
        self.project_id = project_id
        self._output_attr_id = _output_attr_id
        self.project_step_id = project_step_id
        self.project_entity_type = project_entity_type
        self.check_path =check_path
        self._init()
        self._build()

    def _build(self):
        self._ground_layout = QtWidgets.QVBoxLayout(self)
        self.task_list_area = QtWidgets.QScrollArea()
        self.task_widget = QtWidgets.QFrame()
        self.task_layout = QtWidgets.QVBoxLayout(self.task_widget)
        self._ground_layout.addWidget(self.task_list_area)

        start_time = time.clock()
        for _index, _task in enumerate(self.tasks):
            task_id = _task.get('Id')
            task_name = _task.get('Name')
            _item = TaskItem(_index, task_id, task_name, self._output_attr_id,self.check_path)
            self.task_layout.addWidget(_item)

        self.task_list_area.setWidget(self.task_widget)

        end_time = time.clock()

        print('Running time: %s Seconds' % (end_time - start_time))

    def _init(self):

        self.tasks = zfused_api.zFused.get('task', filter={
            'ProjectId': self.project_id,
            'IsOutsource': self.current_company_id,
            'ProjectStepId': self.project_step_id,
            'ProjectEntityType':self.project_entity_type,
            'Name__icontains': self.filtrate_str})

    def checks(self,local_path):
        self.update()
        all_item = self.findChildren(TaskItem)
        max = self.task_list_area.verticalScrollBar().maximum()
        for _index,_item in enumerate(all_item):
            try:
                _value = max * _index / len(all_item)
                self.task_list_area.verticalScrollBar().setValue(_value)

                _item._check_file(local_path)
                QtWidgets.QApplication.processEvents()
            except Exception as e:
                print(e)

                break




class TaskItem(QtWidgets.QFrame):
    def __init__(self, _index, task_Id, task_Name, _output_attr_id, dir_path):
        super(TaskItem, self).__init__()
        self._output_attr_id = _output_attr_id
        self._index = _index
        self._task_name = task_Name
        self._task_id = task_Id
        self._dir_path = dir_path
        self.cache = {
            'args':[self._task_id,self._output_attr_id],
            'kwargs':{'file':""}
        }
        self._init()
        self._build()

    def _init(self):
        self.font_size = '20px'
        self.font_no = QtGui.QFont('times',14,QtGui.QFont.Black)
        self._locale_statue = False
        self._locale_path = ''

        # _no_image = os.path.join(_image_path, 'no.png')
        # _yes_image = os.path.join(_image_path, 'yes.png')
        # self.no_pix = QtGui.QPixmap(_no_image)
        # self.yes_pix = QtGui.QPixmap(_yes_image)


    def _build(self):
        self.ground_layout = QtWidgets.QHBoxLayout(self)
        self.setFixedHeight(50)
        self.setFixedWidth(1100)
        self._index_label = QtWidgets.QLabel()
        self._index_label.setText(str(self._index))
        self._index_label.setFixedWidth(30)
        self._index_label.setAlignment(QtCore.Qt.AlignCenter)
        #self._index_label.setStyleSheet('QLabel{font-size:%s}' % self.font_size)
        self._task_name_label = QtWidgets.QLabel()
        self._task_name_label.setText(self._task_name)
        self._task_name_label.setFixedWidth(300)
        self._task_name_label.setStyleSheet(
            'QLabel{color:MidnightBlue;font-size:%s;background:Azure;border-radius: 5px; border: 1px groove gray;border-style: outset;}' % self.font_size)
        self._task_name_label.setAlignment(QtCore.Qt.AlignCenter)

        # self._task_name_label.setObjectName(str(self._index))
        self.server_label = QtWidgets.QLabel()
        self.server_label.setText(u'服务器文件')
        self.server_label.setFixedWidth(300)
        self.server_label.setStyleSheet('QLabel{color:MidnightBlue;font-size:%s;background:Azure;border-radius: 5px; border: 1px groove gray;border-style: outset;}' % self.font_size)

        self.locale_label = QtWidgets.QLabel()
        self.locale_label.setText(u'指定路径文件')
        self.locale_label.setStyleSheet('QLabel{color:MidnightBlue;font-size:%s;background:Azure;border-radius: 5px; border: 1px groove gray;border-style: outset;}' % self.font_size)
        self.locale_label.setFixedWidth(300)
        self.ground_layout.addWidget(self._index_label)
        self.ground_layout.addWidget(self._task_name_label)
        self.ground_layout.addWidget(self.server_label)
        self.ground_layout.addWidget(self.locale_label)
        #self._check_file()

    def sever_path(self):
        _output_attr_handle = zfused_api.attr.Output(self._output_attr_id)
        _file_format = _output_attr_handle.format()
        _suffix = _output_attr_handle.suffix()
        _attr_code = _output_attr_handle.code()
        _task = zfused_api.task.Task(self._task_id)
        _production_path = _task.production_path()
        _file_code = _task.file_code()
        _cover_file = "{}/{}/{}{}".format(_production_path, _attr_code, _file_code, _suffix)


        if not os.path.exists(_cover_file):
            return False
        return True

    def locale_path(self,local_path):

        _output_attr_handle = zfused_api.attr.Output(self._output_attr_id)
        _file_format = _output_attr_handle.format()
        _suffix = _output_attr_handle.suffix()
        _attr_code = _output_attr_handle.code()
        _task = zfused_api.task.Task(self._task_id)
        _production_path = _task.production_path()
        _file_code = _task.file_code()
        _locale_file = "{}/{}{}".format(local_path, _file_code, _suffix)
        self._locale_path = _locale_file
        if not os.path.exists(_locale_file):
            return False
        return True

    def _check_file(self,local_path):

        if not self.locale_path(local_path):

            self.locale_label.setStyleSheet(
                'QLabel{color:MidnightBlue;MidnightBlue;background:Salmon;font-size :%s;border-radius: 5px; border: 1px groove gray;border-style: outset;}' % self.font_size)
            #self.locale_label.setStyleSheet('QLabel{color:MidnightBlue;MidnightBlue;background:red;font-size :%s;}' % self.font_size)

        else:
            self._locale_statue =True
            self.locale_label.setStyleSheet(
                'QLabel{color:MidnightBlue;background:Ivory;font-size :%s;border-radius: 5px; border: 1px groove gray;border-style: outset;}' % self.font_size)

        if not self.sever_path():
            #
            self.server_label.setStyleSheet(
                'QLabel{color:MidnightBlue;background:Salmon;font-size :%s;border-radius: 5px; border: 1px groove gray;border-style: outset;}' % self.font_size)
        else:
            self.server_label.setStyleSheet(
                'QLabel{color:MidnightBlue;background:Ivory;font-size :%s;border-radius: 5px; border: 1px groove gray;border-style: outset;}' % self.font_size)

        # if not self.locale_path():
        #     self.locale_label.setPixmap(self.no_pix)
        # else:
        #     self.locale_label.setPixmap(self.yes_pix)
        #
        # if not self.sever_path():
        #     self.server_label.setPixmap(self.no_pix)
        # else:
        #     self.server_label.setPixmap(self.yes_pix)

    def locale_text(self):
        return self.locale_label.text()
    def sever_text(self):
        return self.server_label.text()

    def locale_state(self):
        return self._locale_statue

    def locale_file(self):
        return self._locale_path