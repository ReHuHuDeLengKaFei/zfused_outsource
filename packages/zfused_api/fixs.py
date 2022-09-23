#修复 models



#coding:utf-8
import os

_path = "D:/Go/src/zfused-api/models"

_str = """	for k, v := range query {
		// rewrite dot-notation to Object__Attribute
		k = strings.Replace(k, ".", "__", -1)
		if strings.Contains(k, "isnull") {
			qs = qs.Filter(k, (v == "true" || v == "1"))
		} else {
			qs = qs.Filter(k, v)
		}
	}
"""
_new_str = """	for k, v := range query {
		// rewrite dot-notation to Object__Attribute
		k = strings.Replace(k, ".", "__", -1)
		v := strings.Split(v, "|")
		if strings.Contains(k, "isnull") {
			//qs = qs.Filter(k, (v == "true" || v == "1"))
			qs = qs.Filter(k, true)
		} else {
			qs = qs.Filter(k, v)
		}
	}
	if distinct {
		qs = qs.Distinct()
	}
""" 

_distinct = """(query map[string]string, fields []string, sortby []string, order []string,
	offset int64, limit int64) (ml []interface{}, err error) {"""
_new_distinct = """(query map[string]string, fields []string, sortby []string, order []string,
	offset int64, limit int64, distinct bool) (ml []interface{}, err error) {"""

_order = """	qs = qs.OrderBy(sortFields...)"""
_new_order = """	qs = qs.OrderBy(sortFields...)
qs = qs.Distinct()
"""

#获取所有文件
_files = os.listdir(_path)

for _f in _files:
    _file = "%s/%s"%(_path,_f)

    with open(_file,"r") as _handle:
        _data = _handle.read()
        #print _data
        if _str in _data:
            _data = _data.replace(_str,_new_str)
            print _data
        if _distinct in _data:
            _data = _data.replace(_distinct,_new_distinct)
            print _data
    with open(_file,"w") as _handle:
        _handle.write(_data)













# 修复 controllers



#coding:utf-8
import os

_path = "D:/Go/src/zfused-api/controllers"

_str = """	var fields []string
	var sortby []string
	var order []string
	var query = make(map[string]string)
	var limit int64 = 10
	var offset int64

	// fields: col1,col2,entity.col3
	if v := c.GetString("fields"); v != "" {
		fields = strings.Split(v, ",")
	}"""
_new_str = """	var fields []string
	var sortby []string
	var order []string
	var query = make(map[string]string)
	var limit int64 = 10
	var offset int64
	var distinct bool

    // distinct
	if v, err := c.GetBool("distinct"); err == nil {
		distinct = v
	}

	// fields: col1,col2,entity.col3
	if v := c.GetString("fields"); v != "" {
		fields = strings.Split(v, ",")
	}"""


_query = """(query, fields, sortby, order, offset, limit)"""
_new_query = """(query, fields, sortby, order, offset, limit, distinct)"""

#获取所有文件
_files = os.listdir(_path)

for _f in _files:
    _file = "%s/%s"%(_path,_f)

    with open(_file,"r") as _handle:
        _data = _handle.read()
        #print _data
        if _str in _data:
            _data = _data.replace(_str,_new_str)
            print _data
        if _query in _data:
            _data = _data.replace(_query,_new_query)
            print _data
    with open(_file,"w") as _handle:
        _handle.write(_data)



