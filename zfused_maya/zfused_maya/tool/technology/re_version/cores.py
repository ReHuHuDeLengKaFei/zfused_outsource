# -*- coding: UTF-8 -*-
"""
@Time    : 2022/9/14 14:55
@Author  : Jerris_Cheng
@File    : cores.py
@Description:
"""
from __future__ import print_function

import argparse
import os
import re
import shutil
import time

import zfused_api


class MayaRefParser(object):
    def __init__(self, ma_file=None):
        self.header = ''
        self.refHeader = ''
        self.otherHeader = ''
        self.contents = ''
        self.contentsLineNum = 0
        self.ma_file = ma_file
        self.layoutIsLoaded = False
        
        self._need_update_files = []
        
        if ma_file and os.path.isfile(ma_file):
            self.parse(ma_file)
    
    def parse(self, ma_file):
        '''
        Store header refHeader otherHeader and contentsLineNum after parsing
        '''
        with open(ma_file) as inFile:
            # print("open file {}".format(ma_file))
            inHeader = True
            inRefHeader = False
            inOtherHeader = False
            inContents = False
            
            for line in inFile:
                # if line.startswith('fileInfo "UUID"'):
                #     print(line)
                if inHeader and line.startswith('file -r'):
                    inHeader = False
                    inRefHeader = True
                elif inRefHeader and not line.startswith('file -r') and not line.startswith('\t'):
                    inRefHeader = False
                    inOtherHeader = True
                elif inOtherHeader and line.startswith('createNode'):
                    inOtherHeader = False
                    inContents = True
                elif line.startswith('fileInfo "UUID"'):
                    inHeader = False
                    inContents = True
                if inHeader:
                    self.header += line
                elif inRefHeader:
                    self.refHeader += line
                elif inOtherHeader:
                    self.otherHeader += line
                elif inContents:
                    break
                
                self.contentsLineNum += 1
                # print("close file {}".format(ma_file))
    
    #
    # def _par_ref_header(self, header):
    #     parser = argparse.ArgumentParser()
    #     parser.add_argument('-rfn')
    #     parser.add_argument('-rdi')
    #     parser.add_argument('-ns')
    #     parser.add_argument('-dr')
    #     parser.add_argument('-typ')
    #     parser.add_argument('-op')
    #     # group = parser.add_mutually_exclusive_group()
    #     parser.add_argument('-r', action='store_true')
    #     parser.add_argument('file')
    #     parser.add_argument('-rpr')
    #     parser.add_argument('-shd', action='append')
    #     # args = parser.parse_args(header)
    #     args = parser.parse_args(header.split()[1:])
    #     # args.file = args.file.replace("'","")
    #     _old_file, _new_file = self.get_no_version(args.file)
    #     # if args.rdi == "1":
    #     #     if _new_file:
    #     #         self._need_update_files.append(_new_file)
    #     #     else:
    #     #         self._need_update_files.append(_old_file)
    #     return _old_file, _new_file
    def _par_ref_header(self, header):
        parser = argparse.ArgumentParser()
        parser.add_argument('-rfn')
        parser.add_argument('-rdi')
        parser.add_argument('-ns')
        parser.add_argument('-dr')
        parser.add_argument('-typ')
        parser.add_argument('-op')
        # group = parser.add_mutually_exclusive_group()
        parser.add_argument('-r', action='store_true')
        parser.add_argument('file')
        parser.add_argument('-rpr')
        parser.add_argument('-shd', action='append')
        # args = parser.parse_args(header)
        
        _space_re = re.compile(r'["](.*?)["]', re.S)  # 最小匹配
        _spaces = re.findall(_space_re, header)
        if _spaces:
            for _space in _spaces:
                if " " in _space:
                    header = header.replace(_space, _space.replace(" ", ""))
        
        args = parser.parse_args(header.split()[1:])
        # args.file = args.file.replace("'","")
        _old_file, _new_file = self.get_no_version(args.file)
        # if args.rdi == "1":
        #     if _new_file:
        #         self._need_update_files.append(_new_file)
        #     else:
        #         self._need_update_files.append(_old_file)
        return _old_file, _new_file
    
    def get_latest(self, file_path):
        """
        根据文件获取当前文件的最新版文件
        :param file_path:
        :return:
        """
        file_path = file_path.replace('"', '')
        _task_id = record_task_id(file_path)
        _latest_file = task_last_file(_task_id)
        if _latest_file == file_path:
            return file_path, None
        return file_path, _latest_file
    
    def get_no_version(self, file_path):
        """
        获取无版本文件
        :param file_path:
        :return:
        """
        file_path = file_path.replace('"', '')
        file_path_abs = file_path.replace('//', '/')
        _task_id = record_task_id(file_path_abs)
        if _task_id:
            _no_version_file = task_no_version_file(_task_id)
        else:
            _no_version_file = no_version_file(file_path_abs)
        #
        # if file_path == _no_version_file:
        #     return file_path, None
        return file_path, _no_version_file
    
    def update_file(self, new_file=None):
        if not self.refHeader:
            # 如果不需要修改则退出
            # shutil.copy(self.ma_file, new_file)
            return
        with open(new_file, 'w') as new_file:
            
            new_file.write(self.header)
            
            for line in self.refHeader.split(';\n')[:-1]:
                newLine = line
                if not newLine.endswith('.mb"'):
                    continue
                
                _old_file, _new_file = self._par_ref_header(newLine)
                print(_new_file)
                if _new_file:
                    newLine = newLine.replace(_old_file, _new_file)
                
                new_file.write(newLine + ';\n')
            
            new_file.write(self.otherHeader)
            
            with open(self.ma_file, 'r') as old_file:
                for _ in range(self.contentsLineNum):
                    old_file.readline()
                for old_line in old_file:
                    new_file.write(old_line)
    
    def par_ref_assets(self, new_file=None):
        """
        分析当前文件中的资产
        :return:
        """
        if not self.refHeader:
            # 如果不需要修改则退出
            # shutil.copy(self.ma_file, new_file)
            return
        _nodes = []
        _statue = True
        with open(new_file, 'r') as new_file:
            for line in self.refHeader.split(';\n')[:-1]:
                newLine = line
                if not newLine.endswith('.mb"'):
                    continue
                _old_file, _new_file = self._par_ref_header(newLine)
                # if _old_file == _new_file:
                #     _statue = False
                if not os.path.exists(_new_file):
                    _statue = False
                _nodes.append([_old_file, _new_file])
        return _statue, _nodes


def record_task_id(file_path):
    """
    根据文件路径获取task_id
    :param file_path:
    :return:
    """
    _record = zfused_api.zFused.get('production_file_record', filter={
        'Path': file_path})
    if not _record:
        return None
    _task_id = _record[0].get('TaskId')
    return _task_id


def task_last_file(task_id):
    """
    根据task_id 获取最新版文件路径
    :param task_id:
    :return:
    """
    if not task_id:
        return None
    task_entity = zfused_api.task.Task(task_id)
    _last_version = task_entity.last_version_id()
    _version_file = zfused_api.zFused.get('version', filter={
        'Id': _last_version})[0].get('FilePath')
    _task_path = task_entity.production_path()
    # _last_version_file_path = os.path.join(_task_path,_version_file)
    _last_version_file_path = '{}/file/{}'.format(_task_path, _version_file)
    if not os.path.exists(_last_version_file_path):
        return None
    return _last_version_file_path


def backup_file(ori_file):
    """ backup files
    """
    if not os.path.isfile(ori_file):
        return
    
    _dir = os.path.dirname(ori_file)
    _time_str = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    _backup_dir = "{}/__backup__/{}".format(_dir, _time_str)
    if not os.path.isdir(_backup_dir):
        os.makedirs(_backup_dir)
    
    _file_name = os.path.basename(ori_file)
    # _name = os.path.splitext(_file_name)[0]
    
    # _xgen_files = [
    #     os.path.join(_dir, x)
    #     for x in os.listdir(_dir)
    #     if x.startswith(_name) and os.path.splitext(x)[1] in [".xgen", "abc"]
    # ]
    
    # if _xgen_files:
    #     for _file in _xgen_files:
    #         _dst_file = _file.replace(_dir, _backup_dir)
    #         shutil.copy(_file, _dst_file)
    #         # remove src file
    #         os.remove(_file)
    
    # copy file and rename
    # _suffix = os.path.splitext(_file_name)
    # new name
    # _new_name = "{}.{}.{}".format(_suffix[0], _time_str, _suffix[-1])
    _new_file = "{}/{}".format(_backup_dir, _file_name)
    shutil.copy(ori_file, _new_file)
    
    return _new_file


def task_no_version_file(task_id):
    """
    根据task_id 获取不带版本号的文件
    :param task_id:
    :return:
    """
    if not task_id:
        return None
    task_entity = zfused_api.task.Task(task_id)
    _last_version = task_entity.last_version_id()
    if not _last_version:
        return None
    _task_path = task_entity.production_path()
    _version_file = zfused_api.zFused.get('version', filter={
        'Id': _last_version})[0].get('FilePath')
    _name = _version_file.split('.')[0]
    _suffix = _version_file.split('.')[-1]
    _no_version_file = '{}.{}'.format(_name, _suffix)
    _no_version_file_path = '{}/file/{}'.format(_task_path, _no_version_file)
    
    # if not os.path.exists(_no_version_file_path):
    #     return None
    return _no_version_file_path


def no_version_file(file_path):
    """
    根据文件路径直接查找不带版本号文件，如果文件不存在则直接返回当前文件
    
    :param file_path:
    :return:
    """
    _file_name, _file_suffix = os.path.splitext(file_path)
    _file = _file_name.split('.')[0]
    _no_version_file = '{}{}'.format(_file, _file_suffix)
    # if not os.path.exists(_no_version_file):
    #     return file_path
    return _no_version_file


def update_file(ma_file):
    if not os.path.isfile(ma_file):
        return
    _maya_reference_parser = MayaRefParser(ma_file)
    if not _maya_reference_parser.refHeader:
        print(u"{} 无需修改".format(ma_file))
        return True
    _backup_file = backup_file(ma_file)
    # 分析并修改文件
    _maya_reference_parser = MayaRefParser(_backup_file)
    # 分析文件当前内的资产是否存在，如果不存在直接返回
    _statue, _pars_assets = _maya_reference_parser.par_ref_assets(ma_file)
    if not _statue:
        return False, _pars_assets
    # 修改文件
    _maya_reference_parser.update_file(ma_file)
    return True, None
