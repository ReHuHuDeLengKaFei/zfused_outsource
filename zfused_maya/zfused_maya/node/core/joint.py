import pymel.core as pm
import maya.api.OpenMaya as OpenMaya


_source_joint = "main"

_target_joints = [
    "child_1",
    "child_2",
    "child_3"
]

def fnFindSkinCluster(mesh):
    skincluster = None
    for each in pm.listHistory(mesh):  
        if type(each)==pm.nodetypes.SkinCluster:   
            skincluster = each
    return skincluster

mesh = "pSphere1"

skin = fnFindSkinCluster(mesh)

_weights = list(skin.getWeights("pSphereShape1"))

_joints = skin.getInfluence()
# _weights[1]
# skin.getInfluence()

# skin.getWeightedInfluence()

# vtx_id = 3
# skin.weightList[vtx_id].weightList()

def get_component_index(component):
    s, e = component.index('['), component.index(']')
    return int(component[s+1:e])

_vtxs, _values = skin.getPointsAffectedByInfluence("main")

for _vtx, _value in zip(cmds.ls(_vtxs.getSelectionStrings(), fl = True), _values):
    _vtx_id = get_component_index(_vtx)
    _pm_vtx = pm.MeshVertex(_vtx)
    _weight = _weights[_vtx_id]
    _joint_weight = _value/float(len(_target_joints))    
    _fin_weights = []
    for _index, _joint in enumerate(_joints):
        if _joint.name() == _source_joint:
            _fin_weights.append((_source_joint, 0))
            continue
        if _joint.name() in _target_joints:
            _fin_weights.append((_joint.name(), _joint_weight))
            continue
        _fin_weights.append((_joint.name(), _weight[_index]))
    cmds.skinPercent(
            skin.name(),
            _vtx,
            transformValue=_fin_weights,
        )