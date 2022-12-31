# -*- coding: UTF-8 -*-
"""
@Time    : 2022/12/16 11:28
@Author  : Jerris_Cheng
@File    : refparser.py
@Description:
"""
from __future__ import print_function

import argparse
import os
import re

import zfused_api

import logging

_logger = logging.getLogger(__name__)


class MayaRefParser(object):
    def __init__(self, ma_file=None):
        self.header = ''
        self.refHeader = ''
        self.otherHeader = ''
        self.contents = ''
        self.contentsLineNum = 0
        self.ma_file = ma_file
        self.layoutIsLoaded = False
        # self.replace_relative_file = replace_relative_file

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

    def _par_ref_header(self, header, replace_relative_file):
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
        _old_file, _new_file = self.relitive_file_record(args.file,replace_relative_file)

        return _old_file, _new_file

    def relitive_file_record(self, file_path, replace_relative_file):
        try:
            file_path = file_path.replace('"', '')
            file_path_abs = file_path.replace('//', '/')
            _asset_entity_id = zfused_api.zFused.get('production_file_record', filter={
                'Path': file_path_abs})[0].get('ProjectEntityId')
            _logger.info(u'获取镜头文件内资产关联成功！')
            _relative_entity_id = zfused_api.zFused.get('production_file_record', filter={
                'Path': replace_relative_file})[0].get('ProjectEntityId')
            _logger.info(u'获取rigsol资产关联成功！')
            if _asset_entity_id == _relative_entity_id:
                _logger.info(u'匹配成功，----------进行替换')
                return file_path,replace_relative_file

            else:
                _logger.warning(u'匹配失败,进行下一循环匹配')
                return file_path,file_path

        except Exception as e:
            _logger.error(e)
            _logger.error(u'资产匹配失败')

    def update_file(self, new_file=None, replace_relative_file=None):
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

                _old_file, _new_file = self._par_ref_header(newLine,replace_relative_file)

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