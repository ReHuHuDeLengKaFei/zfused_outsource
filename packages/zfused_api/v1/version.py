# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import datetime
import logging
import re

from . import _Entity
import zfused_api
#from . import task

logger = logging.getLogger(__name__)

def cache(project_id):
    """ init project versions
    """
    Version.global_dict = {}
    if not project_id:
        _versions = zfused_api.zFused.get("version", sortby = ["Id"], order = ["desc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _versions = zfused_api.zFused.get("version", filter = {"ProjectId__in": _project_ids}, sortby = ["Id"], order = ["desc"])
    if _versions:
        list(map(lambda _version: Version.global_dict.setdefault(_version["Id"],_version), _versions))
    return _versions

def cache_from_ids(ids):
    ids = "|".join(map(str, ids))
    _versions = zfused_api.zFused.get("version", filter = {"Id__in": ids})
    if _versions:
        list(map(lambda _version: Version.global_dict.setdefault(_version["Id"],_version), _versions))
    return _versions


class Version(_Entity):
    global_dict = defaultdict(dict)
    global_production = defaultdict(int)
    def __init__(self, entity_id, entity_data = None):
        super(Version, self).__init__("version", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("version", self._id)
                if not _data:
                    logger.error("version id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]
                self._data = self.global_dict[self._id]

        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data

    def code(self):
        return self.name()

    @_Entity._recheck
    def description(self):
        return self._data.get("Description")
    
    @_Entity._recheck
    def link_object(self):
        return self._data.get("ProjectEntityType")

    @_Entity._recheck
    def link_id(self):
        return self._data.get("ProjectEntityId")

    @_Entity._recheck
    def user_id(self):
        return self._data.get("UserId")

    @_Entity._recheck
    def assigned_to(self):
        return self.global_dict[self._id]["UserId"]

    @_Entity._recheck
    def project_step(self):
        return zfused_api.step.ProjectStep(self._data.get("ProjectStepId"))
    
    @_Entity._recheck
    def project_step_id(self):
        """ 
        """
        return self.global_dict[self._id].get("ProjectStepId")

    @_Entity._recheck
    def project(self):
        return zfused_api.project.Project(self._data.get("ProjectId"))

    @_Entity._recheck
    def project_id(self):
        return self._data.get("ProjectId")

    @_Entity._recheck
    def project_entity(self):
        return zfused_api.objects.Objects(self._data.get("ProjectEntityType"), self._data.get("ProjectEntityId"))

    @_Entity._recheck
    def task(self):
        return zfused_api.task.Task(self._data.get("TaskId"))

    @_Entity._recheck
    def task_id(self):
        return self._data.get("TaskId")

    @_Entity._recheck
    def project_entity_type(self):
        return self._data.get("ProjectEntityType")

    def project_entity_id(self):
        return self._data.get("ProjectEntityId")

    def software_id(self):
        return self.task().software_id()

    def software(self):
        return self.task().software()

    def full_code(self):
        """
        get full path code
        rtype: str
        """
        return ""

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

    def file_code(self):
        """ get file name
        :rtype: str
        """
        return self.project_entity().file_code()

    def index(self):
        return self._data["Index"]

    def version(self):
        return self._data["Index"]

    def submission_time(self):
        """ 提交时间
        """
        _time_text = self._data["CreatedTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def production_path(self):
        """ get version task production path
        rtype: str
        """
        return self.task().production_path()

    def path(self):
        """ get version path

        rtype: str
        """
        _task_backup_path = zfused_api.task.Task(self._data["TaskId"]).backup_path()
        return _task_backup_path

    def link_entity(self):
        return(self.global_dict[self._id]["ProjectEntityType"], self.global_dict[self._id]["ProjectEntityId"])

    def entity(self):
        return(self.global_dict[self._id]["ProjectEntityType"], self.global_dict[self._id]["ProjectEntityId"])
    
    def thumbnail(self):
        """ get thumbnail
        """
        return self.global_dict[self._id]["Thumbnail"]

    # def get_thumbnail(self):
    #     """ get version thumbnail file
    
    #     rtype: str
    #     """
    #     _path = zfused_api.task.Task(self._data["TaskId"]).backup_path()
    #     _thumbnail = self._data.get("Thumbnail")
    #     if _thumbnail:
    #         _thumbnail_path = u"{}{}".format(_path, _thumbnail)            
    #         return _thumbnail_path
    #     return ""

    def get_thumbnail(self, is_version = True):

        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None

        # _thumbnail = self._data.get("Thumbnail")
        # _thumbnail_path = self._data.get("ThumbnailPath")
        # if _thumbnail_path:
        #     if _thumbnail_path.startswith("storage"):
        #         return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        # else:
        #     _path = zfused_api.task.Task(self._data["TaskId"]).backup_path()
        #     # _thumbnail = self._data.get("Thumbnail")
        #     if _thumbnail:
        #         _thumbnail_path = u"{}{}".format(_path, _thumbnail)            
        #         return _thumbnail_path
        # return None

    def without_version_version(self):
        _path = zfused_api.task.Task(self._data["TaskId"]).production_path()
        _file_name = self._data["FilePath"]
        _re_com = re.compile("\d{4}")
        _re_list = re.findall(_re_com, _file_name)
        if _re_list:
            for _re in _re_list:
                _file_name = _file_name.replace(".{}".format(_re), "")
        _file = "{}/file/{}".format(_path, _file_name)
        return _file

    def production_file(self, attr_code = "file"):
        """ get production file
        :rtype: str
        """
        if self.is_external():
            return self._data.get("FilePath")
        _task_handle = zfused_api.task.Task(self._data["TaskId"])
        _path = _task_handle.production_path()
        _file_name = self._data["FilePath"]

        _work_with_no_version = self.project().variables("work_with_no_version", 0)
        if _work_with_no_version:
            _file_name = _file_name.split(".")
            _file_name.pop(-2)
            _file_name = ".".join(_file_name)

        _file = "{}/{}/{}".format(_path, attr_code, _file_name)
        return _file

    def backup_file(self):
        """ get backup file
        :rtype: str
        """
        # _path = zfused_api.task.Task(self._data["TaskId"]).backup_path()
        _task_path = self.task().backup_path()
        _file_name = self._data.get("FilePath")
        _file = "{}{}".format(_task_path, _file_name)
        return _file

    def work_file(self):
        """ get work file
        :rtype: str
        """
        _path = zfused_api.task.Task(self._data["TaskId"]).work_path()
        _file_name = self._data["FilePath"]
        _file = "{}{}".format(_path, _file_name)
        return _file

    def is_approval(self):
        return self.global_dict[self._id]["IsApproval"]

    def is_production_del(self):
        if self._id not in self.global_production.keys():
            return 0, "undetected"
        return self.global_production[self._id], ""

    def is_production(self):
        if "IsProduction" not in self.global_dict[self._id]:
            return 0
        return self.global_dict[self._id]["IsProduction"]

    def analy_is_production(self):
        """ 判定当前吧版本是否为产品最终版本
        """
        _task_handle = zfused_api.task.Task(self._data["TaskId"])
        _message = ""
        # get version
        _all_versions = _task_handle.versions()

        _is_production = 1
        if self._data["Index"] == len(_all_versions):
            _is_production = 1
        else:
            _is_production = -1
        self.global_dict[self._id]["IsProduction"] = _is_production

    @_Entity._recheck
    def update_approval(self, is_approval):
        if self._data.get("IsApproval") == is_approval:
            return 

        self.global_dict[self._id]["IsApproval"] = is_approval
        self._data["IsApproval"] = is_approval
        v = self.put("version", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    @_Entity._recheck
    def update_negligible(self, is_negligible):
        if self._data.get("IsNegligible") == is_negligible:
            return 

        self.global_dict[self._id]["IsNegligible"] = is_negligible
        self._data["IsNegligible"] = is_negligible
        v = self.put("version", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    def approval_status(self):
        return str(self.global_dict[self._id]["IsApproval"])

    def is_external(self):
        return self._data.get("IsExternal")

    def set_pass(self):
        _approval_index = 1

        if _approval_index == 1:
            _reply_text = {'text': '审批通过', 'msgtype': 'rich-text'} 
        elif _approval_index == -1:
            _reply_text = {'text': '审批未通过', 'msgtype': 'rich-text'}
        else:
            _reply_text = {'text': '等待审批', 'msgtype': 'rich-text'}

        if self.data()["IsApproval"] != _approval_index:
            self.update_approval(_approval_index)
            try:
                _approval_ids = zfused_api.zFused.get("approval", filter = {"Object":"version","ObjectId":self.data()["Id"]})
                if _approval_ids:
                    _approval_handle = zfused_api.approval.Approval(_approval_ids[-1]["Id"])
                    _approval_handle.update_approval(str(_approval_index))
                    _task_handle = zfused_api.task.Task(self.data().get("TaskId"))
                    _project_step_handle = zfused_api.step.ProjectStep( _task_handle.data().get("ProjectStepId") )
                    _receiver_ids = _project_step_handle.approvalto_user_ids() + _project_step_handle.cc_user_ids()
                    _user_id = zfused_api.zFused.USER_ID
                    _message_id = zfused_api.im.submit_message( "user",
                                                                _user_id,
                                                                _receiver_ids,
                                                                { "msgtype": "rich-text",
                                                                  "rich-text": _reply_text },
                                                                "reply", 
                                                                "approval",
                                                                _approval_handle.id(),
                                                                "task",
                                                                _task_handle.id() )
                    _task_handle.update_approval_status(str(_approval_index))
            except:
                pass

    def set_no_pass(self):
        _approval_index = -1

        if _approval_index == 1:
            _reply_text = {'text': '审批通过', 'msgtype': 'rich-text'} 
        elif _approval_index == -1:
            _reply_text = {'text': '审批未通过', 'msgtype': 'rich-text'}
        else:
            _reply_text = {'text': '等待审批', 'msgtype': 'rich-text'}

        if self.data()["IsApproval"] != _approval_index:
            self.update_approval(_approval_index)
            try:
                _approval_ids = zfused_api.zFused.get("approval", filter = {"Object":"version","ObjectId":self.data()["Id"]})
                if _approval_ids:
                    _approval_handle = zfused_api.approval.Approval(_approval_ids[-1]["Id"])
                    _approval_handle.update_approval(str(_approval_index))
                    _task_handle = zfused_api.task.Task(self.data().get("TaskId"))
                    _project_step_handle = zfused_api.step.ProjectStep( _task_handle.data().get("ProjectStepId") )
                    _receiver_ids = _project_step_handle.approvalto_user_ids() + _project_step_handle.cc_user_ids()
                    _user_id = zfused_api.zFused.USER_ID
                    _message_id = zfused_api.im.submit_message( "user",
                                                                _user_id,
                                                                _receiver_ids,
                                                                { "msgtype": "rich-text",
                                                                  "rich-text": _reply_text },
                                                                "reply", 
                                                                "approval",
                                                                _approval_handle.id(),
                                                                "task",
                                                                _task_handle.id() )
                    _task_handle.update_approval_status(str(_approval_index))
            except:
                pass


    @_Entity._recheck
    def search_match(self):
        return self._data.get("Match")

    @_Entity._recheck
    def refresh_match(self):
        _match = u"{};{};{}".format(self._data.get("Name"), self.project_step().name_code(), self.project_entity().full_name_code())
        if self._data.get("Match") == _match:
            return True
        self.global_dict[self._id]["Match"] = _match
        self._data["Match"] = _match
        v = self.put("version", self._data["Id"], self._data, "match", False)
        if v:
            return True
        else:
            return False