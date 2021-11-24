# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import os
import json
import logging

import maya.cmds as cmds

import zfused_api

from zfused_maya.core import record

from zfused_maya.core import tomaya

import zfused_maya.core.menu as menu

__all__ = ["build", "delete", "rebuild"]

logger = logging.getLogger(__name__)


def change_project(project_id):
    record.write_project_id(project_id)
    if cmds.menu("zfused_project", q=True, exists=True):
        cmds.menu("zfused_project", e = True, label = zfused_api.project.Project(project_id).name())

def change_company():
    from zfused_maya.interface import company
    from zfused_maya.ui.widgets import window
    _company_id, _res = company.SetCompanyWidget.set_company(window._Window())
    # print(_company_id, _res)
    if _res:
        record.write_company_id(_company_id)
        if cmds.menuItem("zfused_company", q=True, exists=True):
            cmds.menuItem("zfused_company", e = True, label = zfused_api.company.Company(_company_id).name())

        _build_project_menu()
        
    return _res

def _build_project_menu():
    if cmds.menu("zfused_project", q = True, exists = True):
        cmds.deleteUI("zfused_project")
    # project menu
    _project_id = record.current_project_id()
    if _project_id:
        _project_name = zfused_api.project.Project(_project_id).name()
    else:
        _project_name = u"暂无项目"
    cmds.menu( "zfused_project", label = _project_name,
                    parent = "MayaWindow", 
                    tearOff = True,
                    version = cmds.about(q=True, version=True) )
    _all_projects = zfused_api.zFused.get("project_company", filter = {"CompanyId": record.current_company_id()})
    if _all_projects:
        _all_project_id_list = [_project.get("ProjectId") for _project in _all_projects]
        for _project_id in list(set(_all_project_id_list)):
            _project = zfused_api.project.Project(_project_id)
            _status = _project.status()
            if _status.category() == "in progress":
                _project_name = _project.name()
                cmds.menuItem(label = "", divider = True, parent = "zfused_project")
                cmds.menuItem(label=u"{}".format(_project_name), command = "from zfused_maya.interface import menubar;menubar.change_project({});".format(_project_id))

def build():
    """build zfused maya menu 
    """
    # ===============================================================
    # main menu
    cmds.menu("zfused_outsource", parent = "MayaWindow", label = "zFused outsource", tearOff = True)
    _menu_data = menu.get_menu_data()
    cmds.menuItem(label = u"", divider=True, parent = "zfused_outsource")
    _company_id = record.current_company_id()
    if _company_id:
        _company_name = zfused_api.company.Company(_company_id).name()
    else:
        _company_name = u"未设置公司"
    cmds.menuItem("zfused_company", label=u"{}".format(_company_name), command = "from zfused_maya.interface import menubar;menubar.change_company();", parent = "zfused_outsource")
    cmds.menuItem(label = u"", divider=True, parent = "zfused_outsource")

    for _menu_title in menu.MENU_KEY:
        cmds.menuItem( _menu_title, 
                       label = _menu_title,
                       parent = "zfused_outsource", 
                       subMenu = True, 
                       tearOff = True )
        if _menu_title in _menu_data.keys():
            # load menu
            category = []
            category_cmds = {}
            menu_data = _menu_data[_menu_title]
            for data in menu_data:
                cate = data["category"]
                if not cate in category:
                    category.append(cate)
                if not cate in category_cmds:
                    category_cmds[cate] = []
                category_cmds[cate].append(data)
            for ca in category:
                cmds.menuItem(label = ca, divider=True, parent = _menu_title)
                for data in category_cmds[ca]:
                    cmds.menuItem( data["name"], label = data["title"],
                                   parent=_menu_title, command = data["cmd"])
        cmds.menuItem(divider=True, parent="zfused_outsource")

    # project menu
    _build_project_menu()

def delete():
    if cmds.menu("zfused_outsource", q=True, exists=True):
        cmds.deleteUI("zfused_outsource")
    if cmds.menu("zfused_project", q=True, exists=True):
        cmds.deleteUI("zfused_project")

def rebuild():
    delete()
    build()