## coding:utf-8
from joern.all import JoernSteps
from igraph import *
from access_db_operate import *
from slice_op import *
from py2neo.packages.httpstream import http
http.socket_timeout = 9999


def get_slice_file_sequence(store_filepath, list_result, count, func_name, startline, filepath_all):
    #Extract dat a stream of every node ,filepath is path to save data stream,list_result is data stream,func_name is name of function.
    #src_vulnline_num is point,vulnline_row is the location of point in the data stream.
    list_for_line = []
    statement_line = 0
    vulnline_row = 0
    list_write2file = []

    for node in list_result:    
        if node['type'] == 'Function':
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            raw = int(node['location'].split(':')[0])-1
            code = content[raw].strip()

            new_code = ""
            if code.find("#define") != -1:
                list_write2file.append(code + ' ' + str(raw+1) + '\n')
                continue

            while (len(code) >= 1 and code[-1] != ')' and code[-1] != '{'):
                if code.find('{') != -1:
                    index = code.index('{')
                    new_code += code[:index].strip()
                    list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                    break

                else:
                    new_code += code + '\n'
                    raw += 1
                    code = content[raw].strip()

            else:
                new_code += code
                new_code = new_code.strip()
                if new_code[-1] == '{':
                    new_code = new_code[:-1].strip()
                    list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                else:
                    list_write2file.append(new_code + ' ' + str(raw+1) + '\n')

        elif node['type'] == 'Condition':
            raw = int(node['location'].split(':')[0])-1
            if raw in list_for_line:
                continue
            else:
                f2 = open(node['filepath'], 'r')
                content = f2.readlines()
                f2.close()
                code = content[raw].strip()
                pattern = re.compile("(?:if|while|for|switch)")
                res = re.search(pattern, code)
                if res == None:
                    raw = raw - 1
                    code = content[raw].strip()
                    new_code = ""

                    while (code[-1] != ')' and code[-1] != '{'):
                        if code.find('{') != -1:
                            index = code.index('{')
                            new_code += code[:index].strip()
                            list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                            list_for_line.append(raw)
                            break

                        else:
                            new_code += code + '\n'
                            list_for_line.append(raw)
                            raw += 1
                            code = content[raw].strip()

                    else:
                        new_code += code
                        new_code = new_code.strip()
                        if new_code[-1] == '{':
                            new_code = new_code[:-1].strip()
                            list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                            list_for_line.append(raw)

                        else:
                            list_for_line.append(raw)
                            list_write2file.append(new_code + ' ' + str(raw+1) + '\n')

                else:
                    res = res.group()
                    if res == '':
                        exit()

                    elif res != 'for':
                        new_code = res + ' ( ' + node['code'] + ' ) '
                        list_write2file.append(new_code + ' ' + str(raw+1) + '\n')

                    else:
                        new_code = ""
                        if code.find(' for ') != -1:
                            code = 'for ' + code.split(' for ')[1]

                        while code != '' and code[-1] != ')' and code[-1] != '{':
                            if code.find('{') != -1:
                                index = code.index('{')
                                new_code += code[:index].strip()
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                list_for_line.append(raw)
                                break

                            elif code[-1] == ';' and code[:-1].count(';') >= 2:
                                new_code += code
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                list_for_line.append(raw)
                                break

                            else:
                                new_code += code + '\n'
                                list_for_line.append(raw)
                                raw += 1
                                code = content[raw].strip()

                        else:
                            new_code += code
                            new_code = new_code.strip()
                            if new_code[-1] == '{':
                                new_code = new_code[:-1].strip()
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                list_for_line.append(raw)

                            else:
                                list_for_line.append(raw)
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
        
        elif node['type'] == 'Label':
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            raw = int(node['location'].split(':')[0])-1
            code = content[raw].strip()
            list_write2file.append(code + ' ' + str(raw+1) + '\n')

        elif node['type'] == 'ForInit':
            continue

        elif node['type'] == 'Parameter':
            if list_result[0]['type'] != 'Function':
                row = node['location'].split(':')[0]
                list_write2file.append(node['code'] + ' ' + str(row) + '\n')
            else:
                continue

        elif node['type'] == 'IdentifierDeclStatement':
            if node['code'].strip().split(' ')[0] == "undef":
                f2 = open(node['filepath'], 'r')
                content = f2.readlines()
                f2.close()
                raw = int(node['location'].split(':')[0])-1
                code1 = content[raw].strip()
                list_code2 = node['code'].strip().split(' ')
                i = 0
                while i < len(list_code2):
                    if code1.find(list_code2[i]) != -1:
                        del list_code2[i]
                    else:
                        break
                code2 = ' '.join(list_code2)

                list_write2file.append(code1 + ' ' + str(raw+1) + '\n' + code2 + ' ' + str(raw+2) + '\n')

            else:
                list_write2file.append(node['code'] + ' ' + node['location'].split(':')[0] + '\n')

        elif node['type'] == 'ExpressionStatement':
            row = int(node['location'].split(':')[0])-1
            if row in list_for_line:
                continue

            if node['code'] in ['\n', '\t', ' ', '']:
                list_write2file.append(node['code'] + ' ' + str(row+1) + '\n')
            elif node['code'].strip()[-1] != ';':
                list_write2file.append(node['code'] + '; ' + str(row+1) + '\n')
            else:
                list_write2file.append(node['code'] + ' ' + str(row+1) + '\n')

        elif node['type'] == "Statement":
            row = node['location'].split(':')[0]
            list_write2file.append(node['code'] + ' ' + str(row) + '\n')

        else:         
            if node['location'] == None:
                continue
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            row = int(node['location'].split(':')[0])-1
            code = content[row].strip()
            if row in list_for_line:
                continue

            else:
                list_write2file.append(node['code'] + ' ' + str(row+1) + '\n')

    f = open(store_filepath, 'a')
    f.write(str(count) + ' ' + filepath_all + ' ' + func_name + ' ' + startline + '\n')
    for wb in list_write2file:
        f.write(wb)
    f.write('------------------------------' + '\n')     
    f.close()


def program_slice(pdg, startnodesID, slicetype, testID):#process startnodes as a list, because main func has many different arguments
    #Get slices.StartnodesID is a list saves the start node of a slice, slicetype defines the direction of get slice, testID is the testID or CVE of the data.
    list_startnodes = []
    if pdg == False or pdg == None:
        return [], [], []
        
    for node in pdg.vs:
        if node['name'] in startnodesID:
            list_startnodes.append(node)

    if list_startnodes == []:
        return [], [], []

    if slicetype == 0:#backwords
        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        startline_path = list_startnodes[0]['filepath']
        results_back = program_slice_backwards(pdg, list_startnodes)

        not_scan_func_list = []
        results_back, temp = process_cross_func(results_back, testID, 1, results_back, not_scan_func_list)


        return [results_back], start_line, startline_path

    elif slicetype == 1:#forwords
        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        startline_path = list_startnodes[0]['filepath']
        results_for = program_slice_forward(pdg, list_startnodes)

        not_scan_func_list = []
        results_for, temp = process_cross_func(results_for, testID, 1, results_for, not_scan_func_list)

        return [results_for], start_line, startline_path

    else:#bi_direction
        print "start extract backwords dataflow!"

        start_line = list_startnodes[0]['location'].split(':')[0]
        start_name = list_startnodes[0]['name']
        startline_path = list_startnodes[0]['filepath']
        results_back = program_slice_backwards(pdg, list_startnodes)#results_back is a list of nodes

        results_for = program_slice_forward(pdg, list_startnodes)      
        

        _list_name = []
        for node_back in results_back:
            _list_name.append(node_back['name'])

        for node_for in results_for:
            if node_for['name'] in _list_name:
                continue
            else:
                results_back.append(node_for)

        results_back = sortedNodesByLoc(results_back)
       
        iter_times = 0
        start_list = [[results_back, iter_times]]
        i = 0
        not_scan_func_list = []
        list_cross_func_back, not_scan_func_list = process_crossfuncs_back_byfirstnode(start_list, testID, i, not_scan_func_list)
        list_results_back = [l[0] for l in list_cross_func_back]
      
        all_result = [] 
        for results_back in list_results_back:
            index = 1
            for a_node in results_back:
                if a_node['name'] == start_name:
                    break
                else:
                    index += 1

            list_to_crossfunc_back = results_back[:index]
            list_to_crossfunc_for = results_back[index:]

            list_to_crossfunc_back, temp = process_cross_func(list_to_crossfunc_back, testID, 0, list_to_crossfunc_back, not_scan_func_list)

            list_to_crossfunc_for, temp = process_cross_func(list_to_crossfunc_for, testID, 1, list_to_crossfunc_for, not_scan_func_list)

            all_result.append(list_to_crossfunc_back + list_to_crossfunc_for)
  

        return all_result, start_line, startline_path


def api_slice():
    count = 1
    store_filepath = "slice/api_slices.txt"
    f = open("sensifunc_slice_points.pkl", 'rb')
    dict_unsliced_sensifunc = pickle.load(f)
    f.close()

    for key in dict_unsliced_sensifunc.keys():#key is testID

        for _t in dict_unsliced_sensifunc[key]:
            list_sensitive_funcid = _t[0]
            pdg_funcid = _t[1]
            sensitive_funcname = _t[2]

            if sensitive_funcname.find("main") != -1:
                continue #todo
            else:
                slice_dir = 2
                pdg = getFuncPDGById(key, pdg_funcid)
                if pdg == False:
                    print 'error'
                    exit()

                list_code, startline, startline_path = program_slice(pdg, list_sensitive_funcid, slice_dir, key)

                if list_code == []:
                    fout = open("error.txt", 'a')
                    fout.write(sensitive_funcname + ' ' + str(list_sensitive_funcid) + ' found nothing! \n')
                    fout.close()
                else:
                    for _list in list_code:
                        get_slice_file_sequence(store_filepath, _list, count, sensitive_funcname, startline, startline_path)
                        count += 1

def pointers_slice():
    count = 1
    store_filepath = "slice/pointersuse_slices.txt"
    f = open("pointuse_slice_points.pkl", 'rb')
    dict_unsliced_pointers = pickle.load(f)
    print dict_unsliced_pointers
    f.close()

    l = ['CVE-2015-4521', 'CVE-2015-4482', 'CVE-2016-2824', 'CVE-2015-4487', 'CVE-2014-2894', 'CVE-2015-4484', 'CVE-2016-4002', 'CVE-2015-2729', 'CVE-2015-4500', 'CVE-2015-4501', 'CVE-2016-5238', 'CVE-2014-5263', 'CVE-2015-2726', 'CVE-2013-4526', 'CVE-2014-0223', 'CVE-2013-4527', 'CVE-2016-2814', 'CVE-2015-7178', 'CVE-2015-7179', 'CVE-2013-4530', 'CVE-2013-4533', 'CVE-2015-8662', 'CVE-2015-7176', 'CVE-2016-1714', 'CVE-2015-7174', 'CVE-2015-7175', 'CVE-2016-9104', 'CVE-2016-5280', 'CVE-2016-9101', 'CVE-2016-9103', 'CVE-2016-2819', 'CVE-2016-2818', 'CVE-2015-0829', 'CVE-2016-4952', 'CVE-2015-4511', 'CVE-2015-4512', 'CVE-2015-4517', 'CVE-2014-9676', 'CVE-2013-6399', 'CVE-2016-8910', 'CVE-2013-0866', 'CVE-2013-4542', 'CVE-2015-3395', 'CVE-2016-6351', 'CVE-2016-9923', 'CVE-2013-0860', 'CVE-2016-1957', 'CVE-2016-1956', 'CVE-2013-7020', 'CVE-2013-7021', 'CVE-2016-1953', 'CVE-2016-1952', 'CVE-2013-0868', 'CVE-2014-8541', 'CVE-2016-1970', 'CVE-2014-9319', 'CVE-2014-8542', 'CVE-2016-7421', 'CVE-2014-8544', 'CVE-2014-8547', 'CVE-2016-7161', 'CVE-2014-7937', 'CVE-2015-1872', 'CVE-2014-9317', 'CVE-2014-9316', 'CVE-2014-7933', 'CVE-2016-5258', 'CVE-2016-5259', 'CVE-2015-7512', 'CVE-2014-3640', 'CVE-2016-5106', 'CVE-2016-5107', 'CVE-2016-4453', 'CVE-2015-7203', 'CVE-2016-6835', 'CVE-2016-4454', 'CVE-2016-5256', 'CVE-2016-5257', 'CVE-2015-7220', 'CVE-2015-7221', 'CVE-2015-4504', 'CVE-2016-7170', 'CVE-2016-5278', 'CVE-2015-7180', 'CVE-2016-1981', 'CVE-2016-8909', 'CVE-2016-2836', 'CVE-2016-2857', 'CVE-2013-0858', 'CVE-2014-0182', 'CVE-2013-0856', 'CVE-2013-0857', 'CVE-2016-5403', 'CVE-2014-2099', 'CVE-2014-2098', 'CVE-2015-1779', 'CVE-2016-6833', 'CVE-2014-2097', 'CVE-2015-4493', 'CVE-2015-0825', 'CVE-2015-0824', 'CVE-2016-2837', 'CVE-2015-0826', 'CVE-2016-5254', 'CVE-2016-4441', 'CVE-2015-7194', 'CVE-2015-6820', 'CVE-2013-4149', 'CVE-2015-7198', 'CVE-2015-7199', 'CVE-2015-2710', 'CVE-2015-2712', 'CVE-2013-7022', 'CVE-2013-7023', 'CVE-2013-0845', 'CVE-2016-7466', 'CVE-2015-7202', 'CVE-2013-4151', 'CVE-2013-4150', 'CVE-2016-8668']
    for key in dict_unsliced_pointers.keys():#key is testID
        print key
        if key in l:
            continue

        for _t in dict_unsliced_pointers[key]:
            list_pointers_funcid = _t[0]
            pdg_funcid = _t[1]
            print key, pdg_funcid
            pointers_name = str(_t[2])


            slice_dir = 2
            pdg = getFuncPDGById(key, pdg_funcid)
            if pdg == False:
                print 'error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_pointers_funcid, slice_dir, key)

            if list_code == []:
                fout = open("error.txt", 'a')
                fout.write(pointers_name + ' ' + str(list_pointers_funcid) + ' found nothing! \n')
                fout.close()
            else:
                for _list in list_code:
                    get_slice_file_sequence(store_filepath, _list, count, pointers_name, startline, startline_path)
                    count += 1


def arrays_slice():
    count = 1
    store_filepath = "slice/arraysuse_slices.txt"
    f = open("arrayuse_slice_points.pkl", 'rb')
    dict_unsliced_pointers = pickle.load(f)
    f.close()
    l = []
    for key in dict_unsliced_pointers.keys():#key is testID
        if key in l:
            continue

        for _t in dict_unsliced_pointers[key]:
            list_pointers_funcid = _t[0]
            pdg_funcid = _t[1]
            print pdg_funcid
            arrays_name = str(_t[2])


            slice_dir = 2
            pdg = getFuncPDGById(key, pdg_funcid)
            if pdg == False:
                print 'error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_pointers_funcid, slice_dir, key)

            if list_code == []:
                fout = open("error.txt", 'a')
                fout.write(arrays_name + ' ' + str(list_pointers_funcid) + ' found nothing! \n')
                fout.close()
            else:
                for _list in list_code:
                    get_slice_file_sequence(store_filepath, _list, count, arrays_name, startline, startline_path)
                    count += 1


def integeroverflow_slice():
    count = 1
    store_filepath = "slice/integeroverflow_slices.txt"
    f = open("integeroverflow_slice_points_new.pkl", 'rb')
    dict_unsliced_expr = pickle.load(f)
    f.close()

    l = ['CVE-2016-5259', 'CVE-2015-7512', 'CVE-2014-3640', 'CVE-2016-5106', 'CVE-2016-5107', 'CVE-2016-4453', 'CVE-2015-4475', 'CVE-2016-6835', 'CVE-2016-4454', 'CVE-2016-5257', 'CVE-2015-7220', 'CVE-2015-7221', 'CVE-2016-5278', 'CVE-2016-1981', 'CVE-2015-2726', 'CVE-2016-2857', 'CVE-2013-0858', 'CVE-2014-0182', 'CVE-2013-0856', 'CVE-2013-0857', 'CVE-2016-5403', 'CVE-2014-2099', 'CVE-2014-2098', 'CVE-2015-1779', 'CVE-2016-6833', 'CVE-2014-2097', 'CVE-2015-7203', 'CVE-2015-7194', 'CVE-2015-6820', 'CVE-2015-7199', 'CVE-2015-2710', 'CVE-2016-4952', 'CVE-2015-2712', 'CVE-2013-7022', 'CVE-2013-7023', 'CVE-2013-0845', 'CVE-2016-7466', 'CVE-2015-7202', 'CVE-2013-4151', 'CVE-2013-4150', 'CVE-2016-8668']
    for key in dict_unsliced_expr.keys():#key is testID

        if key in l:
            continue
        for _t in dict_unsliced_expr[key]:
            list_expr_funcid = _t[0]
            pdg_funcid = _t[1]
            print pdg_funcid
            expr_name = str(_t[2])


            slice_dir = 2
            pdg = getFuncPDGById(key, pdg_funcid)
            if pdg == False:
                print 'error'
                exit()

            list_code, startline, startline_path = program_slice(pdg, list_expr_funcid, slice_dir, key)

            if list_code == []:
                fout = open("error.txt", 'a')
                fout.write(expr_name + ' ' + str(list_expr_funcid) + ' found nothing! \n')
                fout.close()
            else:
                for _list in list_code:
                    get_slice_file_sequence(store_filepath, _list, count, expr_name, startline, startline_path)
                    count += 1
     

if __name__ == "__main__":
    api_slice()
    pointers_slice()
    arrays_slice()
    integeroverflow_slice()
