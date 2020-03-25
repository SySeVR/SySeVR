## coding:utf-8
from access_db_operate import *
import copy
from general_op import *
from py2neo.packages.httpstream import http
http.socket_timeout = 9999

def modifyDataEdgeVal(pdg):
    for edge in pdg.es:
        if edge['var'] == None:
            continue

        new_val = ''
        for c in edge['var']:
            if c == '*':
                continue
            else:
                new_val += c

        edge['var'] = new_val

    return pdg


def modifyStmtNode(pdg):
    compare_row = 0
    dict_row2nodestmt = {}
    dict_row2nodeid = {}
    #only process statement node
    dict_static = {}

    i = 0
    while i < pdg.vcount():
        if pdg.vs[i]['type'] == 'Statement' and pdg.vs[i]['code'] == 'static':
            raw = int(pdg.vs[i]['location'].split(':')[0])
            col = int(pdg.vs[i]['location'].split(':')[1])
            dict_static[raw] = (raw, col)
            pdg.delete_vertices(i)
        else:
            i += 1

    i = 0
    while i < pdg.vcount():
        if pdg.vs[i]['type'] == 'Statement':
            row = int(pdg.vs[i]['location'].split(':')[0])
            col = int(pdg.vs[i]['location'].split(':')[1])
            _tuple = (pdg.vs[i]['code'], row, col, pdg.vs[i]['location'])

            if row not in dict_row2nodestmt.keys():
                dict_row2nodestmt[row] = [_tuple]
                dict_row2nodeid[row] = pdg.vs[i]['name'] #to confirm delete order
                i += 1

            else:
                dict_row2nodestmt[row].append(_tuple)
                pdg.delete_vertices(i)


        else:
            i += 1

    #process single node but not statement node
    j = 0
    list_nodeindex_to_delete = []
    while j < pdg.vcount():
        if pdg.vs[j]['location'] != None:
            row = int(pdg.vs[j]['location'].split(':')[0])
            col = int(pdg.vs[j]['location'].split(':')[1])
        else:
            j += 1
            continue

        if row in dict_row2nodestmt.keys() and pdg.vs[j]['type'] != 'Statement':
            _tuple = (pdg.vs[j]['code'], row, col, pdg.vs[j]['location'])
            dict_row2nodestmt[row].append(_tuple)
            list_nodeindex_to_delete.append(pdg.vs[j]['name'])
            j += 1

        else:
            j += 1


    for key in dict_row2nodestmt.keys():
        dict_row2nodestmt[key].sort(key=lambda e:e[2])
        #print dict_row2nodestmt[key]
        nodename = dict_row2nodeid[key]
        nodeIndex = 0
        for node in pdg.vs:
            if node['name'] == nodename:
                break
            else:
                nodeIndex += 1

        location = dict_row2nodestmt[key][0][3]

        new_code = ' '.join([_t[0] for _t in dict_row2nodestmt[key]]).strip()

        #not consider ';' appear too much times
        pdg.vs[nodeIndex]['code'] = new_code
        pdg.vs[nodeIndex]['location'] = location
        pdg.vs[nodeIndex]['type'] = 'Statement'

    for d_name in list_nodeindex_to_delete:
        i = 0
        while i < pdg.vcount():
            if pdg.vs[i]['name'] == d_name:
                pdg.delete_vertices(i)
            else:
                i += 1


    n = 0
    while  n < pdg.vcount():
        if pdg.vs[n]['location'] == None:
            n += 1
            continue

        raw = int(pdg.vs[n]['location'].split(':')[0])
        col = int(pdg.vs[n]['location'].split(':')[1])
        if raw in dict_static.keys() and col > dict_static[raw][1]:
            pdg.vs[n]['code'] = 'static ' + pdg.vs[n]['code']

        n += 1

    list_node_index = []
    for node in pdg.vs:
        if node['type'] == 'Statement':
            raw = int(node['location'].split(':')[0])
            list_node_index.append((raw, node))

    list_node_index.sort(key=lambda x:(x[0], x[1]))

    i = 1
    list_del_name = []
    while i < len(list_node_index):
        if list_node_index[i][0]-list_node_index[i-1][0] == 1:
            list_node_index[i][1]['code'] = list_node_index[i-1][1]['code'] + '\n' + list_node_index[i][1]['code']
            list_del_name.append(list_node_index[i-1][1]['name'])
            del list_node_index[i-1]
        else:
            i += 1

    _dict = {}
    for n in list_node_index:
        _dict[n[1]['name']] = n[1]['code']

    j = 0
    while j < pdg.vcount():
        if pdg.vs[j]['name'] in list_del_name:
            pdg.delete_vertices(j)
        elif pdg.vs[j]['name'] in _dict.keys():
            pdg.vs[j]['code'] =  _dict[pdg.vs[j]['name']]
            j += 1
        else:
            j += 1

    #for v in pdg.vs:
    #    print v['code'], v['type'], v['name']
    #exit()

    return pdg
         

def getInitNodeOfDecl(pdg, list_sorted_pdgnode, node, var, dict_use, dict_def):
    index = list_sorted_pdgnode.index(node)
    list_init_node = []
    for i in range(index+1, len(list_sorted_pdgnode)):
        if list_sorted_pdgnode[i]['type'] != 'IdentifierDeclStatement' and list_sorted_pdgnode[i]['name'] in dict_def.keys():
            if var in dict_def[list_sorted_pdgnode[i]['name']]:
                if isEdgeExists(pdg, node['name'], list_sorted_pdgnode[i]['name'], var):
                    continue
                else:
                    list_init_node.append((list_sorted_pdgnode[i], i))#is init node and dataedge not exists

        elif list_sorted_pdgnode[i]['type'] != 'IdentifierDeclStatement' and list_sorted_pdgnode[i]['name'] not in dict_def.keys():
            print list_sorted_pdgnode[i]['name']
            if list_sorted_pdgnode[i]['name'] in dict_use.keys() and var in dict_use[list_sorted_pdgnode[i]['name']]:
                #print '2'
                if isEdgeExists(pdg, node['name'], list_sorted_pdgnode[i]['name'], var):
                    continue
                else:
                    list_init_node.append((list_sorted_pdgnode[i], i))

        else:
            continue
            
    return list_init_node


def completeDeclStmtOfPDG(pdg, dict_use, dict_def, dict_if2cfgnode, dict_cfgnode2if):
    list_sorted_pdgnode = sortedNodesByLoc(pdg.vs)
    dict_declnode2val = {}
    for node in pdg.vs:
        if (node['type'] == 'IdentifierDeclStatement' or node['type'] == 'Parameter' or node['type'] == 'Statement') and node['code'].find(' = ') == -1:#find not init node
            if node['type'] == 'IdentifierDeclStatement' or node['type'] == 'Parameter':
                list_var = dict_def[node['name']]
            else:
                list_var = getVarOfNode(node['code'])

            if list_var == False:
                continue

            else:
                for var in list_var:
                    results = getInitNodeOfDecl(pdg, list_sorted_pdgnode, node, var, dict_use, dict_def)
                    if results != []:
                        for result in results:
                            if node['name'] not in dict_cfgnode2if.keys():#startnode not belong to if
                                startnode = node['name']
                                endnode = result[0]['name']
                                pdg = addDataEdge(pdg, startnode, endnode, var)

                            else:
                                list_if = dict_cfgnode2if[node['name']]
                                list_not_scan = []

                                for ifstmt_n in list_if:
                                    tuple_statements = dict_if2cfgnode[ifstmt_n]

                                    if node['name'] in tuple_statements[0]:
                                        list_not_scan += tuple_statements[1]

                                    elif node['name'] in tuple_statements[1]:
                                        list_not_scan += tuple_statements[0]

                                if result[0]['name'] not in list_not_scan:
                                    startnode = node['name']
                                    endnode = result[0]['name']
                                    pdg = addDataEdge(pdg, startnode, endnode, var)

    return pdg


def get_nodes_before_exit(pdg, dict_if2cfgnode, dict_cfgnode2if):
    _dict = {}
    for key in dict_cfgnode2if.keys():
        results = pdg.vs.select(name=key)
        if len(results) != 0 and (results[0]['type'] == 'BreakStatement' or results[0]['type'] == 'ReturnStatement' or results[0]['code'].find('exit ') != -1 or results[0]['type'] == 'GotoStatement'):# if stms have return
            if_name = ''
            if len(dict_cfgnode2if[key]) == 1:
                if_name = dict_cfgnode2if[key][0]
            else:
                if_name = get_ifname(key, dict_if2cfgnode, dict_cfgnode2if)

            print "key", key, if_name, dict_cfgnode2if[key]

            _list_name_0 = dict_if2cfgnode[if_name][0]
            _list_name_1 = dict_if2cfgnode[if_name][1]

            if key in _list_name_0:
                ret_index = _list_name_0.index(key)
                del _list_name_0[ret_index] #_list_name are set of nodes which under the same if with return node or exit or goto statement

                for name in _list_name_0:
                    _dict[name] = key

            if key in _list_name_1:
                ret_index = _list_name_1.index(key)
                del _list_name_1[ret_index] #_list_name are set of nodes which under the same if with return node or exit or goto statement

                for name in _list_name_1:
                    _dict[name] = key

        else:
            continue

    return _dict


def completeDataEdgeOfPDG(pdg, dict_use, dict_def, dict_if2cfgnode, dict_cfgnode2if):
#if a var in define list but there is not a edge between a node which use it and node which define it,not include id_decl
    list_sorted_pdgnode = sortedNodesByLoc(pdg.vs)
    exit2stmt_dict = get_nodes_before_exit(pdg, dict_if2cfgnode, dict_cfgnode2if)
    dict_declnode2val = {}

    for i in range(0, len(list_sorted_pdgnode)):
        if list_sorted_pdgnode[i]['type'] == 'IdentifierDeclStatement':
            continue

        if list_sorted_pdgnode[i]['name'] in dict_def.keys():
            #print "list_sorted_pdgnode[i]['name']", list_sorted_pdgnode[i]['name']
            list_def_var = dict_def[list_sorted_pdgnode[i]['name']]

            for def_var in list_def_var:
                for j in range(i+1, len(list_sorted_pdgnode)):
                    if list_sorted_pdgnode[i]['name'] in exit2stmt_dict.keys():
                        exit_name = exit2stmt_dict[list_sorted_pdgnode[i]['name']]

                        if list_sorted_pdgnode[j]['name'] == exit_name:
                            break

                        elif list_sorted_pdgnode[j]['name'] in dict_use.keys() and def_var in dict_use[list_sorted_pdgnode[j]['name']]:
                            if list_sorted_pdgnode[i]['name'] not in dict_cfgnode2if.keys():
                                #must add
                                startnode = list_sorted_pdgnode[i]['name']
                                endnode = list_sorted_pdgnode[j]['name']
                                addDataEdge(pdg, startnode, endnode, def_var)

                                if list_sorted_pdgnode[j]['name'] in dict_def.keys() and def_var in dict_def[list_sorted_pdgnode[j]['name']]:
                                    break

                            elif list_sorted_pdgnode[i]['name'] in dict_cfgnode2if.keys() and list_sorted_pdgnode[j]['name'] not in dict_cfgnode2if.keys():
                                startnode = list_sorted_pdgnode[i]['name']
                                endnode = list_sorted_pdgnode[j]['name']
                                addDataEdge(pdg, startnode, endnode, def_var)

                                if list_sorted_pdgnode[j]['name'] in dict_def.keys() and def_var in dict_def[list_sorted_pdgnode[j]['name']]:
                                    break

                            elif list_sorted_pdgnode[i]['name'] in dict_cfgnode2if.keys() and list_sorted_pdgnode[j]['name'] in dict_cfgnode2if.keys():
                                if_list = dict_cfgnode2if[list_sorted_pdgnode[i]['name']]
                                _not_scan = []
                                for if_stmt in if_list:
                                    _tuple = dict_if2cfgnode[if_stmt]
                                    if list_sorted_pdgnode[i]['name'] in _tuple[0]:
                                        _not_scan += _tuple[1]
                                    else:
                                        _not_scan += _tuple[0]

                                if list_sorted_pdgnode[j]['name'] not in _not_scan:
                                    startnode = list_sorted_pdgnode[i]['name']
                                    endnode = list_sorted_pdgnode[j]['name']
                                    addDataEdge(pdg, startnode, endnode, def_var)

                                if list_sorted_pdgnode[j]['name'] in dict_def.keys() and def_var in dict_def[list_sorted_pdgnode[j]['name']]:
                                    break

                    else:
                        if list_sorted_pdgnode[j]['name'] in dict_use.keys() and def_var in dict_use[list_sorted_pdgnode[j]['name']]:
                            if list_sorted_pdgnode[i]['name'] not in dict_cfgnode2if.keys():
                                #must add
                                startnode = list_sorted_pdgnode[i]['name']
                                endnode = list_sorted_pdgnode[j]['name']
                                addDataEdge(pdg, startnode, endnode, def_var)

                                if list_sorted_pdgnode[j]['name'] in dict_def.keys() and def_var in dict_def[list_sorted_pdgnode[j]['name']]:
                                    break

                            elif list_sorted_pdgnode[i]['name'] in dict_cfgnode2if.keys() and list_sorted_pdgnode[j]['name'] not in dict_cfgnode2if.keys():
                                startnode = list_sorted_pdgnode[i]['name']
                                endnode = list_sorted_pdgnode[j]['name']
                                addDataEdge(pdg, startnode, endnode, def_var)

                                if list_sorted_pdgnode[j]['name'] in dict_def.keys() and def_var in dict_def[list_sorted_pdgnode[j]['name']]:
                                    break

                            elif list_sorted_pdgnode[i]['name'] in dict_cfgnode2if.keys() and list_sorted_pdgnode[j]['name'] in dict_cfgnode2if.keys():
                                if_list = dict_cfgnode2if[list_sorted_pdgnode[i]['name']]
                                _not_scan = []
                                for if_stmt in if_list:
                                    _tuple = dict_if2cfgnode[if_stmt]
                                    if list_sorted_pdgnode[i]['name'] in _tuple[0]:
                                        _not_scan += _tuple[1]
                                    else:
                                        _not_scan += _tuple[0]

                                if list_sorted_pdgnode[j]['name'] not in _not_scan:
                                    startnode = list_sorted_pdgnode[i]['name']
                                    endnode = list_sorted_pdgnode[j]['name']
                                    addDataEdge(pdg, startnode, endnode, def_var)

                                if list_sorted_pdgnode[j]['name'] in dict_def.keys() and def_var in dict_def[list_sorted_pdgnode[j]['name']]:
                                    break


        else:
            continue

    return pdg


def addDataEdgeOfObject(pdg, dict_if2cfgnode, dict_cfgnode2if):
    for node in pdg.vs:
        if node['code'].find(' = new ') != -1:
            objectname = node['code'].split(' = new ')[0].split(' ')[-1].strip()
            cur_name = node['name']

            for pnode in pdg.vs:
                #print pnode['code']
                if pnode['name'] == cur_name:
                    continue

                if node['name'] not in dict_cfgnode2if.keys():
                    if pnode['code'].find(objectname + ' -> ') != -1:
                        if pnode['code'].split(objectname + ' -> ')[0] == '':
                            startnode = node['name']
                            endnode = pnode['name']
                            def_var = objectname
                            addDataEdge(pdg, startnode, endnode, def_var)
                        elif pnode['code'].split(objectname + ' -> ')[0][-1] == ' ':
                            startnode = node['name']
                            endnode = pnode['name']
                            def_var = objectname
                            addDataEdge(pdg, startnode, endnode, def_var)

                    elif pnode['code'].find('delete ') != -1:
                        startnode = node['name']
                        endnode = pnode['name']
                        def_var = objectname
                        addDataEdge(pdg, startnode, endnode, def_var)

                    else:
                        continue

                else:
                    list_if = dict_cfgnode2if[node['name']]
                    list_not_scan = []

                    for ifstmt_n in list_if:
                        tuple_statements = dict_if2cfgnode[ifstmt_n]

                        if node['name'] in tuple_statements[0]:
                            list_not_scan += tuple_statements[1]

                        elif node['name'] in tuple_statements[1]:
                            list_not_scan += tuple_statements[0]

                    if pnode['code'].find(objectname + ' -> ') != -1 and pnode['name'] not in list_not_scan:
                        if pnode['code'].split(objectname + ' -> ')[0] == '':
                            startnode = node['name']
                            endnode = pnode['name']
                            def_var = objectname
                            addDataEdge(pdg, startnode, endnode, def_var)
                        elif pnode['code'].split(objectname + ' -> ')[0][-1] == ' ' :
                            startnode = node['name']
                            endnode = pnode['name']
                            def_var = objectname
                            addDataEdge(pdg, startnode, endnode, def_var)

                    elif pnode['code'].find('delete ') != -1  and pnode['name'] not in list_not_scan:
                        startnode = node['name']
                        endnode = pnode['name']
                        def_var = objectname
                        addDataEdge(pdg, startnode, endnode, def_var)

                    else:
                        continue

        else:
            continue

    return pdg

def deleteCDG(pdg):
    edge=pdg.es
    a=len(edge)
    list_d=[]
    print("delete cdg")
    for j in range(0,a):
        #print edge[j]
        if edge[j]['var']==None:
            list_d.append(j)
    a=list(reversed(list_d))
    for i in a:
        pdg.delete_edges(edge[i])
    return pdg 

def main():
    j = JoernSteps()
    j.connectToDatabase()
    all_func_node = getALLFuncNode(j)
    for node in all_func_node:
        testID = getFuncFile(j, node._id).split('/')[-2]
        path = os.path.join("pdg_db", testID)

        store_file_name = node.properties['name'] + '_' + str(node._id)

        store_path = os.path.join(path, store_file_name)
        if os.path.exists(store_path):
            continue

        initpdg = translatePDGByNode(j, node)#get init PDG
        opt_pdg_1 = modifyStmtNode(initpdg)#merge every statement node

        cfg_path = os.path.join("cfg_db", testID, store_file_name)
        for _file in os.listdir(cfg_path):
            if _file == 'dict_if2cfgnode':
                fin = open(os.path.join(cfg_path, _file))
                dict_if2cfgnode = pickle.load(fin)
                fin.close()

            elif _file == 'dict_cfgnode2if':
                fin = open(os.path.join(cfg_path, _file))
                dict_cfgnode2if = pickle.load(fin)
                fin.close()

            else:
                print cfg_path
                fin = open(os.path.join(cfg_path, _file))
                cfg = pickle.load(fin)
                fin.close()

        i = 0
        while i < opt_pdg_1.vcount():
            if opt_pdg_1.vs[i]['type'] == 'Statement' and opt_pdg_1.vs[i]['name'] not in cfg.vs['name']:
                for n in cfg.vs:
                    if opt_pdg_1.vs[i]['code'] == n['code'] and int(opt_pdg_1.vs[i]['location'].split(':')[0]) == int(n['location'].split(':')[0]):
                        opt_pdg_1.vs[i]['name'] = n['name']
                        opt_pdg_1.vs[i]['location'] = n['location']
                        break
                    else:
                        continue

            i += 1

        d_use, d_def = getUseDefVarByPDG(j, opt_pdg_1)#get use and def nodedict of every cfgnode
        opt_pdg_2 = modifyDataEdgeVal(opt_pdg_1)#not distinguish pointer and buffer it points      
        
        opt_pdg_3 = completeDeclStmtOfPDG(opt_pdg_2, d_use, d_def, dict_if2cfgnode, dict_cfgnode2if)

        opt_pdg_4 = completeDataEdgeOfPDG(opt_pdg_3, d_use, d_def, dict_if2cfgnode, dict_cfgnode2if)#add data edge to get more info
        
        opted_pdg_5 = addDataEdgeOfObject(opt_pdg_4, dict_if2cfgnode, dict_cfgnode2if)
      
        #opted_pdg=deleteCDG(opted_pdg_5)
        

        if not os.path.exists(path):
            os.mkdir(path)
        print store_path, path    
        f = open(store_path, 'wb')
        pickle.dump(opted_pdg_5, f, True)
        f.close()
    

if __name__ == '__main__':
    main()             



