# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function, unicode_literals

import ast
import json
import logging
import datetime

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def all_project_ids():
    """ get all project ids

    """
    _projects = zfused_api.zFused.get("project")
    if not _projects:
        return []
    _project_ids = [_project["Id"] for _project in _projects]
    return _project_ids

def all_projects():
    """ get all project 
        -- 排序,数据库需要更改
    """
    _projects = zfused_api.zFused.get("project")
    if not _projects:
        return []
    return [Project(_project["Id"]) for _project in _projects]

def new_project(name, code, status_id, is_outsource = 0, description = ""):
    """
    create project by name and code
    
    rtype: zfused_api.project.Project
    """
    _projects = zfused_api.zFused.get( "project", filter = {"Code": code})
    if _projects:
        return "{} is exists".format(name), False
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _create_by_id = zfused_api.zFused.USER_ID

    _value, _status = zfused_api.zFused.post( key = "project", 
                                              data = { "Name": name,
                                                       "Code": code,
                                                       "StatusId": status_id,
                                                       "IsOutsource": is_outsource,
                                                       "CreatedBy": _create_by_id,
                                                       "CreatedTime": _current_time } )
    if _status:
        _project_id = _value["Id"]
        # create project profile
        _value, _status = zfused_api.zFused.post( key = "project_profile", 
                                                  data = { "ProjectId": _project_id, 
                                                            "Color": "#FF0000",
                                                            "Introduction": description } )
        if not _status:
            zfused_api.zFused.delete( "project", _project_id )
            return "{} create error".format(name), False
        _project_profile_id = _value["Id"]
        # create project config
        _value, _status = zfused_api.zFused.post( key = "project_config", 
                                                  data = { "ProjectId": _project_id } )
        if not _status:
            zfused_api.zFused.delete( "project", _project_id )
            zfused_api.zFused.delete( "project_profile", _project_profile_id )
            return "{} create error".format(name), False
        # group user
        zfused_api.zFused.post( key = "group_user",
                                data = { "EntityType": "project",
                                         "EntityId": _project_id,
                                         "UserId": _create_by_id,
                                         "CreatedBy": _create_by_id,
                                         "CreatedTime": _current_time } )
        return _project_id, True
    return "{} create error".format(name), False

def cache(project_id_list = []):
    """ cache project database
    """
    Project.global_dict = {}
    Project.config_dict = {}
    Project.profile_dict = {}

    if project_id_list:
        _project_ids = "|".join(map(str,project_id_list))
        _projects = zfused_api.zFused.get("project", filter = {"Id__in": _project_ids}, sortby = ["Priority"], order = ["desc"])
        _project_profiles = zfused_api.zFused.get("project_profile", filter = {"ProjectId__in": _project_ids})
        _project_configs = zfused_api.zFused.get("project_config", filter = {"ProjectId__in": _project_ids})
    else:
        _projects = zfused_api.zFused.get("project", sortby = ["Priority"], order = ["desc"])
        _project_profiles = zfused_api.zFused.get("project_profile")
        _project_configs = zfused_api.zFused.get("project_config")

    if _projects:
        for _project in _projects:
            Project.global_dict[_project["Id"]] = _project
    if _project_configs:
        for _project_config in _project_configs:
            _project_id = _project_config["ProjectId"]
            Project.config_dict[_project_id] = _project_config
    if _project_profiles:
        for _project_profile in _project_profiles:
            _project_id = _project_profile["ProjectId"]
            Project.profile_dict[_project_id] = _project_profile

    return _projects


# class ProjectDocument(_Entity):
#     def __init__(self, entity_id, entity_data = None):
#         super(Project, self).__init__("project", entity_id, entity_data)


class Project(_Entity):

    global_dict = {}
    config_dict = {}
    profile_dict = {}


    @classmethod
    def new(cls, name, code, status_id, color, description = ""):
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID

        _projects = zfused_api.zFused.get( "project", filter = {"Code": code})
        if _projects:
            return "{} is exists".format(name), False

        _project, _status = zfused_api.zFused.post( key = "project", 
                                                data = { "Name": name,
                                                         "Code": code,
                                                         "StatusId": status_id,
                                                         "IsOutsource": 0,
                                                         "Priority": 0,
                                                         "CreatedBy": _created_by,
                                                         "CreatedTime": _created_time } )
        if not _status:
            return "{} create error".format(name), False

        _project_id = _project.get("Id")
        
        _project_profile, _status = zfused_api.zFused.post( key = "project_profile", 
                                                    data = { "ProjectId": _project_id, 
                                                            "Color": color,
                                                            "Introduction": description,
                                                            "CreatedBy": _created_by,
                                                            "CreatedTime": _created_time  } )
        if not _status:
            zfused_api.zFused.delete( "project", _project_id )
            return "{} create error".format(name), False

        _project_profile_id = _project_profile.get("Id")

        _project_config, _status = zfused_api.zFused.post( key = "project_config", 
                                                    data = { "ProjectId": _project_id,
                                                             "CreatedBy": _created_by,
                                                             "CreatedTime": _created_time } )
        if not _status:
            zfused_api.zFused.delete( "project", _project_id )
            zfused_api.zFused.delete( "project_profile", _project_profile_id )
            return "{} create error".format(name), False
        # group user
        zfused_api.zFused.post( key = "group_user",
                                data = { "EntityType": "project",
                                         "EntityId": _project_id,
                                         "UserId": _created_by,
                                         "CreatedBy": _created_by,
                                         "CreatedTime": _created_time } )
        return _project_id, True
        # return "{} create project error".format(name), False


    def __init__(self, entity_id, entity_data = None):
        super(Project, self).__init__("project", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            _data = self.get_one( "project", self._id )
            if not _data:
                logger.error("project id {0} is not exists".format(self._id))
                return
            self._data = _data
            _profile = self.get( "project_profile", filter = {"ProjectId": self._id} )
            if not _profile:
                logger.error("project id {0} is not exists".format(self._id))
                return
            self._profile = _profile[0]
            _config = self.get( "project_config", filter = { "ProjectId": self._id} )
            if not _config:
                logger.error("project id {0} is not exists".format(self._id))
                return
            self._config = _config[0]
            self.global_dict[self._id] = self._data
            self.profile_dict[self._id] = self._profile
            self.config_dict[self._id] = self._config
        else:
            self._data = self.global_dict[self._id]
            self._profile = self.profile_dict[self._id]
            self._config = self.config_dict[self._id]

            self.config = self._config
            self.profile = self._profile

    def full_code(self):
        """get full path code

        :rtype: str
        """
        return u"{}".format(self._data["Code"])

    def full_name(self):
        """get full path name

        :rtype: str
        """
        return u"{}".format(self._data["Name"])

    def full_name_code(self):
        """get full path name and code

        :rtype: str
        """
        return u"{}({})".format(self.full_name(), self.full_code())

    def color(self):
        """ return project color

        """
        _color = self._profile["Color"]
        if not _color:
            return "#FFFFFF"
        return self._profile["Color"]

    def status(self):
        return zfused_api.status.Status(self._data.get("StatusId"))

    def status_id(self):
        """ get status id 
        
        """
        return self._data["StatusId"]

    def start_time(self):
        """
        get start time

        rtype: datetime.datetime
        """
        _time_text = self._profile["StartTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def end_time(self):
        """ get end time

        rtype: datetime.datetime
        """
        _time_text = self._profile["EndTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def production_path(self):
        _production_path = self._config.get("ProductionPath")
        if not _production_path:
            _production_path = self._config.get("Root")
        return _production_path

    def transfer_path(self):
        _transfer_path = self._config.get("TransferPath")
        return _transfer_path

    def backup_path(self):
        _backup_path = self._config.get("BackupPath")
        if not _backup_path:
            _backup_path = self._config.get("Publish")
        return _backup_path

    def work_path(self):
        """ get project work path
        rtype: str
        """
        _work_path = self._config.get("WorkPath")
        if not _work_path:
            _work_path = self._config.get("LocalRoot")
        return _work_path

    def temp_path(self):
        """ get project publish path
        rtype: str
        """
        _temp_path = self._config.get("TempPath")
        if not _temp_path:
            _temp_path = self._config.get("LocalPublish")
        return _temp_path

    def image_path(self):
        return self._config.get("ImagePath")

    def cache_path(self):
        return self._config.get("CachePath")

    def farm_path(self):
        return self._config.get("FarmPath")

    def project_step_ids(self):
        """ get asset task step id

        :rtype: list
        """
        _steps = self.get("project_step", 
                          filter = {"ProjectId": self._id},
                          sortby = ["Sort"], order = ["asc"])
        if _steps:
            return [_step["Id"] for _step in _steps]
        return []

    def task_step_ids(self, object = None):
        """ get task step id by object

        :rtype: list
        """
        if not object or object == "task":
            _steps = self.get("project_step", 
                              filter = {"ProjectId": self._id},
                              sortby = ["Sort", "Object"], order = ["asc"])
        elif object:
            _steps = self.get("project_step", 
                              filter = {"ProjectId": self._id, "Object": object},
                              sortby = ["Sort", "Object"], order = ["asc"])
        if _steps:
            return [_step["Id"] for _step in _steps]
        return []

    def asset_type_ids(self):
        """get asset type

        :rtype: list
        """
        _types = self.get("project_type", filter = {"ProjectId": self._id}) 
        if _types:
            return [_type["TypeId"] for _type in _types]
        return []

    def assembly_attributes(self):
        """ get is assembly attrs
        
        :rtype: list
        """
        _steps = self.get("project_step", filter = {"ProjectId": self._id})
        if not _steps:
            return []
        _step_ids = [str(_step["Id"]) for _step in _steps]
        _attrs = self.get("step_attr_output", filter = {"ProjectStepId__in": "|".join(_step_ids),
                                                        "IsAssembly__gte": 1},
                                              sortby = ["IsAssembly"], order = ["desc"])

        if not _attrs:
            return []
        return _attrs

    def assembly_attribute_ids(self):
        """ get is assembly attr ids
        
        :rtype: list
        """
        _steps = self.get("project_step", filter = {"ProjectId": self._id})
        if not _steps:
            return []
        _step_ids = [str(_step["Id"]) for _step in _steps]
        _attrs = self.get("step_attr_output", filter = {"ProjectStepId__in": "|".join(_step_ids),
                                                        "IsAssembly__gte": 1},
                                              sortby = ["IsAssembly"], order = ["desc"])

        if not _attrs:
            return []
        return [_attr["Id"] for _attr in _attrs]

    def get_thumbnail(self):
        _thumbnail = self._profile["ThumbnailPath"]
        if _thumbnail.startswith("storage"):
            return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail.split("storage/")[-1])
        return None

    def update_thumbnail_path(self, thumbnail_path):
        if self.profile_dict[self._id]["ThumbnailPath"] == thumbnail_path:
            return True
        self.profile_dict[self._id]["ThumbnailPath"] = thumbnail_path
        self._profile["ThumbnailPath"] = thumbnail_path
        v = self.put("project_profile", self._profile["Id"], self._profile, "thumbnail_path", False)
        if v:
            return True
        else:
            return False

    def priority(self):
        return self._data.get("Priority")

    def update_priority(self, priority_index):
        """
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["Priority"] == priority_index:
            return True

        self.global_dict[self._id]["Priority"] = priority_index
        self._data["Priority"] = priority_index
        v = self.put("project", self._data["Id"], self._data, "priority")
        if v:
            return True
        else:
            return False

    def project_softwares(self):
        _project_softwares = self.get("project_software", filter = {"ProjectId": self._id})
        if _project_softwares:
            return [zfused_api.software.ProjectSoftware(_project_software.get("Id")) for _project_software in _project_softwares]
        return []

    def softwares(self):
        """获取项目制作软件
        """
        _project_softwares = self.get("project_software", filter = {"ProjectId": self._id})
        if _project_softwares:
            return [zfused_api.software.Software(_project_software.get("SoftwareId")) for _project_software in _project_softwares]
        return []

    def add_software(self, software_id):
        """添加制作软件
        """
        _softwares = self.get("project_software", filter = {"ProjectId": self._id, "SoftwareId": software_id})
        if _softwares:
            return

        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _create_by_id = zfused_api.zFused.USER_ID

        _value, _status = zfused_api.zFused.post( key = "project_software", 
                                                  data = { "ProjectId": self._id,
                                                           "SoftwareId": software_id,
                                                           "CreatedBy": _create_by_id,
                                                           "CreatedTime": _current_time } )
        if _status:
            _project_software_id = _value["Id"]
            return _project_software_id, True
        return "add software {} error".format(software_id), False

    def fps(self):
        return self._config.get("Fps")

    def resolution(self):
        return [self._config.get("ImageWidth"), self._config.get("ImageHeight")]

    def variables(self, key = "", default = {}):
        self._config = self.get_one( "project_config", self._config.get("Id") )
        _property = self._config.get("Variables")
        if not _property:
            return default
        _property = eval(_property)
        if key:
            if key not in _property:
                if default:
                    _value = default
                else:
                    _value = _property.get(key)
            else:
                _value = _property.get(key)

            # _value = _property.get(key)
            # if not _value:
            #     if default:
            #         _value = default
            
            return _value
        return _property

    def update_variables(self, key, value):
        _property = self.variables()
        _property[key] = value
        self._config["Variables"] = str(_property)
        v = self.put("project_config", self._config["Id"], self._config, "Variables")
        if v:
            return True
        else:
            return False

    @_Entity._recheck
    def search_match(self):
        return self._data.get("Match")

    @_Entity._recheck
    def refresh_match(self):
        _match = self.full_name_code()
        if self._data.get("Match") == _match:
            return True
        self.global_dict[self._id]["Match"] = _match
        self._data["Match"] = _match
        v = self.put("project", self._data["Id"], self._data, "match", False)
        if v:
            return True
        else:
            return False