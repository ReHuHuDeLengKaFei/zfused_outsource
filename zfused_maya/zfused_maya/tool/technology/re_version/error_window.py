# -*- coding: UTF-8 -*-
"""
@Time    : 2022/9/29 14:23
@Author  : Jerris_Cheng
@File    : error_window.py
@Description:
"""
from __future__ import print_function

import os

from zfused_maya.ui.widgets import window
from PySide2 import QtWidgets,QtCore,QtGui
class ErrorWindow(window._Window):
    def __init__(self,error_nodes):
        super(ErrorWindow, self).__init__()
        self.error_nodes = error_nodes
        self._build()
    
    def _build(self):
        self.ground_widget = QtWidgets.QFrame()
        self.ground_layout = QtWidgets.QVBoxLayout(self.ground_widget)
        self.set_central_widget(self.ground_widget)
        
        self.error_tree = QtWidgets.QTreeWidget()
        self.error_tree.setHeaderLabels(['旧文件路径','新文件路径','新文件是否存在'])
        self.ground_layout.addWidget(self.error_tree)
        for error_node in self.error_nodes:
            old_file = error_node[0]
            new_file =error_node[1]
            node_item = QtWidgets.QTreeWidgetItem(self.error_tree)
            node_item.setText(0,old_file)
            node_item.setText(1,new_file)
            node_item.setText(2,'Exists')
            node_item.setBackgroundColor(2,'green')
            if not os.path.exists(new_file):
                node_item.setText(2,'Not Exists')
                #node_item.setBackground(0,QtGui.QBrush(QtGui.QColor("#0000FF")))
                #node_item.setBackground(2,QtGui.QColor("#125622"))
                #.value().setBackground(3, QtCore.Qt.darkGreen)
                
