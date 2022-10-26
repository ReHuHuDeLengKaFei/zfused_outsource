# -*- coding: UTF-8 -*-
"""
@Time    : 2022/10/20 14:51
@Author  : Jerris_Cheng
@File    : cores.py
@Description:
"""

import zfused_api


def output_attr_id(project_step_id):
    _attr_output = zfused_api.zFused.get('attr_output', filter={
        "ProjectStepId": project_step_id,
        'Code': 'file'})
    if not _attr_output:
        return 0
    return _attr_output[0].get('Id')
