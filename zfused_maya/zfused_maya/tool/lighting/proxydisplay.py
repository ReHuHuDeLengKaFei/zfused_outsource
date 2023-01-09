# -*- coding: UTF-8 -*-
"""
@Time    : 2022/12/16 18:55
@Author  : Jerris_Cheng
@File    : proxydisplay.py
@Description:
"""
from __future__ import print_function

from PySide2 import QtWidgets,QtCore

from zfused_maya.ui.widgets import window

import maya.cmds as cmds


class ProxyDisplayWidget(window._Window):
    def __init__(self):
        super(ProxyDisplayWidget, self).__init__()
        self.display_model = 0
        self.select_list = []
        self._build()

    def _build(self):
        self.base_widget = QtWidgets.QFrame()
        self.base_layout = QtWidgets.QVBoxLayout(self.base_widget)
        self.set_central_widget(self.base_widget)
        self.set_title_name(u'阿诺德缓存显示')
        self.resize(400,200)

        self.statue_widget = QtWidgets.QFrame()
        self.statue_layout = QtWidgets.QHBoxLayout(self.statue_widget)
        self.base_layout.addWidget(self.statue_widget)
        self.base_layout.setAlignment(QtCore.Qt.AlignTop)
        # 状态栏
        self.boundbox_btn = QtWidgets.QCheckBox(u'显示box')
        self.boundbox_btn.toggled.connect(self.statue_model)
        self.hide_btn = QtWidgets.QCheckBox(u'隐藏')
        self.hide_btn.toggled.connect(self.statue_model)
        self.wire_btn = QtWidgets.QCheckBox(u'正常')
        self.wire_btn.toggled.connect(self.statue_model)
        self.statue_layout.addWidget(self.boundbox_btn)
        self.statue_layout.addWidget(self.hide_btn)
        self.statue_layout.addWidget(self.wire_btn)
        # 选择模式
        self.choosed_widget = QtWidgets.QFrame()
        self.choosed_layout = QtWidgets.QHBoxLayout(self.choosed_widget)
        self.all_btn = QtWidgets.QCheckBox(u'全选')
        self.all_btn.toggled.connect(self.selected)
        # self.un_select_btn = QtWidgets.QRadioButton(u'反选')
        self.selected_btn = QtWidgets.QCheckBox(u'选中')
        self.selected_btn.toggled.connect(self.selected)
        self.choosed_layout.addWidget(self.all_btn)
        self.choosed_layout.addWidget(self.selected_btn)
        self.base_layout.addWidget(self.choosed_widget)

        # run
        self.execute_widget = QtWidgets.QFrame()
        self.execute_layout = QtWidgets.QHBoxLayout(self.execute_widget)
        self.base_layout.addWidget(self.execute_widget)

        self.execute_btn = QtWidgets.QPushButton()
        self.execute_btn.setText(u'执行')
        self.execute_layout.addWidget(self.execute_btn)
        self.execute_btn.clicked.connect(self.execute)

    def statue_model(self):
        btn = self.sender()
        if btn.text() == u'显示box' and self.boundbox_btn.isChecked():
            self.hide_btn.setChecked(False)
            self.wire_btn.setChecked(False)
            self.display_model = 0
        elif btn.text() == u'隐藏' and self.hide_btn.isChecked():
            self.display_model = 1
            self.boundbox_btn.setChecked(False)
            self.wire_btn.setChecked(False)
        elif btn.text() == u'正常' and self.wire_btn.isChecked():
            self.boundbox_btn.setChecked(False)
            self.hide_btn.setChecked(False)
            self.display_model = 2

    def selected(self):
        btn = self.sender()
        if btn.text() == u'全选' and self.all_btn.isChecked():
            all_ass = cmds.ls(type='aiStandIn')
            self.selected_btn.setChecked(False)
            self.select_list = all_ass
        if btn.text() == u'选中' and self.selected_btn.isChecked():
            all_ass = cmds.ls(sl=True, type='aiStandIn', dag=True)
            self.all_btn.setChecked(False)
            self.select_list = all_ass

    def execute(self):
        for _ass in self.select_list:
            if self.display_model == 1:
                cmds.setAttr('{}.standInDrawOverride'.format(_ass), 3)
                continue

            if self.display_model == 0:
                cmds.setAttr('{}.standInDrawOverride'.format(_ass), 2)
                continue

            if self.display_model == 2:
                cmds.setAttr('{}.standInDrawOverride'.format(_ass), 0)
                cmds.setAttr('{}.mode'.format(_ass), 2)
        QtWidgets.QMessageBox.information(self, u'通知', u'让子弹飞一会·······')
