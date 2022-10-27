# coding:utf-8
# --author-- lanhua.zhou

""" shading color widget """
from __future__ import print_function

import os

from Qt import QtWidgets, QtCore

from pymel.core import *
import maya.cmds as cmds
import maya.mel as mel

from zfused_maya.ui.widgets import window

CAM_KEYWORD_LIST =  ['_cam']

def get_cam_list(*args):
    cam_list = []
    cam_list_all = ls(type = 'camera')
    for cam in cam_list_all:
        for cam_keyword in CAM_KEYWORD_LIST:
            if cam_keyword in str(cam):
                cam_list.append(listRelatives(cam, parent = True)[0])
    return cam_list


def export_cam(export_dir,outtype):
    filepath = cmds.file(q=True, sn=True)
    filename = os.path.basename(filepath).split('.')[0]
    export_name = filename+'_cam'
    export_path = os.path.join(export_dir,export_name +'.'+ outtype).replace('\\','/')

    cam = get_cam_list()[0]
    outcam = cmds.listRelatives(str(cam), fullPath=True)[0].split('|{}Shape'.format(cam))[0]
    select(cam, r = True)

    startframe = cmds.playbackOptions(q = True, min = True)
    endframe = cmds.playbackOptions(q = True, max = True)

    if outtype == 'ma':
        exportSelected(export_path, type = 'mayaAscii')
    elif outtype == 'mb':
        exportSelected(export_path, type = 'mayaBinary')    
    if outtype == 'abc':
        mel_cmd = 'AbcExport -j "-frameRange {} {} -worldSpace -dataFormat ogawa -root {} -file {}"'.format(startframe,endframe,outcam,export_path)
        mel.eval(mel_cmd)
    if outtype == 'fbx':
        export_path = export_path.replace('\\', '/')
        mel.eval('FBXExport -f "{0}" -s;'.format(export_path))
    if os.path.isfile(export_path):
        return True

def export_cam_dir(rootpath,export_dir,outtype):
    cam_list =[]
    num = 0
    for root, dir, filenames in os.walk(rootpath):
        #print ('root:',root)
        #print ('dir',dir)
        #print ('filenames:',filenames)
        for filename in filenames:
            if filename.endswith('.ma'):
                num += 1
                mapath = os.path.join(root,filename).replace('\\','/')
                cmds.file( mapath, open = True, force = True)
                try:
                    export_cam(export_dir,outtype)
                    if filename not in cam_list:
                        cam_list.append(filename)
                except Exception as e:
                    print(e)
                    pass
    
    file_list = os.listdir(rootpath)
    if cam_list:
        if len(cam_list)== num:
            return 0
        else:
            return 1
    else:
        return 2





class ExportCamera(window._Window):
    def __init__(self, parent = None):
        super(ExportCamera, self).__init__(parent)
        self._build()

        self.chose_Button.clicked.connect( self._set_input_folder )
        self.chose_Button2.clicked.connect(lambda :self.btn_fun(self.export_lineedit))

        self.ma_Button.clicked.connect(self._export_line)
        self.dir_Button.clicked.connect(self._seq_line)

    def _set_input_folder(self):
        self.list_widget.clear()
        _path = QtWidgets.QFileDialog.getExistingDirectory()+"/"
        self.seq_lineedit.setText(_path)
        _file_list = os.listdir(_path)
        _cam_list =[]
        for _file_name in _file_list:
            _file_path = _path + '/' + _file_name
            if os.path.isfile(_file_path):
                if _file_path.split('.')[-1] == 'ma':
                    _cam_list.append(_file_path)
        if _cam_list:
            self.list_widget.addItems(_cam_list)

    def _export_line(self):
        _path = self.export_lineedit.text()
        _format = self.select.currentText()
        
        _state = export_cam(_path,_format)
        '''
        if _format == 'ma' or _format == 'mb':
            _state = export_cam_mab(_path,_format)
        elif _format == 'abc':
            _state = export_cam_abc(_path)
        elif _format == 'fbx':
            _state = export_cam_fbx(_path)
        '''
        if _state:
            QtWidgets.QMessageBox.information(self,u"提示",u"相机导出成功！！！！！！！！！")
        else:
            QtWidgets.QMessageBox.critical(self,u"警告",u"相机未导出成功")
        
    def _seq_line(self):
        _inpath = self.seq_lineedit.text()
        _outpath = self.export_lineedit.text()
        _format = self.select.currentText()
        
        _state = export_cam_dir(_inpath,_outpath,_format)

        if _state == 0:
            QtWidgets.QMessageBox.information(self,u"提示",u"相机导出成功！！！！！！！！！")
        elif _state == 1:
            QtWidgets.QMessageBox.information(self,u"提示",u"部分相机导出成功，请检查文件是否正确")
        elif _state == 2:
            QtWidgets.QMessageBox.critical(self,u"警告",u"相机未导出成功")
    
    def prin(self):
        export_path = self.export_lineedit.text()
        print(export_path)

    def _build(self):
        self.resize(576, 330)
        self.set_title(u"导出摄像机(Export Camera)")
        # 布局    
        _widget = QtWidgets.QFrame()
        self.set_central_widget(_widget)
        _layout = QtWidgets.QVBoxLayout(_widget)
        # 注释
        self.error_label = QtWidgets.QLabel()
        _layout.addWidget(self.error_label)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)
        
        self.error_label.setStyleSheet("QLabel{font: bold 14px;background-color:#DD4444;color:#EDEDED;Text-align: center;}")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setText("每个文件内只能有一个摄像机且后缀为\"_cam\"\n输出当前场景摄像机请设置导出路径-导出当前摄像机\n批量输出请设置批量.ma文件夹路径-设置导出路径-批量导出文件夹下摄像机")
        
        # _layout.addStretch(True)

        # 输出面板
        self.export_widget = QtWidgets.QFrame()
        _layout.addWidget(self.export_widget)
        self.export_layout = QtWidgets.QHBoxLayout(self.export_widget)
        self.export_layout.setSpacing(6)
        self.export_layout.setContentsMargins(4,4,4,4)
        # 文件夹标签
        self.seq_label = QtWidgets.QLabel(self)
        self.export_layout.addWidget(self.seq_label)
        self.seq_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.seq_label.setText(u"批量.ma文件夹:") 
        # 文件夹路径输入
        self.seq_lineedit = QtWidgets.QLineEdit(self)
        self.export_layout.addWidget(self.seq_lineedit)
        # 批量路径选择
        self.chose_Button = QtWidgets.QPushButton(">>")
        self.export_layout.addWidget(self.chose_Button)
        self.chose_Button.setFixedSize(40,24)

        # 输入列表
        self.list_widget = QtWidgets.QListWidget()
        _layout.addWidget(self.list_widget)
        self.list_widget.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.list_widget.setStyleSheet("background-color:#222222")


        # 输入面板
        self.input_widget = QtWidgets.QFrame()
        _layout.addWidget(self.input_widget)
        self.input_layout = QtWidgets.QHBoxLayout(self.input_widget)
        self.input_layout.setSpacing(6)
        self.input_layout.setContentsMargins(4,4,4,4)
        # 导出标签
        self.export_label = QtWidgets.QLabel(self)
        self.input_layout.addWidget(self.export_label)
        self.export_label.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.export_label.setText(u"导出文件夹路径:")
        # 导出路径输入    
        self.export_lineedit = QtWidgets.QLineEdit(self)
        self.input_layout.addWidget(self.export_lineedit)
        # 导出路径选择
        self.chose_Button2 = QtWidgets.QPushButton(">>")
        self.input_layout.addWidget(self.chose_Button2)
        self.chose_Button2.setFixedSize(40,24)
        
        
        # 选择导出格式面板
        self.form_widget = QtWidgets.QFrame()
        _layout.addWidget(self.form_widget)
        self.form_layout = QtWidgets.QHBoxLayout(self.form_widget)
        self.form_layout.setSpacing(6)
        self.form_layout.setContentsMargins(4,4,4,4)
        # 选择标签
        self.form_label = QtWidgets.QLabel(self)
        self.form_layout.addWidget(self.form_label)
        #self.form_label.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.form_label.setText(u"导出格式:")
        # 导出路径输入   
        self.select = QtWidgets.QComboBox()
        self.form_layout.addWidget(self.select)
        self.formitem = ['ma','mb','abc','fbx']
        self.select.addItems(self.formitem)
        self.select.setFixedWidth(100)
        self.form_layout.insertSpacing(3,400)


        # 操作界面
        self.operation_widget = QtWidgets.QFrame()
        _layout.addWidget(self.operation_widget)
        self.operation_layout = QtWidgets.QHBoxLayout(self.operation_widget)
        self.operation_layout.setSpacing(4)
        self.operation_layout.setContentsMargins(4,4,4,4)
        # 导出ma按钮
        self.ma_Button = QtWidgets.QPushButton()
        self.operation_layout.addWidget(self.ma_Button)
        self.ma_Button.setMinimumSize(QtCore.QSize(100, 40))
        self.ma_Button.setText(u"导出当前场景摄像机")
        self.ma_Button.setFixedWidth(200)
        self.ma_Button.setStyleSheet("QPushButton{background-color:#252526}")
        self.operation_layout.addStretch(True)
        # 批量导出ma按钮
        self.dir_Button = QtWidgets.QPushButton()
        self.operation_layout.addWidget(self.dir_Button)
        self.dir_Button.setMinimumSize(QtCore.QSize(100, 40))
        self.dir_Button.setText(u"批量导出文件夹下摄像机")
        self.dir_Button.setFixedWidth(200)
        self.dir_Button.setStyleSheet("QPushButton{background-color:#252526}")

        '''
        self.operation_layout.insertSpacing(3,20)

        
        # 导出abc按钮
        self.abc_Button = QtWidgets.QPushButton()
        self.operation_layout.addWidget(self.abc_Button)
        self.abc_Button.setMinimumSize(QtCore.QSize(100, 40))
        self.abc_Button.setText(u"导出当前场景摄像机.abc")
        self.abc_Button.setFixedWidth(150)
        self.abc_Button.setStyleSheet("QPushButton{background-color:#252526}")
        self.operation_layout.addStretch(True)
        # 批量导出abc按钮
        self.abc_dir_Button = QtWidgets.QPushButton()
        self.operation_layout.addWidget(self.abc_dir_Button)
        self.abc_dir_Button.setMinimumSize(QtCore.QSize(10, 40))
        self.abc_dir_Button.setText(u"批量导出文件夹下摄像机.abc")
        self.abc_dir_Button.setFixedWidth(200)
        self.abc_dir_Button.setStyleSheet("QPushButton{background-color:#1e1e1e}")
        '''
    def btn_fun(self, line):
        _path = QtWidgets.QFileDialog.getExistingDirectory()+"/"
        line.setText(_path)

    
if __name__ =="__main__": 
    run = ExportCamera()
    run.show()
    sys.exit(app.exec_())