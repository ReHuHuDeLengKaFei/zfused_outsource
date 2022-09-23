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
    Note.global_dict = {}
    if not project_id:
        _notes = zfused_api.zFused.get("note", sortby = ["Id"], order = ["desc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _notes = zfused_api.zFused.get("note", filter = {"ProjectId__in": _project_ids}, sortby = ["Id"], order = ["desc"])
    if _notes:
        for _note in _notes:
            Note.global_dict[_note["Id"]] = _note
    return _notes

def cache_from_ids(ids):
    ids = "|".join(map(str, ids))
    _notes = zfused_api.zFused.get("note", filter = {"Id__in": ids})
    if _notes:
        list(map(lambda _note: Note.global_dict.setdefault(_note["Id"],_note), _notes))
    return _notes


class Note(_Entity):


    # @classmethod
    # def new(cls, task_id, title, user_ids, medias = [], files = [], description = ""):
    #     _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    #     _created_by = zfused_api.zFused.USER_ID

    #     _task = zfused_api.task.Task(task_id)

    #     _note, _status = zfused_api.zFused.post( key = "note", 
    #                                                  data = { "ProjectId": _task.project_id(),
    #                                                           "ProjectEntityType": _task.project_entity_type(),
    #                                                           "ProjectEntityId": _task.project_entity_id(),
    #                                                           "ProjectStepId": _task.project_step_id(),
    #                                                           "SoftwareId": _task.software_id(),
    #                                                           "TaskId": _task.id(),
    #                                                           "Title": title,
    #                                                           "Description": description,
    #                                                           "Medias": str(medias),
    #                                                           "Status": 0,
    #                                                           "CreatedBy": _created_by,
    #                                                           "CreatedTime": _created_time } )
    #     if not _status:
    #         return u"{} create error".format(title), False

    #     _note_id = _note.get("Id")

    #     # group user
    #     for _user_id in user_ids:
    #         zfused_api.zFused.post( "group_user", { "EntityType": "note", 
    #                                     "EntityId": _note_id, 
    #                                     "UserId": _user_id,
    #                                     "CreatedBy": _created_by,
    #                                     "CreatedTime": _created_time })

    #     zfused_api.im.submit_message( "user",
    #                                   _created_by,
    #                                   user_ids,
    #                                   {"entity_type": "note",
    #                                    "entity_id": _note_id},
    #                                   "note", 
    #                                   "note",
    #                                   _note_id,
    #                                   "note",
    #                                   _note_id )

    #     return _note_id, True


    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Note, self).__init__("note", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("note", self._id)
                if not _data:
                    logger.error("note id {0} not exists".format(self._id))
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
    
    def entity_type(self):
        return self._data.get("EntityType")

    def entity_id(self):
        return self._data.get("EntityId")
    
    def entity(self):
        return zfused_api.objects.Objects(self.entity_type(), self.entity_id())

    def title(self):
        return self._data.get("Title")

    def status(self):
        return self._data.get("Status")

    def rich_text(self):
        return eval(self._data.get("RichText"))

    def update_status(self, status):
        self.global_dict[self._id]["Status"] = status
        self._data["Status"] = status
        v = self.put("note", self._data["Id"], self._data, "status")
        if v:

            _count = zfused_api.zFused.get( "note", filter = { "EntityType": self.entity_type(),
                                                               "EntityId": self.entity_id(),
                                                               "Status": 0 } )
            if _count:
                _count = len(_count)
            else:
                _count = 0
            self.entity().update_note_count(_count)

            return True
        else:
            return False
        