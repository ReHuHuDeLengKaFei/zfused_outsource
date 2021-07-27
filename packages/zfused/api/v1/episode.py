# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from collections import defaultdict

import os
import time
import shutil
import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)

def new_episode(project_id, name, code, status_id, active = "true", create_by = None, description = None):
    """ create new episode

    """
    # asset is exists
    _episodes = zfused_api.zFused.get( "episode", 
                                     filter = {"ProjectId": project_id, "Code": code})
    if _episodes:
        return "{} is exists".format(name), False

    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if create_by:
        _create_by_id = create_by
    else:
        _create_by_id = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post(key = "episode", data = { "Name": name,
                                                   "Code": code,
                                                   "ProjectId": project_id,
                                                   "Description":description,
                                                   "StatusId":status_id,
                                                   # "CreateTime":_current_time, 
                                                   "StartTime":"0001-01-01T00:00:00Z", 
                                                   "EndTime":"0001-01-01T00:00:00Z",
                                                   # "CreateBy":_create_by_id,
                                                   "Active":active,
                                                   "CreatedBy":_create_by_id,
                                                   "CreatedTime":_current_time })
    
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
        _episodes = zfused_api.zFused.get("episode", sortby = ["Code"], order = ["asc"])
        _episode_tasks = zfused_api.zFused.get("task", filter = {"Object": "episode", "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _episodes = zfused_api.zFused.get("episode", filter = {"ProjectId__in": _project_ids, "StatusId__in": _status_ids}, sortby = ["Code"], order = ["asc"])
        _episode_tasks = zfused_api.zFused.get("task", filter = {"Object": "episode", "ProjectId__in": _project_ids, "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])
    if _episodes:
        list(map(lambda _episode: Episode.global_dict.setdefault(_episode["Id"], _episode), _episodes))
        list(map(lambda _episode: clear(Episode.global_tasks[_episode["Id"]]), _episodes))
    if _episode_tasks:
        from . import task
        list(map(lambda _task: Episode.global_tasks[_task["LinkId"]].append(_task), _episode_tasks))
        list(map(lambda _task: task.Task.global_dict.setdefault(_task["Id"],_task), _episode_tasks))

    # cache tags
    _str_episode_ids = [str(_episode_id) for _episode_id in Episode.global_dict.keys()]
    _tag_links = zfused_api.zFused.get("tag_link", filter = {"LinkObject": "episode", "LinkId__in": "|".join(_str_episode_ids)})
    if _tag_links:
        for _tag_link in  _tag_links:
            _episode_id = _tag_link["LinkId"]
            Episode.global_tags[_episode_id].append(_tag_link["TagId"])

    return _episodes

def cache_from_ids(ids, extract_freeze = True):
    _s_t = time.clock()

    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status")
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0})
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    ids = "|".join(map(str, ids))
    _episodes = zfused_api.zFused.get("episode", filter = {"Id__in": ids, "StatusId__in": _status_ids}, sortby = ["Code"], order = ["asc"])
    _episode_tasks = zfused_api.zFused.get("task", filter = {"Object": "episode", "LinkId__in": ids, "StatusId__in": _status_ids}, sortby = ["ProjectStepId"], order = ["asc"])

    if _episodes:
        list(map(lambda _episode: Episode.global_dict.setdefault(_episode["Id"],_episode), _episodes))
        list(map(lambda _episode: clear(Episode.global_tasks[_episode["Id"]]) if Episode.global_tasks[_episode["Id"]] else False, _episodes))
    if _episode_tasks:
        from . import task
        list(map(lambda _task: Episode.global_tasks[_task["LinkId"]].append(_task), _episode_tasks))
        list(map(lambda _task: task.Task.global_dict.setdefault(_task["Id"],_task), _episode_tasks))
    return _episodes


# class Asset(_Entity):
#     def __init__(self, entity_id, entity_data = None):
#         super(Asset, self).__init__("asset", entity_id, entity_data)

class Episode(_Entity):
    global_dict = {}
    global_tasks = defaultdict(list)
    global_historys = defaultdict(list)
    task_dict = {}
    global_tags = {}
    def __init__(self, entity_id, entity_data = None):
        super(Episode, self).__init__("episode", entity_id, entity_data)

# class Episode(zfused_api.zFused):
#     global_dict = {}
#     global_tasks = defaultdict(list)
#     global_historys = defaultdict(list)
#     task_dict = {}
#     global_tags = {}
#     def __init__(self, id, data = None):
#         self._id = id
#         self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("episode", self._id)
                if not _data:
                    logger.error("episode id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    # def object(self):
    #     return "episode"

    # def id(self):
    #     return self._id

    # def data(self):
    #     return self._data

    # def code(self):
    #     """
    #     get code

    #     rtype: str
    #     """
    #     return u"{}".format(self._data["Code"])   

    # def name(self):
    #     """
    #     get name

    #     rtype: str
    #     """
    #     return u"{}".format(self._data["Name"])

    # def name_code(self):
    #     """
    #     get name code

    #     rtype: str
    #     """
    #     return u"{}({})".format(self.name(), self.code())

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
        return u"{}".format(self._data["Code"]) 

    def full_name(self):
        """
        get full path name

        rtype: str
        """
        return u"{}".format(self._data["Name"])

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
        """ get asset level

        """
        return self._data["Level"]

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
        get episode production path

        rtype: str
        """
        _production_project_path = self.project().production_path()
        _path = "{}/{}".format(_production_project_path, self.path())
        return _path

    def backup_path(self):
        """
        get episode backup path

        rtype: str
        """
        _backup_project_path = self.project().backup_path()
        _path = "{}/{}".format(_backup_project_path, self.path())
        return _path

    def work_path(self, absolute = True):
        """
        get episode work path

        rtype: str
        """
        _work_project_path = self.project().work_path()
        _path = "{}/{}".format(_work_project_path, self.path())
        return _path

    def temp_path(self):
        """
        get episode publish path

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
        get episode review path

        rtype: str
        """
        _review_project_path = self.project().config["Review"]
        _path = "{}/{}".format(_review_project_path, self.path())
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

        # if self._data.get("Thumbnail"):
        #     _thumbnail = self._data["Thumbnail"]
        #     _full_code = self.full_code()
        #     _production_path = zfused_api.project.Project(self._data["ProjectId"]).config["Root"]
        #     _production_file = "{0}/episode/{1}/{2}".format(_production_path, _full_code, _thumbnail)
        #     _local_path = zfused_api.project.Project(self._data["ProjectId"]).config["LocalRoot"]
        #     _local_file = "{0}/episode/{1}/{2}".format(_local_path, _full_code, _thumbnail)
            
        #     #return _production_file
        #     # 是否需要宝贝到本机 ???
        #     if os.path.exists(_production_file):
        #         if not os.path.isfile(_local_file):
        #             _path = os.path.dirname(_local_file)
        #             if not os.path.isdir(_path):
        #                 os.makedirs(_path)
        #             shutil.copy(_production_file, _local_file)
        #         return _local_file
        #     else:
        #         return None
        # else:
        #     if is_version:
        #         _versions = self.get("version", filter = {"LinkId":self._id,"Object":"episode"})
        #         if _versions:
        #             _ver = _versions[-1]
        #             import version
        #             _ver_handle = version.Version(_ver["Id"], _ver)
        #             return _ver_handle.GetThumbnail()
        # return None

    def notes(self):
        """ get tasks notes
                history
                version
                message
        :rtype: list
        """
        _notes = []
        # get task history
        _historys = self.get("episode_history", filter = {"EpisodeId": self._id})
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
                        _note = {"user_id": _history["ChangeBy"],
                                 "time": _history["ChangeTime"],
                                 "notes":_his_notes,
                                 "type": "change"}
                        _notes.append(_note)
                    _data = _history

        # get asset task
        _tasks = self.get("task", filter = {"Object": "episode", "LinkId": self._id})
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
        """ get asset link tag ids
        """
        if self._id not in self.global_tags or self.RESET:
            # _historys = self.get("tag_link", filter = {"TaskId":self._id}, sortby = ["ChangeTime"], order = ["asc"])
            _tag_links = self.get("tag_link", filter = {"LinkObject": "asset", "LinkId": self._id})
            if _tag_links:
                self.global_tags[self._id] = [_tag_link["TagId"] for _tag_link in _tag_links]
            else:
                self.global_tags[self._id] = []
        return self.global_tags[self._id]

    def versions(self):
        """ get task version
        
        :rtype: list
        """
        _versions = self.get("version", filter={"LinkId": self._id, "Object": "episode"},
                                        sortby = ["Index"], order = ["asc"])
        if not _versions:
            return []
        return _versions

    def history(self):
        """ get history

        :rtype: list
        """
        _history = self.get("episode_history", filter = {"EpisodeId":self._id}, sortby = ["ChangeTime"], order = ["asc"])
        if _history:
            return _history
        else:
            return []

    def tasks(self, project_step_id_list = []):
        if self._id not in self.global_tasks or zfused_api.zFused.RESET:
            _tasks = self.get("task", filter = {"Object": "episode", "LinkId": self._id})
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

    def _tasks(self, project_step_id_list = []):
        """ get task 
        """
        if project_step_id_list:
            _ids = "|".join([str(_step_id) for _step_id in project_step_id_list])
            _key = "{}_{}".format(self._id, _ids)
            if _key in self.task_dict:
                _tasks = self.task_dict[_key]
            else:
                _tasks = self.get("task", filter = {"LinkId": self._id, 
                                                "Object": "episode", 
                                                "ProjectStepId__in": _ids})
                self.task_dict[_key] = _tasks
        else:
            _tasks = self.get("task", filter = {"LinkId": self._id, 
                                                "Object": "episode"})
        if not _tasks:
            return []
        return _tasks

    def source_relatives(self):
        """ 
        """
        _relatives = zfused_api.zFused.get("relative", filter = {"TargetObject": "episode", 
                                                                  "TargetId": self._id})
        return set([(_relative["SourceObject"], _relative["SourceId"]) for _relative in _relatives if _relative["SourceId"] != self._id] if _relatives else [])

    def target_relatives(self):
        """
        """
        _relatives = zfused_api.zFused.get("relative", filter = {"SourceObject": "episode", 
                                                                  "SourceId": self._id})
        return set([(_relative["TargetObject"], _relative["TargetId"]) for _relative in _relatives if _relative["TargetId"] != self._id] if _relatives else [])

    def update_status(self, status_id):
        """ update project step check script
        
        :param status_id: 状态id
        :rtype: bool
        """
        self.global_dict[self._id]["StatusId"] = status_id
        self._data["StatusId"] = status_id
        v = self.put("episode", self._data["Id"], self._data, "status_id")
        if v:
            return True
        else:
            return False

    def update_description(self, _description):
        self.global_dict[self._id]["Description"] = _description
        self._data["Description"] = _description
        v = self.put("episode", self._data["Id"], self._data, "description")
        if v:
            return True
        else:
            return False

    def update_thumbnail_path(self, thumbnail_path):
        if self.global_dict[self._id]["ThumbnailPath"] == thumbnail_path:
            return True
        self.global_dict[self._id]["ThumbnailPath"] = thumbnail_path
        self._data["ThumbnailPath"] = thumbnail_path
        v = self.put("episode", self._data["Id"], self._data, "thumbnail_path")
        if v:
            return True
        else:
            return False

    def create_project_step_task(self, project_step_id):
        """ create default task

        """
        _project_step_id = project_step_id
        # project id
        _project_id = self._data["ProjectId"]
        # get default status id
        _waiting_ids = zfused_api.status.waiting_status_ids()
        if not _waiting_ids:
            return
        _status_id = _waiting_ids[0]
        # get project step id
        _project_step_handle = zfused_api.step.ProjectStep(_project_step_id)
        _step_id = _project_step_handle.data()["StepId"]

        # 
        # fix file code 
        _task_name = "{}_{}".format(self.file_code(), _project_step_handle.code()).replace("/", "_") 
        
        _create_id = zfused_api.zFused.USER_ID
        _assigned_id = 0
        _object = "episode"
        _link_id = self._id
        _software_id = _project_step_handle.data()["SoftwareId"]
        _current_time = "%s+00:00" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


        _task = self.get("task", filter = { "ProjectStepId": _project_step_id,
                                            "ProjectId":_project_id,
                                            "StepId":_step_id,
                                            "Object":_object,
                                            "LinkId":_link_id,
                                            "SoftwareId":_software_id})
        if _task:
            return False, "%s is exists"%_task_name

        _task, _status = self.post(key = "task",data = { "SelfObject": "task", 
                                                         "Name": _task_name,
                                                         "ProjectStepId": _project_step_id, 
                                                         "ProjectId": _project_id,
                                                         "ProjectEntityType": _object,
                                                         "ProjectEntityId": _link_id,
                                                         "StepId": _step_id,
                                                         "StatusId": _status_id,
                                                         # "CreateBy": _create_id,
                                                         "AssignedTo": _assigned_id,
                                                         "Object": _object,
                                                         "LinkId": _link_id,
                                                         "SoftwareId": _software_id,
                                                         "Description": "",
                                                         "EstimatedTime": 0,
                                                         # "CreateTime": _current_time,
                                                         "StartTime": None,
                                                         "DueTime": None,
                                                         "IsOutsource": 0,
                                                         "Active": "true", 
                                                         "CreatedBy": _create_id,
                                                         "CreatedTime":_current_time })

        # _task = self.get("task", filter = { "SelfObject":"task",
        #                                    "Name": _task_name,
        #                                    "ProjectStepId": _project_step_id, 
        #                                    "ProjectId": _project_id,
        #                                    "StepId": _step_id,
        #                                    "StatusId": _status_id,
        #                                    "CreateBy": _create_id,
        #                                    "AssignedTo": _assigned_id,
        #                                    "Object": _object,
        #                                    "LinkId": _link_id,
        #                                    "SoftwareId":_software_id,
        #                                    "IsOutsource":0})
        if _status:
            return _task[0]["Id"], "%s create success"%_task_name
        return False,"%s create error"%_task_name    