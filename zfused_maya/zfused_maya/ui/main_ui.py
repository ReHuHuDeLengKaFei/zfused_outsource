# -*- coding: UTF-8 -*-
'''
@Time    : 2021/8/9 16:59
@Author  : Jerris_Cheng
@File    : main_ui.py
'''


import maya.cmds as cmds
import json

import zfused_api
import zfused_maya.core.record as record
reload(record)

import os
#
class main_menu(object):
    def __init__(self):
        super(main_menu,self).__init__()
        #self._menu_file=os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"conf\menu.json"))

        #self._menu_file = os.path.join(sys.argv[1],"conf\menu.json")
        self._menu_file=r"D:\zf_outsource\zfused_outsource\zfused_maya\conf\menu.json"

    def createmenu(self,_dict):



        current_project=u"没有项目"
        if record.current_project_id():
            current_project_id=record.current_project_id()
            _task_handle = zfused_api.project.Project(str(current_project_id))
            current_project=_task_handle.name()

        if cmds.menu("zfused_outsource_menu",ex=True):
            cmds.deleteUI("zfused_outsource_menu")

        cmds.setParent("MayaWindow")
        cmds.menu("zfused_outsource_menu", label=u"zfused_outsource", to=True)
        cmds.menuItem(label=u"zfused_outsource",d=True)



        # #current_project_itme
        # project_item=current_project
        #
        # cmds.menuItem(label=u"{}".format(project_item),to=True,en=True)
        # cmds.menuItem(d=True)


        cmds.menuItem(label=u"{}".format(current_project), subMenu=True, to=True)
        all_project=zfused_api.zFused.get("project_company")

        all_project_id_list=[]
        for _project in all_project:
            _id = _project.get("ProjectId")
            all_project_id_list.append(_id)

        for project_id in list(set(all_project_id_list)):
            _task_handle = zfused_api.project.Project(str(project_id))
            _project_name=_task_handle.name()

            #_cmd="import zfused_maya.core.record as record; record.write_project_id({};))".format(project_id)
            _cmd=self._function(project_id)
            _project_code=_task_handle.code()
            cmds.menuItem(label=_project_code,d=True)

            cmds.menuItem(label=u"{}".format(_project_name),command=_cmd)

        cmds.setParent("zfused_outsource_menu", menu=True)


        #utility
        utility_menu="utility"
        cmds.menuItem(d=True)
        cmds.menuItem(label=u"{}".format(utility_menu), subMenu=True, to=True)

        _parent_list=_dict.get(utility_menu)

        for child_menu in _parent_list:
            _child_dict=child_menu
            _name=_child_dict.get("name")
            _cmd=_child_dict.get("cmd")
            # print _cmd
            cmds.menuItem(label=u"{}".format(_name), command=u"{}".format(_cmd))
            cmds.menuItem(d=True)

        cmds.setParent("zfused_outsource_menu", menu=True)



        #model

        model_menu="model"
        cmds.menuItem(d=True)
        cmds.menuItem(label=u"{}".format(model_menu), subMenu=True, to=True)

        _parent_list=_dict.get(model_menu)
        for child_menu in _parent_list:
            _child_dict=child_menu
            _name=_child_dict.get("name")
            _cmd=_child_dict.get("cmd")
            # print _cmd
            cmds.menuItem(label=u"{}".format(_name), command=u"{}".format(_cmd))
            cmds.menuItem(d=True)

        cmds.setParent("zfused_outsource_menu", menu=True)

        #animation

        animation_menu="animation"
        cmds.menuItem(d=True)
        cmds.menuItem(label=u"{}".format(animation_menu), subMenu=True, to=True)

        _parent_list=_dict.get(animation_menu)
        for child_menu in _parent_list:
            _child_dict=child_menu
            _name=_child_dict.get("name")
            _cmd=_child_dict.get("cmd")
            # print _cmd
            cmds.menuItem(label=u"{}".format(_name), command=u"{}".format(_cmd))
            cmds.menuItem(d=True)

        cmds.setParent("zfused_outsource_menu", menu=True)






        cmds.setParent("zfused_outsource_menu", menu=True)

    def _getmenu_dict(self):
        try:
            with open(self._menu_file) as f:
                _dict=json.load(f)
                return _dict
        except Exception as e:
            print "Error read json file,{}".format(e)
            return {}

    def create_menu(self):
        _dict=self._getmenu_dict()
        print _dict
        try:
            self.createmenu(_dict)
        except Exception as e:
            print "Error,{}".format(e)


    def _function(self,id):
        _fun="import zfused_maya.core.record as record;" \
             " record.write_project_id({});".format(id)

        return _fun