# -*- coding: UTF-8 -*-
"""
@Time    : 2022/10/19 15:38
@Author  : Jerris_Cheng
@File    : project_step_widget.py
@Description:
"""
from __future__ import print_function

from PySide2 import QtWidgets, QtCore

import zfused_api


class ProjectStepWidget(QtWidgets.QFrame):
    project_step_id_signal = QtCore.Signal(int)
    project_step_type_signal = QtCore.Signal(str)

    def __init__(self, project_id):
        super(ProjectStepWidget, self).__init__()
        self.project_id = project_id
        self._init()
        self._build()

    def _init(self):
        self._asset_steps = zfused_api.zFused.get('project_step', filter={
            'ProjectId': self.project_id,
            'object': 'asset'})
        self._shot_steps = zfused_api.zFused.get('project_step', filter={
            'ProjectId': self.project_id,
            'object': 'shot'})

    def _build(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self._asset_widget = QtWidgets.QFrame()
        self._layout.addWidget(self._asset_widget)
        self._asset_layout = QtWidgets.QVBoxLayout(self._asset_widget)
        self._asset_layout.setAlignment(QtCore.Qt.AlignTop)
        self._asset_tag = QtWidgets.QLabel()
        self._asset_tag.setText('Asset')
        self._asset_layout.addWidget(self._asset_tag)
        for _asset_step in self._asset_steps:
            _asset_name = _asset_step.get('Name')
            _btn = QtWidgets.QRadioButton()

            _btn.setText(_asset_name)
            _btn.toggled.connect(self._submit_asset_step_id)
            self._asset_layout.addWidget(_btn)

        self._shot_tag = QtWidgets.QLabel()
        self._shot_tag.setText('Shot')
        self._asset_layout.addWidget(self._shot_tag)

        for _shot_step in self._shot_steps:
            _shot_name = _shot_step.get('Name')
            _btn = QtWidgets.QRadioButton()
            _btn.setText(_shot_name)
            _btn.toggled.connect(self._submit_shot_step_id)
            self._asset_layout.addWidget(_btn)

    def _submit_asset_step_id(self):
        btn = self.sender()

        btn_text = btn.text()
        if btn.isChecked() is True:
            step = zfused_api.zFused.get('project_step', filter={
                'ProjectId': self.project_id,
                'Name': btn_text,
                'object': 'asset'})[0]
            step_id = step.get('Id')
            self.project_step_id_signal.emit(step_id)
            self.project_step_type_signal.emit('Asset')

    def _submit_shot_step_id(self):
        btn = self.sender()
        btn_text = btn.text()
        if btn.isChecked() is True:
            step = zfused_api.zFused.get('project_step', filter={
                'ProjectId': self.project_id,
                'Name': btn_text,
                'object': 'Shot'})[0]
            step_id = step.get('Id')
            self.project_step_id_signal.emit(step_id)
            self.project_step_type_signal.emit('Shot')

    # def clear_wdiget_focus(self):
    #     _radios = self.findChildren(QtWidgets.QRadioButton)
    #     for _radio in _radios:
    #         print(_radio.text())
    #         _radio.setChecked(False)