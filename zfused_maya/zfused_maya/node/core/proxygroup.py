# -*- coding: utf-8 -*-
# hz
""" 场景集合操作函数集 """
from __future__ import print_function
import logging
import maya.cmds as cmds

logger = logging.getLogger(__name__)

def set_node_attr(node):
    """ set node proxy attr

    """
    if not cmds.objExists("{}.proxy".format(node)):
        cmds.addAttr(node, longName = "proxy",at = 'bool')
        cmds.setAttr("{}.proxy".format(node), True)

def nodes():
    """ get proxy node
    :rtype: list
    """
    _is_proxy = []
    _proxydag = [i for i in cmds.ls(dag = 1, l = True) if cmds.objExists("{}.proxy".format(i))]
    for _dag in _proxydag:
        _value = cmds.getAttr("%s.proxy"%_dag)
        if _value:
            _is_proxy.append(_dag)
    return _is_proxy

def if_member():
    '''
    whether proxy group contains members
    '''
    if_member = False
    _group = nodes()
    if _group:
        _shapes = cmds.listRelatives(_group[0], ad=True,type = 'shape')
        if _shapes:
            if_member = True
    return if_member 