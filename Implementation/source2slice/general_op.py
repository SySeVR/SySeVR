## coding:utf-8
import os
import pickle
import re

list_destparam_0_cpyapi = ['sprintf', 'gets', 'fgets', '_memccpy', '_mbscpy', '_strncpy', 'wmemset', 'vasprintf', 'asprintf', 'wcsncpy', 'lstrcpy', '_wcsncpy', '_snprintf', 'memcpy', 'memmove', '_tcscpy', '_snwprintf', 'strcpy', 'CopyMemory', 'wcsncat', 'vsprintf', 'lstrcpyn', 'vsnprintf', '_mbsncat', 'wmemmove', 'memset', 'wmemcpy', 'strcat', 'fprintf', '_strncat', '_tcsncpy', '_mbsnbcpy', 'strncpy', 'strncat', 'wcscpy', 'snprintf', 'lstrcat']
list_scanf_api = ['vfscanf', 'fscanf', 'vscanf', 'scanf', 'vsscanf', 'sscanf', 'swscanf']
list_key_words = []


def del_ctrl_edge(pdg):
    i = 0
    while i < pdg.ecount():
        if pdg.es[i]['var'] == None:
            pdg.delete_edges(i)
        else:
            i += 1

    return pdg


def get_ifname(node_id, dict_if2cfgnode, dict_cfgnode2if):
    if_name = ''
    min_count = 10000000
    for if_n in dict_cfgnode2if[node_id]:
        if len(dict_if2cfgnode[if_n]) < min_count:
            min_count = len(dict_if2cfgnode[if_n])
            if_name = if_n
        else:
            continue

    return if_name


def isFuncCall(node):
    result = getCalleeName(node)
    if result != []:
        return result
    else:
        return False


def getCalleeName(slicenode):
    #get functions' name
    code = slicenode['code']
    if slicenode['type'] == "Function":
        return []

    pattern = "((?:_|[A-Za-z])\w*(?:\s(?:\.|::|\->|)\s(?:_|[A-Za-z])\w*)*)\s\("
    result = re.findall(pattern, code)

    i = 0
    while i < len(result):
        if result[i] in list_key_words:
            del result[i]
        else:
            i += 1

    return result #return is funcnamelist


def getFuncPDGBynodeIDAndtestID(list_cfgNodeID_funcID, testID):
    _dict = {}
    for _tuple in list_cfgNodeID_funcID:
        cfgNodeID = _tuple[0]
        func_id = _tuple[1]
        path = os.path.join('pdg_db', testID)
        for _file in os.listdir(path):
            if _file.split('_')[-1] == func_id:
                fpath = os.path.join(path, _file)
                fin = open(fpath, 'rb')
                pdg = pickle.load(fin)
                _dict[cfgNodeID] = pdg
                fin.close()
                break

    return _dict


def getFuncPDGBynodeIDAndtestID_noctrl(list_cfgNodeID_funcID, testID):
    _dict = {}
    for _tuple in list_cfgNodeID_funcID:
        cfgNodeID = _tuple[0]
        func_id = _tuple[1]
        for _dir in os.listdir("pdg/"):
            list_testid = os.listdir(os.path.join("pdg/", _dir))

            if testID not in list_testid:
                continue

            else:    
                path = os.path.join("pdg/", _dir, testID)
                for _file in os.listdir(path):
                    if _file.split('_')[-1] == func_id:
                        fpath = os.path.join(path, _file)
                        fin = open(fpath, 'rb')
                        pdg = pickle.load(fin)
                        _dict[cfgNodeID] = pdg
                        fin.close()
                        break

    return _dict


def getFuncPDGByfuncIDAndtestID(func_ID, testID):
    path = os.path.join('pdg_db', testID)
    pdg = False
    for _file in os.listdir(path):
        if _file.split('_')[-1] == str(func_ID):
            fpath = os.path.join(path, _file)
            fin = open(fpath, 'rb')
            pdg = pickle.load(fin)
            fin.close()
            break

    return pdg


def getFuncPDGByfuncIDAndtestID_noctrl(func_ID, testID, _type):
    pdg = False
    for _dir in os.listdir("pdg/"):
        list_testid = os.listdir(os.path.join("pdg/", _dir))

        if testID not in list_testid:
            continue

        else:
            path = os.path.join("pdg/", _dir, testID)
            for _file in os.listdir(path):
                if _file.split('_')[-1] == str(func_ID):
                    fpath = os.path.join(path, _file)
                    fin = open(fpath, 'rb')
                    pdg = pickle.load(fin)
                    fin.close()
                    break

    return pdg


def getReturnVarOfAPI(code):
    for api in list_destparam_0_cpyapi:
        if code.find(api + ' ') != -1:
            _list = code.split(api + ' ')
            if _list[0] == '' and _list[1][0] == '(':
                var = _list[1].split(',')[0].replace('(', '').strip()
                if var.find(' & ') > -1:
                    var = var.split(' & ')[1]

                if var.find(' + ') != -1:
                    var = var.split(' + ')[0]
                    if var.find(' . ') != -1:
                        _list = [var]
                        var_1 = []
                        while var.find(' . ') != -1:
                            var_1.append(var.split(' . ')[0])
                            _list.append(' . '.join(var_1))
                            var = ' . '.join(var.split(' . ')[1:])

                        return _list

                    elif var.find(' -> ') != -1:
                        _list = [var]
                        var_1 = []
                        while var.find(' -> ') != -1:
                            var_1.append(var.split(' -> ')[0])
                            _list.append(' -> '.join(var_1))
                            var = ' -> '.join(var.split(' -> ')[1:])

                        return _list

                    else:
                        return [var]

                elif var.find(' - ') != -1:
                    var = var.split(' - ')[0]
                    if var.find(' . ') != -1:
                        _list = [var]
                        var_1 = []
                        while var.find(' . ') != -1:
                            var_1.append(var.split(' . ')[0])
                            _list.append(' . '.join(var_1))
                            var = ' . '.join(var.split(' . ')[1:])

                        return _list

                    elif var.find(' -> ') != -1:
                        _list = [var]
                        var_1 = []
                        while var.find(' -> ') != -1:
                            var_1.append(var.split(' -> ')[0])
                            _list.append(' -> '.join(var_1))
                            var = ' -> '.join(var.split(' -> ')[1:])

                        return _list

                    else:
                        return [var]

                elif var.find(' * ') != -1:
                    temp = var.split(' * ')[1]
                    if temp[0] == ')':
                        var = temp[1:].strip()
                    else:
                        var = var.split(' * ')[0]

                    if var.find(' . ') != -1:
                        _list = [var]
                        var_1 = []
                        while var.find(' . ') != -1:
                            var_1.append(var.split(' . ')[0])
                            _list.append(' . '.join(var_1))
                            var = ' . '.join(var.split(' . ')[1:])

                        return _list

                    elif var.find(' -> ') != -1:
                        _list = [var]
                        var_1 = []
                        while var.find(' -> ') != -1:
                            var_1.append(var.split(' -> ')[0])
                            _list.append(' -> '.join(var_1))
                            var = ' -> '.join(var.split(' -> ')[1:])

                        return _list

                    else:
                        return [var]

                elif var.find(' . ') != -1:
                    _list = [var]
                    var_1 = []
                    while var.find(' . ') != -1:
                        var_1.append(var.split(' . ')[0])
                        _list.append(' . '.join(var_1))
                        var = ' . '.join(var.split(' . ')[1:])

                    return _list

                elif var.find(' -> ') != -1:
                    _list = [var]
                    var_1 = []
                    while var.find(' -> ') != -1:
                        var_1.append(var.split(' -> ')[0])
                        _list.append(' -> '.join(var_1))
                        var = ' -> '.join(var.split(' -> ')[1:])

                    return _list

                else:
                    return [var]

        else:
            continue

    for scanfapi in list_scanf_api:
        if scanfapi in ['fscanf', 'sscanf', 'swscanf', 'vfscanf', 'vsscanf']:
            if code.find(scanfapi + ' ') != -1:
                _list = code.split(scanfapi+' ')
                if _list[0] == '' and _list[1][0] == '(':
                    list_var = _list[1].split(',')[2:]
                    list_var = [var.replace('(', '').strip() for var in list_var]
                    new_list_var = []
                    for var in list_var:
                        if var.find(' & ') > -1:
                            var = var.split(' & ')[1]

                        if var.find(' + ') > -1:
                            var = var.split(' + ')[0]
                            if var.find(' . ') != -1:
                                _list = [var]
                                var_1 = []
                                while var.find(' . ') != -1:
                                    var_1.append(var.split(' . ')[0])
                                    _list.append(' . '.join(var_1))
                                    var = ' . '.join(var.split(' . ')[1:])

                                new_list_var += _list

                            elif var.find(' -> ') != -1:
                                _list = [var]
                                var_1 = []
                                while var.find(' -> ') != -1:
                                    var_1.append(var.split(' -> ')[0])
                                    _list.append(' -> '.join(var_1))
                                    var = ' -> '.join(var.split(' -> ')[1:])

                                new_list_var += _list

                            else:
                                new_list_var.append(var)

                        elif var.find(' - ') != -1:
                            var = var.split(' - ')[0]
                            if var.find(' . ') != -1:
                                _list = [var]
                                var_1 = []
                                while var.find(' . ') != -1:
                                    var_1.append(var.split(' . ')[0])
                                    _list.append(' . '.join(var_1))
                                    var = ' . '.join(var.split(' . ')[1:])

                                new_list_var += _list

                            elif var.find(' -> ') != -1:
                                _list = [var]
                                var_1 = []
                                while var.find(' -> ') != -1:
                                    var_1.append(var.split(' -> ')[0])
                                    _list.append(' -> '.join(var_1))
                                    var = ' -> '.join(var.split(' -> ')[1:])

                                new_list_var += _list

                            else:
                                new_list_var.append(var)

                        elif var.find(' * ') != -1:
                            temp = var.split(' * ')[1]
                            if temp[0] == ')':
                                var = temp[1:].strip()
                            else:
                                var = var.split(' * ')[0]

                            if var.find(' . ') != -1:
                                _list = [var]
                                var_1 = []
                                while var.find(' . ') != -1:
                                    var_1.append(var.split(' . ')[0])
                                    _list.append(' . '.join(var_1))
                                    var = ' . '.join(var.split(' . ')[1:])

                                new_list_var += _list

                            elif var.find(' -> ') != -1:
                                _list = [var]
                                var_1 = []
                                while var.find(' -> ') != -1:
                                    var_1.append(var.split(' -> ')[0])
                                    _list.append(' -> '.join(var_1))
                                    var = ' -> '.join(var.split(' -> ')[1:])

                                new_list_var += _list

                            else:
                                new_list_var.append(var)

                        elif var.find(' . ') != -1:
                            _list = [var]
                            var_1 = []
                            while var.find(' . ') != -1:
                                var_1.append(var.split(' . ')[0])
                                _list.append(' . '.join(var_1))
                                var = ' . '.join(var.split(' . ')[1:])

                            new_list_var += _list

                        elif var.find(' -> ') != -1:
                            _list = [var]
                            var_1 = []
                            while var.find(' -> ') != -1:
                                var_1.append(var.split(' -> ')[0])
                                _list.append(' -> '.join(var_1))
                                var = ' -> '.join(var.split(' -> ')[1:])

                            new_list_var += _list

                        else:
                            new_list_var.append(var)

                    return new_list_var


        elif scanfapi in ['scanf', 'vscanf']:
            if code.find(scanfapi) != -1:
                _list = code.split(scanfapi + ' ')
                if _list[0] == '' and _list[1][0] == '(':
                    list_var = _list[1].split(',')[1:]
                    list_var = [var.replace('(', '').strip() for var in list_var]
                    new_list_var = []
                    for var in list_var:
                        if var.find(' & ') > -1:
                            var = var.split(' & ')[1]

                        if var.find(' + ') != -1:
                            var = var.split(' + ')[0]
                            if var.find(' . ') != -1:
                                _list = [var]
                                var_1 = []
                                while var.find(' . ') != -1:
                                    var_1.append(var.split(' . ')[0])
                                    _list.append(' . '.join(var_1))
                                    var = ' . '.join(var.split(' . ')[1:])

                                new_list_var += _list

                            else:
                                new_list_var.append(var)

                        elif var.find(' - ') != -1:
                            var = var.split(' - ')[0]
                            if var.find(' . ') != -1:
                                _list = [var]
                                var_1 = []
                                while var.find(' . ') != -1:
                                    var_1.append(var.split(' . ')[0])
                                    _list.append(' . '.join(var_1))
                                    var = ' . '.join(var.split(' . ')[1:])

                                new_list_var += _list

                            else:
                                new_list_var.append(var)

                        elif var.find(' * ') != -1:
                            temp = var.split(' * ')[1]
                            if temp[0] == ')':
                                var = temp[1:].strip()
                            else:
                                var = var.split(' * ')[0]

                            if var.find(' . ') != -1:
                                _list = [var]
                                var_1 = []
                                while var.find(' . ') != -1:
                                    var_1.append(var.split(' . ')[0])
                                    _list.append(' . '.join(var_1))
                                    var = ' . '.join(var.split(' . ')[1:])

                                new_list_var += _list

                            else:
                                new_list_var.append(var)

                        elif var.find(' . ') != -1:
                            _list = [var]
                            var_1 = []
                            while var.find(' . ') != -1:
                                var_1.append(var.split(' . ')[0])
                                _list.append(' . '.join(var_1))
                                var = ' . '.join(var.split(' . ')[1:])

                            new_list_var += _list

                        elif var.find(' -> ') != -1:
                            _list = [var]
                            var_1 = []
                            while var.find(' -> ') != -1:
                                var_1.append(var.split(' -> ')[0])
                                _list.append(' -> '.join(var_1))
                                var = ' -> '.join(var.split(' -> ')[1:])

                            new_list_var += _list

                        else:
                            new_list_var.append(var)

                    return new_list_var

    return False


def isEdgeExists(pdg, startnode, endnode, var):
    for edge in pdg.es:
        if pdg.vs[edge.tuple]['name'][0] == startnode and pdg.vs[edge.tuple]['name'][1] == endnode and edge['var'] == var:
            return True
        else:
            continue

    return False 


def addDataEdge(pdg, startnode, endnode, var):
    if isEdgeExists(pdg, startnode, endnode, var):
        return pdg
            
    edge_prop = {'var': var}
    pdg.add_edge(startnode, endnode, **edge_prop)
    return pdg


def getVarOfNode(code):
    list_var = []
    if code.find(' = ') != -1:
        _list = code.split(' = ')[0].split(' ')
        if ']' in _list:        
            index_right = _list.index(']')
            index_left = _list.index('[')
            
            i = 0
            while i < len(_list):
                if i < index_left or i > index_right:
                    list_var.append(_list[i])
                i += 1

    elif code[-1] == ';':
        code = code[:-1].strip()
        if '(' in code:
            list_var = False
        else:
            list_value = code.split(',')#-1 is ;
            for _list in list_value:
                _list = code.split(' ')
                if '[' in _list:
                    index = _list.index('[')
                    var = _list[index-1]
                    list_var.append(var)

                else:
                    var = _list[-1]
                    list_var.append(var)

    else:
        if '(' in code:
            list_var = False
        else:
            list_value = code.split(',')#-1 is ;
            for _list in list_value:
                _list = code.split(' ')
                if '[' in _list:
                    index = _list.index('[')
                    var = _list[index-1]
                    list_var.append(var)

                else:
                    var = _list[-1]
                    list_var.append(var)

    return list_var


def sortedNodesByLoc(list_node):
    _list = []
    for node in list_node:
        if node['location'] == None:
            row = 'inf'
            col = 'inf'
        else:
            row, col = [int(node['location'].split(':')[0]), int(node['location'].split(':')[1])]
        _list.append((row, col, node))

    _list.sort(key=lambda x: (x[0], x[1]))


    list_ordered_nodes = [_tuple[2] for _tuple in _list]

    return list_ordered_nodes


def getFuncPDGById(testID, pdg_funcid):
    file_dir = os.path.join("pdg_db", testID)

    for _file in os.listdir(file_dir):
        func_id = _file.split('_')[-1]

        if func_id == pdg_funcid:
            pdg_path = os.path.join(file_dir, _file)
            f = open(pdg_path, 'rb')
            pdg = pickle.load(f)
            f.close()

            return pdg


def getFuncPDGById_noctrl(testID, pdg_funcid):
    for _dir in os.listdir("pdg/"):
        list_testid = os.listdir(os.path.join("pdg/", _dir))

        if testID not in list_testid:
            continue
        else:
            file_dir = os.path.join("pdg/", _dir, testID)

            for _file in os.listdir(file_dir):
                func_id = _file.split('_')[-1]

                if func_id == pdg_funcid:
                    pdg_path = os.path.join(file_dir, _file)
                    f = open(pdg_path, 'rb')
                    pdg = pickle.load(f)
                    f.close()

                    return pdg


def getFuncPDGByNameAndtestID(func_name, testID):
    path = os.path.join('pdg_db', testID)
    pdg = False
    for _file in os.listdir(path):
        if '_'.join(_file.split('_')[:-1]) == func_name:
            fpath = os.path.join(path, _file)
            fin = open(fpath, 'rb')
            pdg = pickle.load(fin)
            fin.close()
            break

    return pdg


def getFuncPDGByNameAndtestID_noctrl(func_name, testID):
    pdg = False
    for _dir in os.listdir("pdg_db/"):
        list_testid = os.listdir(os.path.join("pdg_db/", _dir))

        if testID not in list_testid:
            continue

        else:
            path = os.path.join('pdg', _dir, testID)
            for _file in os.listdir(path):
                if '_'.join(_file.split('_')[:-1]) == func_name:
                    fpath = os.path.join(path, _file)
                    fin = open(fpath, 'rb')
                    pdg = pickle.load(fin)
                    fin.close()
                    break

    return pdg


def isNewOrDelOp(node, testID):
    if node['code'].find(' = new ') != -1:

        tempvalue = node['code'].split(' = new ')[1].replace('*', '')
        if tempvalue.split(' ')[0] != 'const':
            classname = tempvalue.split(' ')[0].strip()
            funcname = classname + ' :: ' + classname
            return funcname

        else:
            classname = tempvalue.split(' ')[1].strip()
            funcname = classname + ' :: ' + classname
            return funcname

    elif node['code'].find('delete ') != -1:
        objectname = node['code'].split('delete ')[1].replace(';', '').strip()
        list_s = []
        functionID = node['functionId']
        pdg = getFuncPDGByfuncIDAndtestID(functionID, testID)
        for n in pdg.vs:

            if n['name'] == node['name']:
                list_s = n.predecessors()

                for edge in pdg.es:
                    if pdg.vs[edge.tuple[0]] in list_s and pdg.vs[edge.tuple[1]] == n and edge['var'] == objectname:

                        start_n = pdg.vs[edge.tuple[0]]
                        if start_n['code'].find(' = new ') != -1:
                        
                            tempvalue = start_n['code'].split(' = new ')[1].replace('*', '')
                            if tempvalue.split(' ')[0] != 'const':
                                classname = tempvalue.split(' ')[0].strip()
                                funcname = classname + ' :: ~' + classname
                                return funcname

                            else:
                                classname = tempvalue.split(' ')[1].strip()
                                funcname = classname + ' :: ~' + classname
                                return funcname

                        else:
                            continue

    return False


def isNewOrDelOp_noctrl(node, testID, _type):
    if node['code'].find(' = new ') != -1:
        tempvalue = node['code'].split(' = new ')[1].replace('*', '')
        if tempvalue.split(' ')[0] != 'const':
            classname = tempvalue.split(' ')[0].strip()
            funcname = classname + ' :: ' + classname
            return funcname

        else:
            classname = tempvalue.split(' ')[1].strip()
            funcname = classname + ' :: ' + classname
            return funcname

    elif node['code'].find('delete ') != -1:
        objectname = node['code'].split('delete ')[1].replace(';', '').strip()
        list_s = []
        functionID = node['functionId']

        if _type:
            pdg = getFuncPDGByfuncIDAndtestID_noctrl(functionID, testID, _type)
        else:
            pdg = getFuncPDGByfuncIDAndtestID(functionID, testID)

        for n in pdg.vs:
            
            if n['name'] == node['name']:
                list_s = n.predecessors()

                for edge in pdg.es:
                    if pdg.vs[edge.tuple[0]] in list_s and pdg.vs[edge.tuple[1]] == n and edge['var'] == objectname:
                        
                        start_n = pdg.vs[edge.tuple[0]]
                        if start_n['code'].find(' = new ') != -1:
                            tempvalue = start_n['code'].split(' = new ')[1].replace('*', '')
                            if tempvalue.split(' ')[0] != 'const':
                                classname = tempvalue.split(' ')[0].strip()
                                funcname = classname + ' :: ~' + classname
                                return funcname

                            else:
                                classname = tempvalue.split(' ')[1].strip()
                                funcname = classname + ' :: ~' + classname
                                return funcname

                        else:
                            continue

    return False
