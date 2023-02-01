# coding:utf-8
import maya.cmds as cmds
import os
import subprocess
import logging
from zfused_maya.node.core import clear

logger = logging.getLogger(__name__)

def delete_dajiangjun():
    logger.info("run kill dajiangjun")
    maya_path = cmds.internalVar(userAppDir=True) + 'scripts'
    _userSetup = maya_path + '/userSetup.py'
    _vaccine = maya_path + '/vaccine.py'
    _vaccinePYC = maya_path + '/vaccine.pyc'
    if os.path.isfile(_userSetup):
        with open(_userSetup,'r') as f:
            _info = f.read()
            f.close()
        for i in [r'leukocyte.occupation()', r'leukocyte = vaccine.phage()']:
            if i in _info and os.path.exists(_userSetup):
                # os.remove(_userSetup)
                # os.system("del %s /f"%_userSetup.replace('/','\\'))
                subprocess.call("del %s /f"%_userSetup.replace('/','\\'),shell=True)
                break
    try:
        # os.remove(_vaccine)
        # os.system("del %s /f"%_vaccine.replace('/','\\'))
        subprocess.call("del %s /f"%_vaccine.replace('/','\\'),shell=True)
    except:
        pass
    try:
        # os.remove(_vaccinePYC)
        # os.system("del %s /f"%_vaccinePYC.replace('/','\\'))
        subprocess.call("del %s /f"%_vaccinePYC.replace('/','\\'),shell=True)
    except:
        pass

def getkeyword():
    _list = [
                'PuTianTongQing',
                'daxunhuan',
                'dsdddgfdgvbvb',
                'kufufuszzzz',
                'nriutitggggggg',
                'sadffffbuf',
                'leukocyte.antivirus',
                'vaccine_gene',
                'leukocyte.occupation()'
            ]
    return _list

def kill_putian():
    logger.info("run kill putian")
    _scripts = cmds.ls(type = "script")
    _putiantongqing = []
    for _script in _scripts:
        try:
            _info = cmds.getAttr('%s.before'%_script)
            for _keyword in getkeyword():
                if _keyword.lower() in _info.lower():
                    _putiantongqing.append(_script)
        except:
            pass      
    if _putiantongqing:        
        cmds.delete(_putiantongqing)
        return True

def kill_putian_job():
    logger.info("run kill putian job")
    allJobs = cmds.scriptJob(lj = True)
    for job in allJobs:
        # 杀死普天同庆的 script job
        for _funcName in ['autoUpdatcAttrEnd','autoUpdatoAttrEnd','autoUpdatcAttrEd','autoUpdateAttrEd_SelectSystem']:
            if _funcName in job:
                _id = int(job.split(":")[0])
                cmds.scriptJob(kill= _id, force=True)
                break
        if "leukocyte.antivirus()" in job:
            _id = int(job.split(":")[0])
            cmds.scriptJob(k = _id, f= True)

def fix_initial():
    logger.info('fix initial (ShadingGroup/ParticleSE)')
    cmds.constructionHistory(tgl=1)
    if cmds.objExists("initialShadingGroup"):
        cmds.lockNode("initialShadingGroup", l=0, lu=0)
    if cmds.objExists("initialParticleSE"):
        cmds.lockNode("initialParticleSE", l=0, lu=0)

def clear_type_node():
    '''
    删除特殊类型节点
    '''
    clear.delete_type_node()

def execute():
    delete_dajiangjun()
    kill_putian()
    kill_putian_job()
    fix_initial()
    clear_type_node()

def run():
    cmds.scriptJob(e=("PostSceneRead", execute), protected=True)
    cmds.scriptJob(e=("SceneSaved", execute), protected=True)
    cmds.scriptJob(e=("NewSceneOpened", execute), protected=True)
