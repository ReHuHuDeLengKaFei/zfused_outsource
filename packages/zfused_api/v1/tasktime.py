# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import os
import time
import shutil
import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def submit_time(task_id,):
    pass

def clear(lis):
    del lis[:]

def cache(project_ids = []):
    """ get project tasks 
        init 
    """
    _s_t = time.clock()

    if not project_ids:
        _tasks = zfused_api.zFused.get("task_time",sortby = ["CreatedTime"], order = ["desc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_ids])
        _tasks = zfused_api.zFused.get("task_time", filter = {"ProjectId__in": _project_ids}, sortby = ["CreatedTime"], order = ["desc"])
    if _tasks:
        list(map(lambda _task: TaskTime.global_dict.setdefault(_task["Id"],_task), _tasks))
    _e_t = time.clock()
    logger.info("task cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _tasks

def cache_from_ids(ids):
    ids = "|".join(map(str, ids))
    _feedbacks = zfused_api.zFused.get("task_time", filter = {"Id__in": ids},sortby = ["CreatedTime"], order = ["desc"])
    if _feedbacks:
        list(map(lambda _feedback: TaskTime.global_dict.setdefault(_feedback["Id"],_feedback), _feedbacks))
    return _feedbacks



class TaskTime(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(TaskTime, self).__init__("task_time", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("task_time", self._id)
                if not _data:
                    logger.error("task time id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def code(self):
        return self.task().code()

    def name_code(self):
        return self.task().name_code()

    def project(self):
        return zfused_api.project.Project(self._data.get("ProjectId"))

    def project_id(self):
        return self._data.get("ProjectId")

    def project_entity(self):
        return zfused_api.objects.Objects( self._data.get("ProjectEntityType"), self._data.get("ProjectEntityId") )

    def project_step(self):
        return zfused_api.step.ProjectStep( self._data.get("ProjectStepId") )

    def project_step_id(self):
        return self._data.get("ProjectStepId")

    def production_time(self):
        return self.global_dict[self._id].get("ProductionTime")

    def production_date(self):
        _time_text = self._data.get("ProductionDate")
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("T")[0] #.replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d")        

    def task(self):
        return zfused_api.task.Task(self._data.get("TaskId"))

    def user_id(self):
        return self._data.get("UserId")

    def get_thumbnail(self, is_version = True):
        _task_id = self._data.get("TaskId")
        _task_handle = zfused_api.task.Task(_task_id)
        return _task_handle.get_thumbnail()
        # _thumbnail_path = _task_handle.data().get("ThumbnailPath")
        # if _thumbnail_path:
        #     if _thumbnail_path.startswith("storage"):
        #         return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        # return None

    def description(self):
        return self._data.get("Description")
