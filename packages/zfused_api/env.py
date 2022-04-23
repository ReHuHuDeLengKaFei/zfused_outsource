# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

# zfused_api 全局变量


__startup_project_id = 0
__startup_task_id = 0


def startup_project_id():
    return __startup_project_id

def set_startup_project_id(project_id):
    global __startup_project_id
    __startup_project_id = project_id


def startup_task_id():
    return __startup_task_id

def set_startup_task_id(task_id):
    global __startup_task_id
    __startup_task_id = task_id