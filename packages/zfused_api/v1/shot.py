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

def delete(shot_id):
    """ delete asset

    """
    zfused_api.zFused.delete("shot", shot_id)

def new_shot(project_id, name, code, status_id, episode_id = 0, sequence_id = 0, type_id = 0,create_by = None, description = None, active = "true"):
    """ create new asset

    """
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    # asset is exists
    _shots = zfused_api.zFused.get( "shot", 
                                    filter = {"ProjectId": project_id,"Code": code, "EpisodeId": episode_id, "SequenceId": sequence_id})
    if _shots:
        return "{} is exists".format(name), False

    if create_by:
        _create_by_id = create_by
    else:
        _create_by_id = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post(key = "shot", data = {  "Name": name,
                                                   "Code": code,
                                                   "ProjectId": project_id,
                                                   "StatusId":status_id,
                                                   "EpisodeId": episode_id,
                                                   "SequenceId": sequence_id,
                                                   "TypeId": type_id,
                                                   "Description": description,
                                                   # "CreateTime": _current_time, 
                                                   "StartTime": None, 
                                                   "EndTime": None,
                                                   # "CreateBy":_create_by_id,
                                                   "Active":active,
                                                   "CreatedBy": _create_by_id,
                                                   "CreatedTime": _current_time }  )
    # _shots = zfused_api.zFused.get( "shot", 
    #                                 filter = {"ProjectId": project_id,"Code": code, "EpisodeId": episode_id, "SequenceId": sequence_id})
    if _status:
        return _value["Id"], True
    
    return "{} create error".format(name), False

def clear(lis):
    del lis[:]

def cache(project_id = [], extract_freeze = True):
    """ init project shots
    """
    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status")
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0})
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    if not project_id:
        _shots = zfused_api.zFused.get("shot", sortby = ["Code"], order = ["asc"])
        # _shot_historys = zfused_api.zFused.get("shot_history")
        _shot_tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityType": "shot", "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _shots = zfused_api.zFused.get("shot", filter = {"ProjectId__in": _project_ids, "StatusId__in": _status_ids}, sortby = ["Code"], order = ["asc"])
        # _shot_historys = zfused_api.zFused.get("shot_history", filter = {"ProjectId__in": _project_ids})
        _shot_tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityType": "shot", "ProjectId__in": _project_ids, "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])
    if _shots:
        list(map(lambda _shot: Shot.global_dict.setdefault(_shot["Id"],_shot), _shots))
        list(map(lambda _shot: clear(Shot.global_tasks[_shot["Id"]]) if Shot.global_tasks[_shot["Id"]] else False, _shots))
    # if _shot_historys:
    #     list(map(lambda _shot: Shot.global_historys[_shot["ShotId"]].append(_shot), _shot_historys))
    if _shot_tasks:
        from . import task
        list(map(lambda _task: Shot.global_tasks[_task["ProjectEntityId"]].append(_task), _shot_tasks))
        list(map(lambda _task: task.Task.global_dict.setdefault(_task["Id"],_task), _shot_tasks))
        
    # cache tags
    _str_shot_ids = [str(_shot_id) for _shot_id in Shot.global_dict.keys()]
    _tag_links = zfused_api.zFused.get("tag_link", filter = {"LinkObject": "shot", "LinkId__in": "|".join(_str_shot_ids)})
    if _tag_links:
        for _tag_link in  _tag_links:
            _shot_id = _tag_link["LinkId"]
            Shot.global_tags[_shot_id].append(_tag_link["TagId"])
    return _shots

def cache_from_ids(ids, extract_freeze = True):
    _s_t = time.clock()

    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status")
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0})
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    ids = "|".join(map(str, ids))
    _shots = zfused_api.zFused.get("shot", filter = {"Id__in": ids, "StatusId__in": _status_ids})
    _shot_tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityType": "shot", "ProjectEntityId__in": ids, "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])
    if _shots:
        list(map(lambda _shot: Shot.global_dict.setdefault(_shot["Id"],_shot), _shots))
        list(map(lambda _shot: clear(Shot.global_tasks[_shot["Id"]]) if Shot.global_tasks[_shot["Id"]] else False, _shots))
    if _shot_tasks:
        from . import task
        list(map(lambda _task: Shot.global_tasks[_task["ProjectEntityId"]].append(_task), _shot_tasks))
        list(map(lambda _task: task.Task.global_dict.setdefault(_task["Id"],_task), _shot_tasks))
    return _shots


class Shot(_Entity):
    global_dict = {}
    task_dict = {}
    global_tasks = defaultdict(list)
    global_historys = defaultdict(list)
    global_tags = defaultdict(list)  
    def __init__(self, entity_id, entity_data = None):
        super(Shot, self).__init__("shot", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("shot", self._id)
                if not _data:
                    logger.error("shot id {0} not exists".format(self._id))
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

    def description(self):
        return self._data["Description"]

    def file_code(self):
        """ task version file name

        :rtype: str
        """
        return self.full_code().replace("/", "_")
        
    def full_code(self):
        """
        get full path code

        rtype: str
        """
        _code = self._data["Code"]
        if self._data["SequenceId"]:
            _sequence_code = zfused_api.sequence.Sequence(self._data["SequenceId"]).full_code()
            return u"{}/{}".format(_sequence_code, _code)
        elif self._data["EpisodeId"]:
            _episode_code = zfused_api.episode.Episode(self._data["EpisodeId"]).full_code()
            return u"{}/{}".format(_episode_code, _code)
        else:
            return _code

    def full_name(self):
        """
        get full path name

        rtype: str
        """
        _name = self._data["Name"]
        if self._data["SequenceId"]:
            _sequence_name = zfused_api.sequence.Sequence(self._data["SequenceId"]).full_name()
            return u"{}/{}".format(_sequence_name, _name)
        elif self._data["EpisodeId"]:
            _episode_name = zfused_api.episode.Episode(self._data["EpisodeId"]).full_name()
            return u"{}/{}".format(_episode_name, _name)
        else:
            return _name

    def full_name_code(self):
        """
        get full path name and code

        rtype: str
        """
        return u"{}({})".format(self.full_name(), self.full_code())

    def type(self):
        """get type handle
        """
        _type_id = self._data.get("TypeId")
        if _type_id:
            return zfused_api.types.Types(_type_id)
        return None

    def project(self):
        _project_id = self._data.get("ProjectId")
        if _project_id:
            return zfused_api.project.Project(_project_id)
        return None

    def project_id(self):
        """ get project id

        """
        return self._data["ProjectId"]

    def status_id(self):
        """ get status id 
        
        """
        return self._data["StatusId"]

    def level(self):
        """ get shot level

        """
        return self._data["Level"]

    def start_frame(self):
        """ get start frame
        """
        return self._data["FrameStart"]

    def end_frame(self):
        """ get end frame
        """
        return self._data["FrameEnd"]

    def start_time(self):
        """ get start time

        rtype: datetime.datetime
        """
        _time_text = self._data["StartTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def end_time(self):
        """ get end time

        rtype: datetime.datetime
        """
        _time_text = self._data["EndTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def create_time(self):
        """ get create time

        """
        _time_text = self._data["CreateTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def sequence_id(self):
        return self._data.get("SequenceId")

    def sequence(self):
        _sequence_id = self.sequence_id()
        if _sequence_id:
            return zfused_api.sequence.Sequence(_sequence_id)
        return None

    def episode_id(self):
        return self._data.get("EpisodeId")

    def episode(self):
        _episode_id = self.episode_id()
        if _episode_id:
            return zfused_api.episode.Episode(_episode_id)
        return None

    def default_path(self):
        return r"{}/{}".format(self.object(), self.full_code())

    def path(self):
        _path = self.default_path()
        # project entity
        _project_entity = zfused_api.zFused.get("project_entity", filter = { "ProjectId": self._data.get("ProjectId"),
                                                                             "Code": self.object()} )
        if _project_entity:
            _project_entity = _project_entity[0]
            _custom_path = _project_entity.get("CustomPath")
            if _custom_path:
                _path = self.get_custom_path(_custom_path)
        return _path

    def production_path(self):
        """
        get shot production path

        rtype: str
        """
        _project_production_path = self.project().production_path()
        _path = "{}/{}".format(_project_production_path, self.path())
        return _path

    def transfer_path(self):
        _project_transfer_path = self.project().transfer_path()
        _path = "{}/{}".format(_project_transfer_path, self.path())
        return _path

    def backup_path(self):
        """
        get shot backup path

        rtype: str
        """
        _project_backup_path = self.project().backup_path()
        _path = "{}/{}".format(_project_backup_path, self.path())
        return _path

    def work_path(self, absolute = True):
        """
        get shot work path

        rtype: str
        """
        if absolute:
            _project_work_path = self.project().work_path()
            _path = "{}/{}".format(_project_work_path, self.path())
        else:
            _path = self.path()
        return _path

    def temp_path(self):
        """
        get shot publish path
        rtype: str
        """
        _publish_project_path = self.project().temp_path()
        _path = "{}/{}".format(_publish_project_path, self.path())
        return _path

    def image_path(self):
        _image_path = self.project().image_path()
        _path = "{}/{}".format(_image_path, self.path())
        return _path

    def cache_path(self):
        _cache_path = self.project().cache_path()
        _path = "{}/{}".format(_cache_path, self.path())
        return _path

    def review_path(self):
        """
        get shot review path

        rtype: str
        """
        _review_project_path = self.project().config["Review"]
        _path = "{}/shot/{}".format(_review_project_path, self.full_code())
        return _path

    def thumbnail(self):
        """ get thumbnai name
        """
        return self._data["Thumbnail"]

    def get_thumbnail(self, is_version = False):

        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None

    def notes(self):
        """ get tasks notes
                history
                version
                message
        :rtype: list
        """
        _notes = []
        # get task history
        _historys = self.get("shot_history", filter = {"ShotId": self._id})
        if _historys:
            _data = _historys[0]
            _note = {"user_id": _data["CreatedBy"],
                     "notes": _data,
                     "type": "create",
                     "time": _data["CreatedTime"]}
            _notes.append(_note)
            if len(_historys) > 1:
                for _history in _historys:
                    _his_notes = []
                    for _key, _value in _history.items():
                        if _key in ["CreatedTime", "Id", "ChangeTime", "ChangeBy"]:
                            continue
                        if _value != _data[_key]:
                            _note = { _key: _value }
                            _his_notes.append(_note)
                    if _his_notes:
                        _note = {"user_id": _data["ChangeBy"],
                                 "time": _data["ChangeTime"],
                                 "notes":_his_notes,
                                 "type": "change"}
                        _notes.append(_note)
                    _data = _history

        # get shot task
        _tasks = self.get("task", filter = {"ProjectEntityType": "shot", "ProjectEntityId": self._id})
        if _tasks:
            for _task in _tasks:
                _note = {"user_id": _task["CreatedBy"],
                         "time": _task["CreatedTime"],
                         "notes":_task,
                         "type": "task"}
                _notes.append(_note)

        def get_sort(elem):
            return elem["time"]
        _notes.sort(key = get_sort)

        return _notes

    def tag_ids(self):
        """ get shot link tag ids
        """
        if self._id not in self.global_tags.keys() or self.RESET:
            _tag_links = self.get("tag_link", filter = {"LinkObject": "shot", "LinkId": self._id})
            if not _tag_links:
                self.global_tags[self._id] = []
            else:
                self.global_tags[self._id] = [_tag_link["TagId"] for _tag_link in _tag_links]
        return self.global_tags[self._id]

    def versions(self):
        """ get task version
        
        :rtype: list
        """
        _versions = self.get("version", filter={ "ProjectEntityId": self._id, "ProjectEntityType": "shot" },
                                        sortby = ["Index"], order = ["asc"])
        if not _versions:
            return []
        return _versions

    def project_step_versions(self, project_step_id):
        """
        """
        # get task
        _tasks = zfused_api.zFused.get("task", filter = {"ProjectEntityId": self._id, "ProjectEntityType": "shot", "ProjectStepId": project_step_id})
        if not _tasks:
            return []
        _task = _tasks[0]
        _versions = self.get("version", filter={"ProjectEntityId": self._id, "ProjectEntityType": "shot", "TaskId": _task["Id"], "IsApproval": 1},
                                        sortby = ["Index"], order = ["asc"])
        if not _versions:
            return []
        return _versions

    def history(self):
        """ get history

        :rtype: list
        """
        _history = self.get("shot_history", filter = {"ShotId":self._id}, sortby = ["ChangeTime"], order = ["asc"])
        if _history:
            return _history
        else:
            return []

    def tasks(self, project_step_id_list = []):
        if self._id not in self.global_tasks.keys() or zfused_api.zFused.RESET:
            _tasks = self.get("task", filter = {"ProjectEntityType": "shot", "ProjectEntityId": self._id})
            self.global_tasks[self._id] = _tasks
        _tasks = self.global_tasks[self._id]
        if not _tasks:
            return []
        if project_step_id_list:
            __tasks = []
            for _task in _tasks:
                if _task["ProjectStepId"] in project_step_id_list:
                    __tasks.append(_task)
            return __tasks
        else:
            return _tasks

    def user_ids(self):
        _user_ids = [zfused_api.zFused.USER_ID]

        _project_step_ids = self.project().task_step_ids()
        if _project_step_ids:
            for _project_step_id in _project_step_ids:
                _project_step = zfused_api.step.ProjectStep(_project_step_id)
                _user_ids += _project_step.review_user_ids() + _project_step.cc_user_ids() + _project_step.approvalto_user_ids()

        _tasks = self.tasks()
        if _tasks:
            for _task in _tasks:
                _task = zfused_api.task.Task(_task.get("Id"))
                _project_step = _task.project_step()
                _user_ids += [_task.assigned_to()]

        _group_user_ids = list(set(_user_ids))
        # insert 
        _user_id = zfused_api.zFused.USER_ID
        _create_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _group_users = self.get("group_user", filter = {"EntityType":self._type, "EntityId":self._id})
        if _group_users:
            for _group_user in _group_users:
                _user_id_un = int(_group_user["UserId"])
                if _user_id_un in _group_user_ids:
                    _group_user_ids.remove(_user_id_un)
        if _group_user_ids:
            for _user_id_un in _group_user_ids:
                self.post( "group_user", { "EntityType":self._type, 
                                           "EntityId":self._id, 
                                           "UserId":_user_id_un,
                                           "CreatedBy": _user_id,
                                           "CreatedTime": _create_time })

        return list(set(_user_ids))

    def _tasks(self, project_step_id_list = []):
        """ get task 
        """
        if project_step_id_list:
            _ids = "|".join([str(_step_id) for _step_id in project_step_id_list])
            _key = "{}_{}".format(self._id, _ids)
            if _key in self.task_dict.keys():
                _tasks = self.task_dict[_key]
            else:
                _tasks = self.get("task", filter = { "ProjectEntityId": self._id, 
                                                     "ProjectEntityType": "shot", 
                                                     "ProjectStepId__in": _ids})
                self.task_dict[_key] = _tasks
        else:
            _tasks = self.get("task", filter = {"ProjectEntityId": self._id, 
                                                "ProjectEntityType": "shot"})
        if not _tasks:
            return []
        return _tasks

    def source_relatives(self):
        """ 
        """
        _relatives = zfused_api.zFused.get("relative", filter = {"TargetObject": "shot", 
                                                                  "TargetId": self._id})
        return set([(_relative["SourceObject"], _relative["SourceId"]) for _relative in _relatives if _relative["SourceId"] != self._id] if _relatives else [])

    def target_relatives(self):
        """
        """
        _relatives = zfused_api.zFused.get("relative", filter = {"SourceObject": "shot", 
                                                                  "SourceId": self._id})
        return set([(_relative["TargetObject"], _relative["TargetId"]) for _relative in _relatives if _relative["TargetId"] != self._id] if _relatives else [])

    # @classmethod
    # def load_task(cls, shot_id, project_step_id, task):
    #     _key = "{}_{}".format(shot_id, project_step_id)
    #     if not _key in cls.task_dict.keys():
    #         cls.task_dict[_key] = []        
    #     cls.task_dict[_key].append(task)

    def update_status(self, status_id):
        """ update project step check script
        
        :param status_id: 状态id
        :rtype: bool
        """
        self.global_dict[self._id]["StatusId"] = status_id
        self._data["StatusId"] = status_id
        v = self.put("shot", self._data["Id"], self._data, "status_id")
        if v:
            return True
        else:
            return False

    def update_thumbnail(self, _thumbnail):
        """
        """
        self.global_dict[self._id]["Thumbnail"] = _thumbnail
        self._data["Thumbnail"] = _thumbnail
        v = self.put("shot", self._data["Id"], self._data, "thumbnai")
        if v:
            return True
        else:
            return False

    def update_thumbnail_path(self, thumbnail_path):
        if self.global_dict[self._id]["ThumbnailPath"] == thumbnail_path:
            return True
        self.global_dict[self._id]["ThumbnailPath"] = thumbnail_path
        self._data["ThumbnailPath"] = thumbnail_path
        v = self.put("shot", self._data["Id"], self._data, "thumbnail_path")
        if v:
            return True
        else:
            return False

    def update_description(self, _description):
        self.global_dict[self._id]["Description"] = _description
        self._data["Description"] = _description
        v = self.put("shot", self._data["Id"], self._data, "description")
        if v:
            return True
        else:
            return False

    def update_start_frame(self, start_frame):
        if self._data.get("FrameStart") == start_frame:
            return True
        self.global_dict[self._id]["FrameStart"] = start_frame
        self._data["FrameStart"] = start_frame
        v = self.put("shot", self._data["Id"], self._data, "frame_start")
        if v:
            return True
        else:
            return False

    def update_end_frame(self, end_frame):
        if self._data.get("FrameEnd") == end_frame:
            return True
        self.global_dict[self._id]["FrameEnd"] = end_frame
        self._data["FrameEnd"] = end_frame
        v = self.put("shot", self._data["Id"], self._data, "frame_end")
        if v:
            return True
        else:
            return False

    def create_project_step_task(self, project_step_id):
        """ create default task

        """
        _project_step_id = project_step_id
        _project_id = self.project_id()
        _waiting_ids = zfused_api.status.waiting_status_ids()
        if not _waiting_ids:
            return False, "has not set waiting status"
        _status_id = _waiting_ids[0]
        # get project step id
        _project_step_handle = zfused_api.step.ProjectStep(_project_step_id)
        _step_id = _project_step_handle.data()["StepId"]

        # fix file code 
        _task_name = "{}_{}".format(self.file_code(), _project_step_handle.code()).replace("/", "_") 
        
        _assigned_id = 0
        _object = self.object()
        _project_entity_id = self.id()
        _software_id = _project_step_handle.data()["SoftwareId"]
        _create_id = zfused_api.zFused.USER_ID
        _current_time = "%s+00:00" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


        _task = self.get("task", filter = { "ProjectStepId": _project_step_id,
                                            "ProjectId":_project_id,
                                            "StepId":_step_id,
                                            "ProjectEntityType":_object,
                                            "ProjectEntityId":_project_entity_id,
                                            "SoftwareId":_software_id})
        if _task:
            return False, "%s is exists"%_task_name

        _task, _status = self.post(key = "task", data = { "SelfObject": "task", 
                                                          "Name": _task_name,
                                                          "ProjectStepId": _project_step_id, 
                                                          "ProjectId": _project_id,
                                                          "ProjectEntityType": _object,
                                                          "ProjectEntityId": _project_entity_id,
                                                          "StepId": _step_id,
                                                          "StatusId": _status_id,
                                                          "AssignedTo": _assigned_id,
                                                          "SoftwareId": _software_id,
                                                          "Description": "",
                                                          "EstimatedTime": 0,
                                                          "StartTime": None,
                                                          "DueTime": None,
                                                          "IsOutsource": 0,
                                                          "Active": "true",
                                                          "CreatedBy": _create_id,
                                                          "CreatedTime": _current_time })
                                                          
        if _status:
            self.global_tasks[self._id].append(_task)

            _task = zfused_api.task.Task(_task["Id"])
            zfused_api.im.submit_message( "user",
                                           zfused_api.zFused.USER_ID,
                                           self.user_ids(),
                                           { "msgtype": "new", 
                                             "new": {"object": "task", "object_id": _task.id()} }, 
                                           "new",
                                           self.object(),
                                           self.id(),
                                           self.object(),
                                           self.id() )

            return _task.id(), "%s create success"%_task_name
        return False,"%s create error"%_task_name    