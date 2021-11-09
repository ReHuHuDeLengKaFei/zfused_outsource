# -*- coding: UTF-8 -*-
'''
@Time    : 2021/11/5 13:51
@Author  : Jerris_Cheng
@File    : position_repair.py
'''
from __future__ import print_function
from qtpy import QtWidgets,QtGui
import json
import os
import maya.cmds as cmds
class position_repair_ui(QtWidgets.QWidget):
    def __init__(self):
        super(position_repair_ui,self).__init__()
        self._init()
        self.build()

    def _init(self):
        self.baselayout=QtWidgets.QVBoxLayout()
        self.file_laber =QtWidgets.QLabel("json path")
        self.file_edit =QtWidgets.QLineEdit()
        self.file_btn =QtWidgets.QPushButton(":")
        self.rfn_tree =QtWidgets.QTreeWidget()
        self.singl_repair_btn =QtWidgets.QPushButton(u"单独修复")
        self.global_repair =QtWidgets.QPushButton(u"全部修复")
        self.font =QtGui.QFont()



    def build(self):
        self.setLayout(self.baselayout)
        self.resize(600,800)
        self.setWindowTitle(u"修复")

        #设置json文件指认
        self.file_widget()
        self.rfn_tree_widget()
        self.repair_btn_widget()
        self.confige()

    def confige(self):
        self.file_btn.clicked.connect(self.file_btn_func)
        self.rfn_tree.setHeaderLabels(["namespace","file_path","matrix"])
        self.rfn_tree.setColumnCount(3)
        self.rfn_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.singl_repair_btn.clicked.connect(self.singal_repair_func)
        self.global_repair.clicked.connect(self.global_repair_func)
        self.font.setPixelSize(20)


        #
        all_widget=self.findChildren(QtWidgets.QWidget)
        for i in all_widget:
            i.setFont(self.font)
        pass

    #file_dialog
    def file_widget(self):
        widget =QtWidgets.QWidget()
        layout =QtWidgets.QHBoxLayout(widget)
        self.baselayout.addWidget(widget)
        layout.addWidget(self.file_laber)
        layout.addWidget(self.file_edit)
        layout.addWidget(self.file_btn)

    def rfn_tree_widget(self):
        _widget =QtWidgets.QWidget()
        layout =QtWidgets.QHBoxLayout(_widget)
        self.baselayout.addWidget(_widget)
        layout.addWidget(self.rfn_tree)


    def repair_btn_widget(self):
        widget =QtWidgets.QWidget()
        layout =QtWidgets.QHBoxLayout(widget)
        self.baselayout.addWidget(widget)
        layout.addWidget(self.singl_repair_btn)
        layout.addWidget(self.global_repair)

    def file_btn_func(self):
        file_dialog =QtWidgets.QFileDialog()
        json_path =file_dialog.getOpenFileName(self,'Open file',r'D:\\','Json files (*.json)')[0]
        self.file_edit.setText(json_path)
        try:
            with open(json_path,"r") as f:
                _date =json.load(f)
            for rfn_dict in _date:
                name_space =rfn_dict.get("namespace")
                file_path =rfn_dict.get("filename")
                print(file_path)
                if not os.path.exists(file_path):
                    without_name =rfn_dict.get("without_name")
                    short_name =rfn_dict.get("short_name")
                    file_path =file_path.replace(short_name,without_name)

                matrix =str(rfn_dict.get("matrix"))
                item =QtWidgets.QTreeWidgetItem(self.rfn_tree)
                item.setText(0,name_space)
                item.setText(1,file_path)
                item.setText(2,matrix)
        except Exception as e:
            print(e)
    def singal_repair_func(self):
        items =self.rfn_tree.selectedItems()[0]
        matrix =eval(items.text(2))
        main_curve =cmds.ls(sl=True)[0]
        if main_curve:
            if "Main" in main_curve:
                try:
                    cmds.xform(main_curve,matrix=matrix)
                except Exception as e:
                    print(e)
            else:
                QtWidgets.QMessageBox.critical(self, u"错误", u"请选择Main控制器")

        else:
            QtWidgets.QMessageBox.critical(self,u"错误",u"没有选中大环")
    def global_repair_func(self):
        item =QtWidgets.QTreeWidgetItemIterator(self.rfn_tree)
        while item.value():

            name_space =item.value().text(0)
            filename =item.value().text(1)
            temp_matrix =eval(item.value().text(2))

            rfn =cmds.file(filename,reference=True,namespace=name_space)
            _temp_namespace =cmds.referenceQuery(rfn,namespace=True)
            main_curve ="{}:{}".format(_temp_namespace,"Main")

            if cmds.objExists(main_curve):
                cmds.xform(main_curve,matrix=temp_matrix)
            item = item.__iadd__(1)
