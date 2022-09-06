# coding:utf-8
# --author-- lanhua.zhou

from __future__ import print_function

import maya.cmds as cmds


def create_group():
    cmds.group(n='fur_group', em=True)
    cmds.group(n='hair_group', em=True, parent='fur_group')
    cmds.group(n='hair_inputcv', em=True, parent='hair_group')
    cmds.group(n='inputcv_to_render', em=True, parent='hair_inputcv')
    cmds.group(n='hair_outputcv', em=True, parent='hair_group')
    cmds.group(n='outputcv_to_render', em=True, parent='hair_outputcv')
    cmds.group(n='hair_sys', em=True, parent='hair_group')
    cmds.group(n='sys_to_render', em=True, parent='hair_sys')
    cmds.group(n='grow_group', em=True, parent='fur_group')
    cmds.group(n='xgen_group', em=True, parent='fur_group')

    cmds.addAttr('grow_group', ln='groom_caching', at='bool')
    cmds.setAttr('{}.{}'.format('grow_group', 'groom_caching'), 1, l=True)

    cmds.addAttr('outputcv_to_render', ln='outcurve', at='bool')
    cmds.setAttr('{}.{}'.format('outputcv_to_render', 'outcurve'), 1, l=True)
