# -*- coding: UTF-8 -*-
'''
@Time    : 2020/11/24 21:05
@Author  : Jerris_Cheng
@File    : publishxgen.py
'''
import maya.cmds as cmds
import os
import shutil

from zcore import filefunc

def publishxgen():
    if _getallxgennode()[0] is True:
        _xgennode_list=_getallxgennode()[1]
        for xgen_node in _xgennode_list:
            _xgen_path=_getxgenfile(xgen_node)
            if not os.path.exists(_xgen_path):
                rf_xgen_path=_getrf_xgenfile(xgen_node)
                scene_xgen_path=_getxgenfile(xgen_node)
                transform_xgenfile(rf_xgen_path,scene_xgen_path)


        return True,u"xgen文件已设置成功"
    else:
        return True,"xgen is ok"

def transform_xgenfile(ast,dst):
    try:
        new_ast=ast.replace("\\","/")
        new_dst=dst.replace("\\","/")
        #filefunc.publish_file(ast,dst)
        shutil.copy(new_ast,new_dst)
    except Exception as e:
        print(e)


def _getallxgennode():
    _xgen_node_list=cmds.ls(type="xgmPalette")
    if not _xgen_node_list:
        return False,_xgen_node_list
    return True,_xgen_node_list


def _getrf_xgenfile(xgen):
    _filepath=_getrf_basepath(xgen)
    _xgenname=_getxgenfilename(xgen)
    _filename=_getfilename()
    if str(_xgenname).find(str(_filename))!=-1:
        _newname=_xgenname.replace(_filename+"__","")
        return os.path.join(_filepath,_newname)
    return os.path.join(_filepath,_xgenname)

def _getscenepath():
    _scenename=cmds.file(q=True,sceneName=True)
    _path=os.path.abspath(os.path.dirname(_scenename))
    return _path


def _isrefernecenode(xgen):
    if cmds.referenceQuery(xgen,isNodeReferenced=True):
        return True
    else:
        return False
def _getrfpath(xgen):
    path=cmds.referenceQuery(xgen,filename=True)
    return path

def _getrf_basepath(xgen):
    path = cmds.referenceQuery(xgen, filename=True)
    abs_path=os.path.abspath(os.path.dirname(path))
    return abs_path


def _getxgenfilename(xgen):
    _filename=cmds.getAttr(xgen+".xgFileName")
    return _filename

def _getfilename():
    filename=cmds.file(q=True,sceneName=True,shortName=True,ignoreVersion=True,withoutCopyNumber=True)
    _suffix=str(filename).split(".")[-1]
    name=filename.replace(".{}".format(_suffix),"")
    return name
def _getxgenfile(xgen):
    _xgenfilename = cmds.getAttr(xgen + ".xgFileName")
    _shortname=cmds.file(q=True,shortName=True,sceneName=True)
    _scnename=cmds.file(q=True,sceneName=True)

    all_path=_scnename.replace(_shortname,_xgenfilename)
    return all_path













