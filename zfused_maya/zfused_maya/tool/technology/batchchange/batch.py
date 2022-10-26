# -*- coding: UTF-8 -*-
"""
@Time    : 2022/10/20 14:20
@Author  : Jerris_Cheng
@File    : batch.py
@Description:
"""
from __future__ import print_function

from PySide2 import QtWidgets

from cores import cores
reload(cores)
from zfused_maya.core import record
from .widget import filtratewidget, project_step_widget, task_list,tool_widget
from zfused_maya.ui.widgets import window
reload(task_list)
reload(project_step_widget)

reload(filtratewidget)


class Batch(window._Window):
    def __init__(self):
        super(Batch, self).__init__()
        self._init()
        self._build()
        self.project_step_frame.project_step_id_signal.connect(self.update_project_step_id)
        self.project_step_frame.project_step_type_signal.connect(self.update_project_step_type)
        self.filtratewidget.filtrate_signal.connect(self.update_filtrate_str)
        self.localepathwidget.local_path_signal.connect(self.update_local_path)
        self.toolwidget.execute_script_signal.connect(self.update_execute_script)



    def _build(self):
        self.basewidget = QtWidgets.QFrame()
        self.baselayout = QtWidgets.QHBoxLayout(self.basewidget)
        self.left_widget = QtWidgets.QWidget()
        self.left_layout = QtWidgets.QVBoxLayout(self.left_widget)

        self.project_step_frame = project_step_widget.ProjectStepWidget(self.current_project_id)
        self.left_layout.addWidget(self.project_step_frame)
        self.baselayout.addWidget(self.left_widget)

        self.right_widget = QtWidgets.QWidget()
        self.right_layout = QtWidgets.QVBoxLayout(self.right_widget)
        self.filtratewidget = filtratewidget.FiltrateWidget()
        self.right_layout.addWidget(self.filtratewidget)
        self.localepathwidget =filtratewidget.LocalPathWidget()
        self.right_layout.addWidget(self.localepathwidget)
        self.toolwidget = tool_widget.ToolWidget()
        self.right_layout.addWidget(self.toolwidget)

        self.right_down_widget = QtWidgets.QWidget()
        self.right_down_layout = QtWidgets.QHBoxLayout(self.right_down_widget)
        self.task_list_widget = task_list.TaskListWidget(self.filtrate_str, self.current_project_id,
                                                         self.current_company_id, self.project_step_id, 'shot',
                                                         self.output_attr_id,self.locale_path)

        self.right_down_layout.addWidget(self.task_list_widget)
        self.right_down2_widget = QtWidgets.QWidget()
        self.right_down2_layout = QtWidgets.QHBoxLayout(self.right_down2_widget)
        self.check_btn = QtWidgets.QPushButton(u'检查文件')
        self.right_down2_layout.addWidget(self.check_btn)
        self.check_btn.clicked.connect(self.check)
        self.publish_btn = QtWidgets.QPushButton(u'发布')
        self.publish_btn.clicked.connect(self._publish_files)
        self.right_down2_layout.addWidget(self.publish_btn)

        self.right_layout.addWidget(self.right_down_widget)
        self.right_layout.addWidget(self.right_down2_widget)
        self.baselayout.addWidget(self.right_widget)

        self.set_central_widget(self.basewidget)


    def _init(self):
        self.current_project_id = record.current_project_id()
        self.current_company_id = record.current_company_id()
        self.filtrate_str = ''
        self.project_step_id = 0
        self.project_entity_type = 'shot'
        self.output_attr_id = cores.output_attr_id(self.project_step_id)
        self.locale_path = ''
        self.execute_script = ''

    def update_project_step_id(self, int):
        #print(int)
        self.project_step_id = int
        self.output_attr_id = cores.output_attr_id(int)
        self.update_task_list()

    def update_filtrate_str(self, str):
        self.filtrate_str = str
        self.update_task_list()

    def update_project_step_type(self,str):
        self.project_entity_type = str
        self.update_task_list()


    def update_task_list(self):
        self.clear_widget()
        self.task_list_widget = task_list.TaskListWidget(self.filtrate_str, self.current_project_id,
                                                         self.current_company_id, self.project_step_id, self.project_entity_type,
                                                         self.output_attr_id,self.locale_path)
        self.right_down_layout.addWidget(self.task_list_widget)
        #task_list_widget.checks()

    def update_local_path(self,str):
        self.locale_path = str
        #self.update_task_list()

    def update_execute_script(self,str):
        self.execute_script = str
    def clear_widget(self):
        for i in range(self.right_down_layout.count()):
            self.right_down_layout.itemAt(i).widget().deleteLater()
        pass

    def check(self):
        self.task_list_widget.checks(self.locale_path)

    def _publish_files(self):
        all_widget = self.task_list_widget.findChildren(task_list.TaskItem)
        for _widegt in all_widget:
            if _widegt.locale_state():
                _cache = _widegt.cache
                args = _cache.get('args')
                kwargs =_cache.get('kwargs')
                _path = _widegt.locale_file()
                kwargs['file'] = _path
                exec(self.execute_script)






