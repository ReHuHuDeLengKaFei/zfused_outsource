# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import time
import logging
import datetime

from . import _Entity
import zfused_api


logger = logging.getLogger(__name__)


def new_record(name, company_id, project_id, project_step_id, project_entity_type, project_entity_id, task_id, index = 1, thumbnail_path = ""):
    _created_by = zfused_api.zFused.USER_ID
    _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    _provides = zfused_api.zFused.get("file_provide", filter = {"CompanyId":company_id, "TaskId": task_id})
    if _provides:
        for _provide in _provides:
            zfused_api.zFused.delete("file_provide", _provide["Id"])

    _value, _status = zfused_api.zFused.post( "file_provide", data = { "Name": name, 
                                                                        "CompanyId": company_id,
                                                                        "ProjectId": project_id, 
                                                                        "ProjectStepId": project_step_id, 
                                                                        "ProjectEntityType": project_entity_type,
                                                                        "ProjectEntityId": project_entity_id,
                                                                        "TaskId": task_id,
                                                                        "Index": index,
                                                                        "ThumbnailPath": thumbnail_path,
                                                                        "CreatedBy": _created_by,
                                                                        "CreatedTime": _created_time } )

    _value, _status = zfused_api.zFused.post( "file_provide_record", data = { "Name": name, 
                                                                              "CompanyId": company_id,
                                                                              "ProjectId": project_id, 
                                                                              "ProjectStepId": project_step_id, 
                                                                              "ProjectEntityType": project_entity_type,
                                                                              "ProjectEntityId": project_entity_id,
                                                                              "TaskId": task_id,
                                                                              "Index": index,
                                                                              "ThumbnailPath": thumbnail_path,
                                                                              "CreatedBy": _created_by,
                                                                              "CreatedTime": _created_time } )
    if _status:
        return _value["Id"], "files provide create success"
    return False,"files provide create error"


def cache_from_ids(ids):
    _s_t = time.clock()


    ids = "|".join(map(str, ids))
    _tasks = zfused_api.zFused.get("file_provide", filter = {"Id__in": ids}, sortby = ["Id"], order = ["desc"])
    # _task_versions = zfused_api.zFused.get("version", filter = {"TaskId__in": ids})
    if _tasks:
        list(map(lambda _task: FileProvide.global_dict.setdefault(_task["Id"],_task), _tasks))
    _e_t = time.clock()
    logger.info("task cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _tasks


class FileProvide(_Entity):
    global_dict = {}
    global_tags = defaultdict(list)
    def __init__(self, entity_id, entity_data = None):
        super(FileProvide, self).__init__("file_provide", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("file_provide", self._id)
                if not _data:
                    logger.error("file_provide id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def project_entity(self):
        return zfused_api.objects.Objects(self._data.get("ProjectEntityType"), self._data.get("ProjectEntityId"))

    def project_step_id(self):
        return self._data.get("ProjectStepId")

    def project_step(self):
        return zfused_api.step.ProjectStep(self._data.get("ProjectStepId"))

    def index(self):
        return self._data.get("Index")

    def get_thumbnail(self, is_version = True):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None

    def task(self):
        return zfused_api.task.Task(self._data.get("TaskId"))

    def task_id(self):
        return self._data.get("TaskId")

    def is_latest(self):
        if "is_latest" not in self._data:
            return 0
        else:
            return self._data.get("is_latest")

    def analy_is_latest(self):
        _index = self._data.get("Index")
        _versions = zfused_api.zFused.get("version", filter = {"TaskId": self.task_id()}, fields = ["Id"])
        self._data["is_latest"] = 1 if _index == len(_versions) else -1