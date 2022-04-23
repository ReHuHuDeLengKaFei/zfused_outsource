import json
import os

import zfused_api



EXPORT_DATABASE_KEY = [
    "project",
    "project_config",
    "project_profile",
    "project_step",
    "asset",
    "assembly",
    "episode",
    "sequence",
    "shot",
    "task",
    "version",
    "software",
    "attr_input",
    "attr_output",
    "attr_conn",
    "company"
]

HAS_PROJECT_ID_KEY = [
    "project_config",
    "project_profile",
    "project_step",
    "asset",
    "assembly",
    "episode",
    "sequence",
    "shot",
    "task",
    "version",
]



def extration_database( project_ids, data_dir ):
    """ get all project database

    """
    _project_ids = "|".join([str(_project_id) for _project_id in project_ids])
    _database = {}
    for _table_name in EXPORT_DATABASE_KEY:
        if _table_name == "project":
            _data = zfused_api.zFused.get( _table_name , filter = {"Id__in": _project_ids})
        elif _table_name in HAS_PROJECT_ID_KEY:
            _data = zfused_api.zFused.get( _table_name , filter = {"ProjectId__in": _project_ids})
        else:
            _data = zfused_api.zFused.get( _table_name)

        _file = "{}/{}.json".format(data_dir, _table_name)
        with open(_file, "w") as handle:
            json.dump(_data, handle, indent=4)

    return _database


if __name__ == "__main__":
    
    # zfused_api.zFused("http://192.168.100.104:8080", "lanhua.zhou", 888888)
    extration_database([33], r"D:\lanhua.zhou\develop\zfused\zfused_outsource\database")
    