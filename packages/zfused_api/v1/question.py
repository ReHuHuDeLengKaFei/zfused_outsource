# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import shutil
import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def cache( project_id ):
    """ init project versions
    """
    Question.global_dict = {}
    if not project_id:
        _questions = zfused_api.zFused.get("question", sortby = ["Id"], order = ["desc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _questions = zfused_api.zFused.get("question", filter = {"ProjectId__in": _project_ids}, sortby = ["Id"], order = ["desc"])
    if _questions:
        for _question in _questions:
            Question.global_dict[_question["Id"]] = _question
    return _questions

def cache_from_ids(ids):
    ids = "|".join(map(str, ids))
    _questions = zfused_api.zFused.get("question", filter = {"Id__in": ids})
    if _questions:
        list(map(lambda _question: Question.global_dict.setdefault(_question["Id"],_question), _questions))
    return _questions


class Question(_Entity):


    @classmethod
    def new(cls, task_id, title, user_ids, medias = [], files = [], description = ""):
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID

        _task = zfused_api.task.Task(task_id)

        _question, _status = zfused_api.zFused.post( key = "question", 
                                                     data = { "ProjectId": _task.project_id(),
                                                              "ProjectEntityType": _task.project_entity_type(),
                                                              "ProjectEntityId": _task.project_entity_id(),
                                                              "ProjectStepId": _task.project_step_id(),
                                                              "SoftwareId": _task.software_id(),
                                                              "TaskId": _task.id(),
                                                              "Title": title,
                                                              "Description": description,
                                                              "Medias": str(medias),
                                                              "Status": 0,
                                                              "CreatedBy": _created_by,
                                                              "CreatedTime": _created_time } )
        if not _status:
            return u"{} create error".format(title), False

        _question_id = _question.get("Id")

        # group user
        for _user_id in user_ids:
            zfused_api.zFused.post( "group_user", { "EntityType": "question", 
                                        "EntityId": _question_id, 
                                        "UserId": _user_id,
                                        "CreatedBy": _created_by,
                                        "CreatedTime": _created_time })

        zfused_api.im.submit_message( "user",
                                      _created_by,
                                      user_ids,
                                      {"entity_type": "question",
                                       "entity_id": _question_id},
                                      "question", 
                                      "question",
                                      _question_id,
                                      "question",
                                      _question_id )

        return _question_id, True


    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Question, self).__init__("question", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("question", self._id)
                if not _data:
                    logger.error("question id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data

    def entity(self):
        return zfused_api.objects.Objects(self._data.get("EntityType"),self._data.get("EntityId"))

    def name_code(self):
        return self.title()

    def title(self):
        return self._data.get("Title")

    def description(self):
        return self._data["Description"]

    def project(self):
        return zfused_api.project.Project(self.project_id())

    def project_id(self):
        _project_id = self._data["ProjectId"]
        return _project_id

    def project_entity_type(self):
        return self._data["ProjectEntityType"]

    def project_entity_id(self):
        return self._data["ProjectEntityId"]

    def project_entity(self):
        return zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"])

    def entity(self):
        return zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"])

    def project_step(self):
        _project_step_id = self._data.get("ProjectStepId")
        if _project_step_id:
            return zfused_api.step.ProjectStep(_project_step_id)
        return None

    def project_step_id(self):
        return self.global_dict[self._id]["ProjectStepId"]

    def full_name_code(self):
        return zfused_api.objects.Objects(self._data["EntityType"], self._data["EntityId"]).full_name_code()

    def file_code(self):
        """ project step file code

        :rtype: str
        """
        return self.code().replace("/", "_")

    def file_path(self):
        return self.code()

    def color(self):
        """ return question color
        """
        return self._data["Coloe"]

    def sort(self):
        """ 返回排序序号
        """
        return self._data["Sort"]

    def status(self):
        return self._data["Status"]

    def update_status(self, status):
        """ update status
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self._data["Status"] == status:
            return False

        self.global_dict[self._id]["Status"] = status
        self._data["Status"] = status
        v = self.put("question", self._data["Id"], self._data, "status")
        if v:
            return True
        else:
            return False

    def task(self):
        return zfused_api.task.Task(self._data.get("TaskId"))

    def task_id(self):
        return self._data.get("TaskId")

    def update_color(self, color):
        self.global_dict[self._id]["Color"] = color
        self._data["Color"] = color
        v = self.put("project_step", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    def get_thumbnail(self, is_question = True):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None

    def thumbnail(self):
        """ get thumbnail
        """
        return self._data["ThumbnailPath"]
