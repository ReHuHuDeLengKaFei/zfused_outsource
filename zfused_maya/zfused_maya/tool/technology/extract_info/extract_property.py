# -*- coding: UTF-8 -*-
"""
@Time    : 2022/9/23 14:57
@Author  : Jerris_Cheng
@File    : extract_property.py
@Description:
"""

from __future__ import print_function

import os
import shutil

from PySide2 import QtWidgets,QtCore

from zfused_maya.ui.widgets import window


class ExtractProperty(window.Window):
    def __init__(self):
        super(ExtractProperty, self).__init__()
        self._build()
    
    def _build(self):
        
        self.ground_widget = QtWidgets.QFrame()
        self.ground_layout = QtWidgets.QVBoxLayout(self.ground_widget)
        self.set_central_widget(self.ground_widget)
        self.ground_layout.setAlignment(QtCore.Qt.AlignTop)
        self.set_title_name(u'提取property文件')
        self.resize(400, 200)
        
        self.input_widget = QtWidgets.QFrame()
        self.input_layout = QtWidgets.QHBoxLayout(self.input_widget)
        self.input_lab = QtWidgets.QLabel(u"搜索路径")
        self.input_edit = QtWidgets.QLineEdit()
        self.input_btn = QtWidgets.QPushButton(u"浏览")
        self.input_btn.clicked.connect(self.set_input_dir)
        self.input_btn.setObjectName("title_button")
        self.input_layout.addWidget(self.input_lab)
        self.input_layout.addWidget(self.input_edit)
        self.input_layout.addWidget(self.input_btn)
        self.ground_layout.addWidget(self.input_widget)
        
        self.output_widget = QtWidgets.QFrame()
        self.output_layout = QtWidgets.QHBoxLayout(self.output_widget)
        self.output_lab = QtWidgets.QLabel(u"放置路径")
        self.output_edit = QtWidgets.QLineEdit()
        self.output_btn = QtWidgets.QPushButton(u"浏览")
        self.output_btn.clicked.connect(self.set_output_dir)
        self.output_btn.setObjectName("title_button")
        self.output_layout.addWidget(self.output_lab)
        self.output_layout.addWidget(self.output_edit)
        self.output_layout.addWidget(self.output_btn)
        self.ground_layout.addWidget(self.output_widget)
        
        self.tips_widget = QtWidgets.QFrame()
        self.tips_layout = QtWidgets.QHBoxLayout(self.tips_widget)
        self.tips_label = QtWidgets.QLabel()
        self.tips_label.setText(u'1、选择动画文件发布的P盘路径\n'
                                u'2、选择需要放置property的路径\n'
                                u'3、点击提取按钮')
        self.tips_layout.addWidget(self.tips_label)
        self.ground_layout.addWidget(self.tips_widget)
        
        self.execute_widget = QtWidgets.QFrame()
        self.execute_layout = QtWidgets.QHBoxLayout(self.execute_widget)
        self.execute_btn = QtWidgets.QPushButton(u"提取")
        self.execute_btn.clicked.connect(self.execute)
        self.execute_btn.setFixedHeight(40)
        self.execute_layout.addWidget(self.execute_btn)
        self.ground_layout.addWidget(self.execute_widget)


    def set_input_dir(self):
        _path = QtWidgets.QFileDialog.getExistingDirectory(self, u"搜索文件夹", "P:/")
        if not _path:
            return
        if not os.path.exists(_path):
            return
        
        self.input_edit.setText(_path)
    
    def set_output_dir(self):
        _path = QtWidgets.QFileDialog.getExistingDirectory(self, u"搜索文件夹", "D:/")
        if not _path:
            return
        if not os.path.exists(_path):
            return
        
        self.output_edit.setText(_path)
        
    def execute(self):
        if not os.path.exists(self.input_edit.text()):
            return
        if not os.path.exists(self.output_edit.text()):
            return
        
        for root,dirs,files in os.walk(self.input_edit.text()):
            for _file in files:
                try:
                    if str(_file).endswith('.property'):
                        _old_path = os.path.join(root,_file)
                        _copy_path = os.path.join(self.output_edit.text(),_file)
                        print(_old_path)
                        shutil.copy2(_old_path,_copy_path)
                except Exception as e :
                    print(e)
        QtWidgets.QMessageBox.information(self,u'通知',u'提取完成！')
        
                    