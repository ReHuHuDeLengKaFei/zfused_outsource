# coding:utf-8
# --author-- lanhua.zhou

import logging

from . import _Entity
import zfused_api

OBJECT = {
    "asset": zfused_api.asset.Asset,
    "episode": zfused_api.episode.Episode,
    "shot": zfused_api.shot.Shot,
    "sequence": zfused_api.sequence.Sequence,
    "task": zfused_api.task.Task,
    "task_time": zfused_api.tasktime.TaskTime,
    "types": zfused_api.types.Types,
    "step": zfused_api.step.Step,
    "project_step": zfused_api.step.ProjectStep,
    "status": zfused_api.status.Status,
    "user": zfused_api.user.User,
    "project": zfused_api.project.Project,
    "version": zfused_api.version.Version,
    "report": zfused_api.report.Report,
    "approval": zfused_api.approval.Approval,
    "company": zfused_api.company.Company,
    "review": zfused_api.review.Review,
    "input_attr": zfused_api.inputattr.InputAttr,
    "output_attr": zfused_api.outputattr.OutputAttr,
    "attr_input": zfused_api.attr.Input,
    "attr_output": zfused_api.attr.Output,
    "project_step_attr": zfused_api.outputattr.OutputAttr,
    "message": zfused_api.message.Message,
    "message_link": zfused_api.message.MessageLink,
    "library": zfused_api.library.Library,
    "library_entity": zfused_api.library.LibraryEntity,
    "library_entity_edition": zfused_api.library.LibraryEntityEdition,
    "medialibrary": zfused_api.medialibrary.MediaLibrary,
    "project_component": zfused_api.component.ProjectComponent,
    "prophet": zfused_api.prophet.Prophet,
    "project_entity": zfused_api.entity.ProjectEntity,
    "plan": zfused_api.plan.Plan,
    "feedback": zfused_api.feedback.FeedBack,
    "department": zfused_api.department.Department,
    "assembly": zfused_api.assembly.Assembly,
    "fileprovide": zfused_api.fileprovide.FileProvide,
    "check": zfused_api.check.Check,
    "project_step_check": zfused_api.step.ProjectStepCheck,
    "software": zfused_api.software.Software,
    "project_software": zfused_api.software.ProjectSoftware,
    "question": zfused_api.question.Question,
    "production_file": zfused_api.production_file.ProductionFile,
    "attr_input": zfused_api.attr.Input,
    "attr_output": zfused_api.attr.Output,
    "development": zfused_api.development.Development,
    "login": zfused_api.login.Login,
    "note": zfused_api.note.Note,
    "chat_single": zfused_api.chat.Single,
    "chat_group": zfused_api.chat.Group
}


ENTITY_MAP = {
    "asset": zfused_api.asset.Asset,
    "episode": zfused_api.episode.Episode,
    "shot": zfused_api.shot.Shot,
    "sequence": zfused_api.sequence.Sequence,
    "task": zfused_api.task.Task,
    "task_time": zfused_api.tasktime.TaskTime,
    "types": zfused_api.types.Types,
    "step": zfused_api.step.Step,
    "project_step": zfused_api.step.ProjectStep,
    "status": zfused_api.status.Status,
    "user": zfused_api.user.User,
    "project": zfused_api.project.Project,
    "version": zfused_api.version.Version,
    "report": zfused_api.report.Report,
    "approval": zfused_api.approval.Approval,
    "company": zfused_api.company.Company,
    "review": zfused_api.review.Review,
    "input_attr": zfused_api.inputattr.InputAttr,
    "output_attr": zfused_api.outputattr.OutputAttr,
    "project_step_attr": zfused_api.outputattr.OutputAttr,
    "message": zfused_api.message.Message,
    "message_link": zfused_api.message.MessageLink,
    "library": zfused_api.library.Library,
    "library_entity": zfused_api.library.LibraryEntity,
    "library_entity_edition": zfused_api.library.LibraryEntityEdition,
    "medialibrary": zfused_api.medialibrary.MediaLibrary,
    "project_component": zfused_api.component.ProjectComponent,
    "prophet": zfused_api.prophet.Prophet,
    "project_entity": zfused_api.entity.ProjectEntity,
    "plan": zfused_api.plan.Plan,
    "feedback": zfused_api.feedback.FeedBack,
    "department": zfused_api.department.Department,
    "assembly": zfused_api.assembly.Assembly,
    "fileprovide": zfused_api.fileprovide.FileProvide,
    "check": zfused_api.check.Check,
    "project_step_check": zfused_api.step.ProjectStepCheck,
    "question": zfused_api.question.Question,
    "production_file": zfused_api.production_file.ProductionFile,
    "attr_input": zfused_api.attr.Input,
    "attr_output": zfused_api.attr.Output,
    "development": zfused_api.development.Development,
    "login": zfused_api.login.Login,
    "note": zfused_api.note.Note,
    "chat_single": zfused_api.chat.Single,
    "chat_group": zfused_api.chat.Group
}

logger = logging.getLogger(__name__) 

def reset():
    for _, _api in OBJECT.items():
        _api.global_dict = {}

def Objects(obj, id, data = None):
    return OBJECT[obj](id, data)

def refresh(obj, object_id):
    """ 刷新对象        
    """
    if obj not in OBJECT:
        return
    try:
        zfused_api.zFused.RESET = True
        if hasattr(OBJECT[obj], "global_dict"):
            logger.info("refresh {} {}".format(obj, object_id))
            if object_id in OBJECT[obj].global_dict:
                OBJECT[obj].global_dict.pop(object_id)
            OBJECT[obj](object_id)
    except Exception as e:
        logger.warning(e)
    finally:
        zfused_api.zFused.RESET = False

def cache(entity_type, entity_id_list):
    _entity_datas = zfused_api.zFused.get(entity_type, filter = {"Id__in": "|".join(map(str, entity_id_list))})
    list(map(lambda _entity_data: ENTITY_MAP[entity_type].global_dict.setdefault(_entity_data["Id"], _entity_data), _entity_datas))
    return _entity_datas