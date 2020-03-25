# -- coding: utf-8 --
from access_db_operate import *
from complete_PDG import *
import re
from py2neo.packages.httpstream import http
http.socket_timeout = 9999


def getSubCFGGraph(startNode, list_node, not_scan_list):
    #print "startNode", startNode['code']
    #print ""
    if startNode['name'] in not_scan_list or startNode['code'] == 'EXIT':
        return list_node, not_scan_list

    else:
        list_node.append(startNode)
        not_scan_list.append(startNode['name'])

    successors = startNode.successors()
    if successors != []:
        for p_node in successors:
            #print "P_node", p_node['name'], p_node['code']  
            list_node, not_scan_list = getSubCFGGraph(p_node, list_node, not_scan_list)

    return list_node, not_scan_list

print
def getCtrlRealtionOfCFG(cfg):

    list_ifstmt_nodes = []
    for node in cfg.vs:
        if node['type'] == 'Condition':
            filepath = node['filepath']
            location_row = int(node['location'].split(':')[0])
            fin = open(filepath, 'r')
            content = fin.readlines()
            fin.close()
            src_code = content[location_row-1]

            pattern = re.compile("(?:if|while|for|switch)")
            #print src_code, node['name']
            result = re.search(pattern, src_code)
            if result == None:
                res = 'for'
            else:
                res = result.group()
            if res == '':
                print "error!"
                exit()

            elif res == 'if':
                list_ifstmt_nodes.append(node)
            
            else:
                continue

        else:
            continue

    _dict = {}
    for if_node in list_ifstmt_nodes:
        list_truestmt_nodes = []
        list_falsestmt_nodes = []
        for es in cfg.es:
            if cfg.vs[es.tuple[0]] == if_node and es['var'] == 'True':
                
                start_node = cfg.vs[es.tuple[1]]
                
                not_scan_list = [if_node['name']]
                list_truestmt_nodes, temp = getSubCFGGraph(start_node, list_truestmt_nodes, not_scan_list)

            elif cfg.vs[es.tuple[0]] == if_node and es['var'] == 'False':
                
                start_node = cfg.vs[es.tuple[1]]              
                not_scan_list = [if_node['name']]
                list_falsestmt_nodes, temp = getSubCFGGraph(start_node, list_falsestmt_nodes, not_scan_list)

            else:
                continue

        _share_list = []
        for t_node in list_truestmt_nodes:
            if t_node in list_falsestmt_nodes:
                _share_list.append(t_node)
            else:
                continue

        if _share_list != []:
            i = 0
            while i < len(list_truestmt_nodes):
                if list_truestmt_nodes[i] in _share_list:
                    del list_truestmt_nodes[i]
                else:
                    i += 1

            i = 0
            while i < len(list_falsestmt_nodes):
                if list_falsestmt_nodes[i] in _share_list:
                    del list_falsestmt_nodes[i]
                else:
                    i += 1

            _dict[if_node['name']] = ([t_node['name'] for t_node in list_truestmt_nodes], [f_node['name'] for f_node in list_falsestmt_nodes])

        else:
            filepath = cfg.vs[0]['filepath']
            fin = open(filepath, 'r')
            content = fin.readlines()
            fin.close()

            if_line = int(if_node['location'].split(':')[0])-1
            #print list_truestmt_nodes
            if list_truestmt_nodes == []:
                continue
            sorted_list_truestmt_nodes = sortedNodesByLoc(list_truestmt_nodes)

            true_stmt_start = sorted_list_truestmt_nodes[0]
            start_line = int(true_stmt_start['location'].split(':')[0])
            str_if_stmts = '\n'.join(content[if_line:start_line])

            if '{' in str_if_stmts:
                if sorted_list_truestmt_nodes[-1]['location'] == None:
                    end_line = int(sorted_list_truestmt_nodes[-2]['location'].split(':')[0])
                else:
                    end_line = int(sorted_list_truestmt_nodes[-1]['location'].split(':')[0])

                list_stmt = content[if_line:end_line]
                left_brace = 0
                i = 0
                index = 0    
                tag = 0         
                for stmt in list_stmt:
                    for c in stmt:
                        if c == '{':
                            left_brace += 1

                        elif c == '}':
                            left_brace -= 1

                            if left_brace == 0:
                                tag = 1
                                break

                    if tag == 1:
                        break
                    else:
                        index += 1

                real_end_line = int(if_node['location'].split(':')[0]) + index

                list_real_true_stmt = []

                for node in sorted_list_truestmt_nodes:
                    if node['location'] == None:
                        continue

                    if int(node['location'].split(':')[0]) >= if_line+1 and int(node['location'].split(':')[0]) <= real_end_line:
                        list_real_true_stmt.append(node)

            else:
                list_real_true_stmt = [true_stmt_start]

            if list_falsestmt_nodes == []:
                continue
            sorted_list_falsestmt_nodes = sortedNodesByLoc(list_falsestmt_nodes)
            

            false_stmt_start = sorted_list_falsestmt_nodes[0]
            if sorted_list_truestmt_nodes[-1]['location'] != None:
                start_line = int(sorted_list_truestmt_nodes[-1]['location'].split(':')[0])
            else:
                start_line = int(sorted_list_truestmt_nodes[-2]['location'].split(':')[0])
            end_line = int(false_stmt_start['location'].split(':')[0])


            str_else_stmts = '\n'.join(content[start_line:end_line])

            if 'else' in str_else_stmts:                
                else_line = 0
                for line in content[start_line:end_line]:
                    if 'else' in line:
                        break
                    else:
                        else_line += 1

                real_else_line = start_line + else_line + 1
                str_else_stmts = str_else_stmts.split('else')[1]

                if '{' in str_else_stmts:
                    if sorted_list_falsestmt_nodes[-1]['location'] != None:
                        end_line = int(sorted_list_falsestmt_nodes[-1]['location'].split(':')[0])
                    elif sorted_list_falsestmt_nodes[-2]['location'] != None:
                        end_line = int(sorted_list_falsestmt_nodes[-2]['location'].split(':')[0])
                    else:
                        end_line = int(sorted_list_falsestmt_nodes[-3]['location'].split(':')[0])
                    list_stmt = content[real_else_line-1:end_line]
                    left_brace = 0
                    i = 0
                    index = 0    
                    tag = 0         
                    for stmt in list_stmt:
                        for c in stmt:
                            if c == '{':
                                left_brace += 1

                            elif c == '}':
                                left_brace -= 1

                                if left_brace == 0:
                                    tag = 1
                                    break

                        if tag == 1:
                            break
                        else:
                            index += 1

                    real_end_line = int(if_node['location'].split(':')[0]) + index
                    #print "real_end_line", real_end_line
                    list_real_false_stmt = []

                    for node in sorted_list_falsestmt_nodes:
                        if node['location'] == None:
                            continue

                        if int(node['location'].split(':')[0]) >= if_line+1 and int(node['location'].split(':')[0]) <= real_end_line:
                            list_real_false_stmt.append(node)

                else:
                    list_real_false_stmt = [false_stmt_start]
                    print "false_stmt_start", false_stmt_start['name']

            else:
                list_real_false_stmt = []

            _dict[if_node['name']] = ([t_node['name'] for t_node in list_real_true_stmt], [f_node['name'] for f_node in list_real_false_stmt])


    return _dict


def completeDataEdgeOfCFG(cfg):
    list_ordered_list = sortedNodesByLoc(cfg.vs)

    for node in list_ordered_list:
        if node['type'] == 'Statement':
            list_pre = node.predecessors()
            list_su = node.successors()

            if list_pre == [] or list_pre == None:
                index = list_ordered_list.index(node)
                start_node = list_ordered_list[index-1]['name']
                end_node = node['name']
                var = None
                addDataEdge(cfg, start_node, end_node, var)

            if list_su == [] or list_su == None:
                index = list_ordered_list.index(node)
                start_node = node['name']
                end_node = list_ordered_list[index+1]['name']
                var = None
                addDataEdge(cfg, start_node, end_node, var)

    return cfg


def main():
    j = JoernSteps()
    j.connectToDatabase()
    all_func_node = getALLFuncNode(j)
    for node in all_func_node:
        testID = getFuncFile(j, node._id).split('/')[-2]
        path = os.path.join("cfg_db", testID)

        store_file_name = node.properties['name'] + '_' + str(node._id)
        store_path = os.path.join(path, store_file_name)

        initcfg = translateCFGByNode(j, node)#get init CFG
        opt_cfg_1 = modifyStmtNode(initcfg)
        cfg = completeDataEdgeOfCFG(opt_cfg_1)
        _dict = getCtrlRealtionOfCFG(cfg)

        _dict_node2ifstmt = {}
        for key in _dict.keys():
            _list = _dict[key][0] + _dict[key][1]
            for v in _list:
                if v not in _dict_node2ifstmt.keys():
                    _dict_node2ifstmt[v] = [key]

                else:
                    _dict_node2ifstmt[v].append(key)

        for key in _dict_node2ifstmt.keys():
            _dict_node2ifstmt[key] = list(set(_dict_node2ifstmt[key]))

        if not os.path.exists(path):
            os.mkdir(path)

        if not os.path.exists(store_path):
            os.mkdir(store_path)
        else:
            continue
        
        filename = 'cfg'
        cfg_store_path = os.path.join(store_path, filename)
        fout = open(cfg_store_path, 'wb')
        pickle.dump(cfg, fout, True)
        fout.close()

        filename = 'dict_if2cfgnode'
        dict_store_path_1 = os.path.join(store_path, filename)
        fout = open(dict_store_path_1, 'wb')
        pickle.dump(_dict, fout, True)
        fout.close()

        filename = 'dict_cfgnode2if'
        dict_store_path_2 = os.path.join(store_path, filename)
        fout = open(dict_store_path_2, 'wb')
        pickle.dump(_dict_node2ifstmt, fout, True)
        fout.close()

        print node.properties['name']
        print _dict
        print _dict_node2ifstmt
        print ''


if __name__ == '__main__':
    main()
