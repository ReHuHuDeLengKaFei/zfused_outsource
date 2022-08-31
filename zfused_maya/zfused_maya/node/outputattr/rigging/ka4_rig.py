# -*- coding: UTF-8 -*-
'''
@Time    : 2020/12/14 11:43
@Author  : Jerris_Cheng
@File    : ka4_rig.py
'''

from zfused_maya.core import record
import os
_project_id=record.current_project_id()
#_project_id=26

from zcore import filefunc

ka4_path=r"B:\temp\jerris\ka4\asset\rig"
if not os.path.exists(ka4_path):
    os.makedirs(ka4_path)

def publish(rig_path):
    if _project_id==26:
        _parent=os.path.basename(rig_path)
        new_path=os.path.join(ka4_path,_parent)
        _reuslt=filefunc.publish_file(rig_path,new_path)
        if _reuslt:
            os.system(r"\\td\pipeline\ming\ka4\changePath_auto.bat")
