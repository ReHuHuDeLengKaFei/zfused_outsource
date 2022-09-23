# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import time
import datetime
import logging

from . import _Entity
import zfused_api
#from . import task

logger = logging.getLogger(__name__)

def cache(project_id = []):
    """ init project versions
    """
    Report.global_dict = {}
    if not project_id:
        _reports = zfused_api.zFused.get("report", sortby = ["Id"], order = ["desc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _reports = zfused_api.zFused.get("report", filter = {"ProjectId__in": _project_ids}, sortby = ["Id"], order = ["desc"])
    if _reports:
        list(map(lambda _report: Report.global_dict.setdefault(_report["Id"],_report), _reports))
    return _reports

def cache_from_ids(ids):
    ids = "|".join(map(str, ids))
    _reports = zfused_api.zFused.get("report", filter = {"Id__in": ids})
    if _reports:
        list(map(lambda _report: Report.global_dict.setdefault(_report["Id"],_report), _reports))
    return _reports

class Report(_Entity):
    global_dict = defaultdict(dict)
    global_production = defaultdict(int)
    def __init__(self, entity_id, entity_data = None):
        super(Report, self).__init__("report", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("report", self._id)
                if not _data:
                    logger.error("report id {0} not exists".format(self._id))
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

    def code(self):
        return self.name()

    def description(self):
        return self._data["Description"]

    def link_object(self):
        return self._data["EntityType"]

    def link_id(self):
        return self._data["EntityId"]

    def user_id(self):
        return self.global_dict[self._id]["CreatedBy"]

    def assigned_to(self):
        """
        """
        return self.global_dict[self._id]["CreatedBy"]

    def project(self):
        return zfused_api.project.Project(self._data.get("ProjectId"))

    def project_id(self):
        return self._data.get("ProjectId")

    def project_step(self):
        return zfused_api.step.ProjectStep(self._data.get("ProjectStepId"))
    
    def project_step_id(self):
        """ 
        """
        return self._data.get("ProjectStepId")

    def project_entity(self):
        return zfused_api.objects.Objects(self._data.get("ProjectEntityType"), self._data.get("ProjectEntityId"))

    def task(self):
        return zfused_api.task.Task(self._data.get("TaskId"))

    def task_id(self):
        return self._data.get("TaskId")

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

    # def file_code(self):
    #     """ get file name

    #     :rtype: str
    #     """
    #     _link_handle = zfused_api.objects.Objects(self._data["Object"], self._data["LinkId"])
    #     return _link_handle.file_code()

    def index(self):
        return self._data["Index"]

    def version(self):
        return self._data["Index"]

    # def created_by(self):
    #     return self.global_dict[self._id]["CreatedBy"]

    # def created_time(self):
    #     """ get create time

    #     rtype: datetime.datetime
    #     """
    #     _time_text = self._data["CreatedTime"]
    #     if _time_text.startswith("0001"):
    #         return None
    #     _time_text = _time_text.split("+")[0].replace("T", " ")
    #     return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def create_time(self):
        """ get create time

        rtype: datetime.datetime
        """
        _time_text = self._data["CreatedTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def submission_time(self):
        """ 提交时间
        """
        _time_text = self._data["CreatedTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def production_path(self):
        """ get asset production path

        rtype: str
        """
        _production_project_path = zfused_api.project.Project(self._data["ProjectId"]).config["Root"]

        project_path = self.get("project_config", filter= {"Id":self._data["ProjectId"]})[0]["Root"]

        #get path
        version_path = self._data["FilePath"]

        #asset_name = self._data["Code"]
        step_name = self.Get("type", filter = {"Id":self._data["TypeId"]})[0]["Code"]
        project_name = self.Get("project_config", filter = {"Id":self._data["ProjectId"]})[0]["Publish"]

        linkHandle = self.Get(self._data["Object"], filter = {"Id":self._data["LinkId"]})
        if self._data["Object"] == "asset":
            linkHandle = asset.Asset(self._data["LinkId"])
        elif self._data["Object"] == "shot":
            linkHandle = shot.Shot(self._data["LinkId"]) 
        elif self._data["Object"] == "sequence":
            linkHandle = sequence.Sequence(self._data["LinkId"]) 
        path = linkHandle.GetPath()
        taskHandle.GetPath()

        return "%s/%s/%s"%(path,step_name,asset_name)


    def path(self):
        """ get version path

        rtype: str
        """
        _task_backup_path = zfused_api.task.Task(self._data["TaskId"]).backup_path()
        return _task_backup_path


    def thumbnail(self):
        """ get thumbnail
        """
        return self.global_dict[self._id]["ThumbnailPath"]

    def link_entity(self):
        return(self.global_dict[self._id]["Object"], self.global_dict[self._id]["LinkId"])

    def get_thumbnail(self):
        """ get version thumbnail file
    
        rtype: str
        """
        _thumbnail = self._data.get("ThumbnailPath")
        if _thumbnail:
            if _thumbnail.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail.split("storage/")[-1])        
        return ""

    def production_file(self):
        """ get production file

        :rtype: str
        """
        _path = zfused_api.task.Task(self._data["TaskId"]).production_path()
        _file_name = self._data["FilePath"]
        _file = "{}/file/{}".format(_path, _file_name)
        return _file

    def backup_file(self):
        """ get backup file

        :rtype: str
        """
        _path = zfused_api.task.Task(self._data["TaskId"]).backup_path()
        _file_name = self._data["FilePath"]
        _file = "{}{}".format(_path, _file_name)
        return _file

    def work_file(self):
        """ get work file

        :rtype: str
        """
        _path = zfused_api.task.Task(self._data["TaskId"]).work_path()
        _file_name = self._data["FilePath"]
        _file = "{}{}".format(_path, _file_name)
        return _file

    def link_files(self):
        _file_keys = zfused_api.zFused.get("file_link", filter = {"EntityType": "report", "EntityId": self._id})
        if not _file_keys:
            return None
        _file_keys = [_file_key["FileKey"] for _file_key in _file_keys]
        return zfused_api.zFused.get("file", filter = {"MD5__in":"|".join(_file_keys)})

    def update_approval(self, is_approval):
        self.global_dict[self._id]["IsApproval"] = is_approval
        self._data["IsApproval"] = is_approval
        v = self.put("report", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    def is_approval(self):
        return self.global_dict[self._id]["IsApproval"]

    def review_status(self):
        return str(self.global_dict[self._id]["IsApproval"])

    def layer_id(self):
        return self._data.get("LayerId")

    def set_pass(self):

        _review = zfused_api.zFused.get("review", filter = {"EntityType":"report", "EntityId": self._id})
        if not _review:
            self.update_approval(-1)
            self.task().update_review_status("-1")
            return

        _review_id = _review[0].get("Id")
        _review_handle = zfused_api.review.Review(_review_id)
        _task_handle = zfused_api.task.Task(self._data.get("TaskId"))
        
        # if _review_handle.data()["Status"] == "1":
        #     return

        _review_process_name = ""
        _review_process_id = _review_handle.data().get("ReviewProcessId")
        if _review_process_id:
            _review_process_handle = zfused_api.review.ReviewProcess(_review_process_id)
            _review_process_name = _review_process_handle.name()
        _review_handle.submit("1")
        _next_review_process_id = _review_handle.data().get("ReviewProcessId")
        if _next_review_process_id == _review_process_id:
            self.update_approval(1)
            
        currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._reply(self, _review_id, {}, {"name":_review_process_name,"value":1,"submitter_id":zfused_api.zFused.USER_ID,"submit_time":currentTime})

        _task_handle.update_review_process(_next_review_process_id)
        if _next_review_process_id == _review_process_id:
            _task_handle.update_review_status("1")

    
    def set_no_pass(self):
        _review = zfused_api.zFused.get("review", filter = {"EntityType":"report", "EntityId":self._id})
        if not _review:
            self.update_approval(-1)
            self.task().update_review_status("-1")
            return

        _review_id = _review[0]["Id"]
        _review_handle = zfused_api.review.Review(_review_id)

        # if _review_handle.data()["Status"] == "-1":
        #     return

        _review_process_name = ""
        _review_process_id = _review_handle.data().get("ReviewProcessId")
        if _review_process_id:
            _review_process_handle = zfused_api.review.ReviewProcess(_review_process_id)
            _review_process_name = _review_process_handle.name()
        _review_handle.submit("-1")
        self.update_approval(-1)

        currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._reply(self, _review_id, {}, {"name":_review_process_name,"value":-1,"submitter_id":zfused_api.zFused.USER_ID,"submit_time":currentTime})
    
        _task_handle = zfused_api.task.Task(self._data.get("TaskId"))
        _task_handle.update_review_process(_review_process_id)
        _task_handle.update_review_status("-1")

    def _reply(self, report_handle, review_id, message, respond = None, clear = True):
        """ 
        """
        _reply_text = message

        _task_id = report_handle.data()["TaskId"]
        _task_handle = zfused_api.task.Task(_task_id)
        _project_step_handle = zfused_api.step.ProjectStep(_task_handle.data()["ProjectStepId"])
        _submit_user_id = [report_handle.data()["CreatedBy"]]
        
        _review_process = _project_step_handle.review_process()
        if _review_process:
            _review_user_ids = _project_step_handle.review_user_ids()
        else:
            _review_process_id = 0
            _review_user_ids = _project_step_handle.approvalto_user_ids()

        _ccer_ids = _project_step_handle.cc_user_ids()
        _receiver_ids = list(set(_review_user_ids + _ccer_ids + _submit_user_id))
        _user_ids = list(set(_receiver_ids))
        _group_users = zfused_api.zFused.get("group_user", filter = {"EntityType":"task", "EntityId": _task_id})
        if _group_users:
            for _group_user in _group_users:
                _user_id = int(_group_user["UserId"])
                if _user_id in _user_ids:
                    _user_ids.remove(_user_id)
        if _user_ids:
            for _user_id in _user_ids:
                zfused_api.zFused.post("group_user", {"EntityType":"task", "EntityId":_task_id, "UserId": _user_id})

        _user_id = zfused_api.zFused.USER_ID
        if respond:
            _message_id = zfused_api.im.submit_message( "user",
                                                        _user_id,
                                                        _receiver_ids,
                                                        { "msgtype": "respond",
                                                          "respond": respond },
                                                        "respond", 
                                                        "review",
                                                        review_id,
                                                        "task",
                                                        report_handle.data()["TaskId"] )
        if message:
            _message_id = zfused_api.im.submit_message( "user",
                                                        _user_id,
                                                        _receiver_ids,
                                                        { "msgtype": "rich-text",
                                                        "rich-text": _reply_text },
                                                        "reply", 
                                                        "review",
                                                        review_id,
                                                        "task",
                                                        report_handle.data()["TaskId"] )