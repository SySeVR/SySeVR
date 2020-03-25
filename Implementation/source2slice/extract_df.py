## coding:utf-8
from joern.all import JoernSteps
from igraph import *
from access_db_operate import *
from slice_op import *
from py2neo.packages.httpstream import http
http.socket_timeout = 9999


def get_slice_file_sequence(store_filepath, list_result, count, func_name, startline, filepath_all):
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
                    #print "raw", raw, code

            else:
                new_code += code
                new_code = new_code.strip()
                if new_code[-1] == '{':
                    new_code = new_code[:-1].strip()
                    list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                    #list_line.append(str(raw+1))
                else:
                    list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                    #list_line.append(str(raw+1))

        elif node['type'] == 'Condition':
            raw = int(node['location'].split(':')[0])-1
            if raw in list_for_line:
                continue
            else:
                #print node['type'], node['code'], node['name']
                f2 = open(node['filepath'], 'r')
                content = f2.readlines()
                f2.close()
                code = content[raw].strip()
                pattern = re.compile("(?:if|while|for|switch)")
                #print code
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
                            #list_line.append(str(raw+1))
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
                            #list_line.append(str(raw+1))
                            list_for_line.append(raw)

                        else:
                            list_for_line.append(raw)
                            list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                            #list_line.append(str(raw+1))

                else:
                    res = res.group()
                    if res == '':
                        print filepath_all + ' ' + func_name + " error!"
                        exit()

                    elif res != 'for':
                        new_code = res + ' ( ' + node['code'] + ' ) '
                        list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                        #list_line.append(str(raw+1))

                    else:
                        new_code = ""
                        if code.find(' for ') != -1:
                            code = 'for ' + code.split(' for ')[1]

                        while code != '' and code[-1] != ')' and code[-1] != '{':
                            if code.find('{') != -1:
                                index = code.index('{')
                                new_code += code[:index].strip()
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                #list_line.append(str(raw+1))
                                list_for_line.append(raw)
                                break

                            elif code[-1] == ';' and code[:-1].count(';') >= 2:
                                new_code += code
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                #list_line.append(str(raw+1))
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
                                #list_line.append(str(raw+1))
                                list_for_line.append(raw)

                            else:
                                list_for_line.append(raw)
                                list_write2file.append(new_code + ' ' + str(raw+1) + '\n')
                                #list_line.append(str(raw+1))
        
        elif node['type'] == 'Label':
            f2 = open(node['filepath'], 'r')
            content = f2.readlines()
            f2.close()
            raw = int(node['location'].split(':')[0])-1
            code = content[raw].strip()
            list_write2file.append(code + ' ' + str(raw+1) + '\n')
            #list_line.append(str(raw+1))

        elif node['type'] == 'ForInit':
            continue

        elif node['type'] == 'Parameter':
            if list_result[0]['type'] != 'Function':
                row = node['location'].split(':')[0]
                list_write2file.append(node['code'] + ' ' + str(row) + '\n')
                #list_line.append(row)
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
                #list_line.append(row+1)
            elif node['code'].strip()[-1] != ';':
                list_write2file.append(node['code'] + '; ' + str(row+1) + '\n')
                #list_line.append(row+1)
            else:
                list_write2file.append(node['code'] + ' ' + str(row+1) + '\n')
                #list_line.append(row+1)

        elif node['type'] == "Statement":
            row = node['location'].split(':')[0]
            list_write2file.append(node['code'] + ' ' + str(row) + '\n')
            #list_line.append(row+1)

        else:         
            #print node['name'], node['code'], node['type'], node['filepath']
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
                #list_line.append(str(row+1))

    f = open(store_filepath, 'a')
    f.write(str(count) + ' ' + filepath_all + ' ' + func_name + ' ' + startline + '\n')
    for wb in list_write2file:
        f.write(wb)
    f.write('------------------------------' + '\n')     
    f.close()


def program_slice(pdg, startnodesID, slicetype, testID):#process startnodes as a list, because main func has many different arguments
    list_startnodes = []
    if pdg == False or pdg == None:
        return [], [], []
        
    for node in pdg.vs:
        #print node['functionId']
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
        print "start extract forword dataflow!"
        print list_startnodes, startnodesID
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
    store_filepath = "C/test_data/4/api_slices.txt"
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
                #print len(list_code)

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
    store_filepath = "C/test_data/4/pointersuse_slices.txt"
    f = open("pointuse_slice_points.pkl", 'rb')
    dict_unsliced_pointers = pickle.load(f)
    print dict_unsliced_pointers
    f.close()

    #l = ['CVE-2013-4921', 'CVE-2013-4514', 'CVE-2015-1158', 'CVE-2015-1159', 'CVE-2005-3806', 'CVE-2012-6647', 'CVE-2012-2123', 'CVE-2015-0239', 'CVE-2013-2596', 'CVE-2008-5713', 'CVE-2015-2192', 'CVE-2015-2191', 'CVE-2006-5751', 'CVE-2014-1690', 'CVE-2012-5354', 'CVE-2008-3527', 'CVE-2004-1151', 'CVE-2011-0059', 'CVE-2008-3833', 'CVE-2010-4258', 'CVE-2014-2241', 'CVE-2011-2689', 'CVE-2011-2723', 'CVE-2014-4655', 'CVE-2014-4654', 'CVE-2010-0727', 'CVE-2014-4656', 'CVE-2014-4652', 'CVE-2009-2909', 'CVE-2008-1514', 'CVE-2014-3534', 'CVE-2014-3537', 'CVE-2012-1947', 'CVE-2012-5670', 'CVE-2011-1759', 'CVE-2011-1750', 'CVE-2007-0006', 'CVE-2010-4805', 'CVE-2013-2015', 'CVE-2014-3122', 'CVE-2011-0085', 'CVE-2011-0084', 'CVE-2011-0083', 'CVE-2007-6151', 'CVE-2009-3547', 'CVE-2012-0044', 'CVE-2014-8133', 'CVE-2009-3238', 'CVE-2012-0041', 'CVE-2009-3234', 'CVE-2013-4220', 'CVE-2014-0203', 'CVE-2011-1138', 'CVE-2005-3807', 'CVE-2014-3523', 'CVE-2013-0854', 'CVE-2010-3877', 'CVE-2013-0913', 'CVE-2013-1732', 'CVE-2014-8884', 'CVE-2013-1735', 'CVE-2013-1736', 'CVE-2013-0914', 'CVE-2010-2960', 'CVE-2010-2962', 'CVE-2010-2240', 'CVE-2009-0946', 'CVE-2012-3984', 'CVE-2010-1224', 'CVE-2014-1498', 'CVE-2012-6617', 'CVE-2012-6616', 'CVE-2010-0437', 'CVE-2010-1188', 'CVE-2012-2652', 'CVE-2006-4790', 'CVE-2013-0867', 'CVE-2013-0866', 'CVE-2014-1522', 'CVE-2013-0864', 'CVE-2013-0863', 'CVE-2010-3880', 'CVE-2013-0861', 'CVE-2013-0860', 'CVE-2014-3511', 'CVE-2013-0869', 'CVE-2013-0868', 'CVE-2008-5029', 'CVE-2006-4813', 'CVE-2011-0716', 'CVE-2013-1848', 'CVE-2008-5025', 'CVE-2011-0711', 'CVE-2011-0710', 'CVE-2013-0764', 'CVE-2005-2261', 'CVE-2010-2500', 'CVE-2013-0761', 'CVE-2012-1090', 'CVE-2014-0155', 'CVE-2012-1097', 'CVE-2009-3640', 'CVE-2011-3363', 'CVE-2011-3362', 'CVE-2015-2922', 'CVE-2012-0464', 'CVE-2014-2099', 'CVE-2014-9661', 'CVE-2014-9665', 'CVE-2014-8712', 'CVE-2014-8713', 'CVE-2014-8714', 'CVE-2014-7841', 'CVE-2014-7842', 'CVE-2012-3377', 'CVE-2014-1552', 'CVE-2012-0855', 'CVE-2009-0675', 'CVE-2012-5237', 'CVE-2010-4346', 'CVE-2014-1950', 'CVE-2012-5238', 'CVE-2009-1961', 'CVE-2014-9584', 'CVE-2010-2226', 'CVE-2015-0562', 'CVE-2013-0166', 'CVE-2014-5271', 'CVE-2014-5272', 'CVE-2014-3470', 'CVE-2015-0204', 'CVE-2008-1390', 'CVE-2011-1080', 'CVE-2012-1146', 'CVE-2011-3944', 'CVE-2011-2896', 'CVE-2012-3430', 'CVE-2008-3276', 'CVE-2008-3275', 'CVE-2008-3272', 'CVE-2012-2776', 'CVE-2013-4933', 'CVE-2013-4587', 'CVE-2009-0935', 'CVE-2011-1712', 'CVE-2013-0796', 'CVE-2010-4656', 'CVE-2010-2478', 'CVE-2015-0228', 'CVE-2009-0269', 'CVE-2013-1573', 'CVE-2013-4929', 'CVE-2013-6339', 'CVE-2012-3979', 'CVE-2010-4163', 'CVE-2012-3976', 'CVE-2012-2802', 'CVE-2010-4649', 'CVE-2012-3972', 'CVE-2010-4165', 'CVE-2009-0859', 'CVE-2009-3722', 'CVE-2012-4186', 'CVE-2012-4184', 'CVE-2009-3726', 'CVE-2012-2313', 'CVE-2011-2535', 'CVE-2011-2534', 'CVE-2011-2536', 'CVE-2010-3080', 'CVE-2012-0957', 'CVE-2011-3936', 'CVE-2012-1952', 'CVE-2011-3934', 'CVE-2012-1956', 'CVE-2012-1955', 'CVE-2010-3855', 'CVE-2010-3858', 'CVE-2012-1958', 'CVE-2013-4162', 'CVE-2012-3975', 'CVE-2009-3290', 'CVE-2012-4204', 'CVE-2012-0451', 'CVE-2012-4207', 'CVE-2014-1737', 'CVE-2013-0755', 'CVE-2014-1738', 'CVE-2012-3962', 'CVE-2013-0756', 'CVE-2013-0750', 'CVE-2010-4073', 'CVE-2005-2555', 'CVE-2010-2495', 'CVE-2012-2136', 'CVE-2012-2137', 'CVE-2010-2499', 'CVE-2015-3814', 'CVE-2015-3811', 'CVE-2005-2492', 'CVE-2015-3813', 'CVE-2015-3812', 'CVE-2013-0849', 'CVE-2014-3633', 'CVE-2014-3631', 'CVE-2012-0457', 'CVE-2012-0456', 'CVE-2005-4635', 'CVE-2013-7100', 'CVE-2011-2999', 'CVE-2011-2998', 'CVE-2010-2521', 'CVE-2011-2988', 'CVE-2006-5619', 'CVE-2009-3080', 'CVE-2010-4668', 'CVE-2013-2232', 'CVE-2013-2237', 'CVE-2014-7933', 'CVE-2011-1173', 'CVE-2013-4163', 'CVE-2013-3562', 'CVE-2013-3560', 'CVE-2010-3066', 'CVE-2015-5949', 'CVE-2005-3848', 'CVE-2006-2935', 'CVE-2006-2934', 'CVE-2010-1488', 'CVE-2005-3847', 'CVE-2009-4410', 'CVE-2013-4265', 'CVE-2013-4264', 'CVE-2009-3621', 'CVE-2013-0799', 'CVE-2013-1709', 'CVE-2011-3660', 'CVE-2011-3661', 'CVE-2015-2666', 'CVE-2013-0792', 'CVE-2013-4348', 'CVE-2015-0292', 'CVE-2013-2548', 'CVE-2012-1976', 'CVE-2013-6367', 'CVE-2006-1525', 'CVE-2010-0006', 'CVE-2010-1148', 'CVE-2014-8109', 'CVE-2010-0007', 'CVE-2013-1796', 'CVE-2013-0753', 'CVE-2011-4611', 'CVE-2013-1798', 'CVE-2008-2826', 'CVE-2011-4348', 'CVE-2013-6449', 'CVE-2014-1874', 'CVE-2010-0003', 'CVE-2011-1479', 'CVE-2013-1708', 'CVE-2013-7113', 'CVE-2013-1700', 'CVE-2013-1705', 'CVE-2013-1704', 'CVE-2013-1707', 'CVE-2010-1173', 'CVE-2010-2068', 'CVE-2006-1530', 'CVE-2012-2390', 'CVE-2009-1439', 'CVE-2012-2393', 'CVE-2011-3648', 'CVE-2012-6062', 'CVE-2015-4652', 'CVE-2011-1598', 'CVE-2013-4081', 'CVE-2007-4997', 'CVE-2013-4083', 'CVE-2013-4082', 'CVE-2011-1592', 'CVE-2012-6060', 'CVE-2009-1338', 'CVE-2006-4997', 'CVE-2013-7264', 'CVE-2012-5669', 'CVE-2006-6333', 'CVE-2013-1581', 'CVE-2013-6673', 'CVE-2012-0458', 'CVE-2013-0845', 'CVE-2010-3861', 'CVE-2012-4293', 'CVE-2012-4292', 'CVE-2012-4565', 'CVE-2009-4021', 'CVE-2014-6431', 'CVE-2014-6430', 'CVE-2014-4943', 'CVE-2012-4298', 'CVE-2011-1927', 'CVE-2011-1023', 'CVE-2007-1592', 'CVE-2009-0747', 'CVE-2009-0746', 'CVE-2011-1147', 'CVE-2012-5240', 'CVE-2014-1642', 'CVE-2012-2787', 'CVE-2012-2786', 'CVE-2012-0045', 'CVE-2012-2783', 'CVE-2013-4300', 'CVE-2012-2788', 'CVE-2006-2445', 'CVE-2011-0521', 'CVE-2006-2446', 'CVE-2011-2984', 'CVE-2015-0253', 'CVE-2014-8369', 'CVE-2014-0206', 'CVE-2006-2448', 'CVE-2008-3792', 'CVE-2011-2909', 'CVE-2010-2798', 'CVE-2009-1046', 'CVE-2014-2907', 'CVE-2014-3186', 'CVE-2013-3231', 'CVE-2013-3230', 'CVE-2011-2906', 'CVE-2013-3234', 'CVE-2007-1217', 'CVE-2014-1497', 'CVE-2011-2588', 'CVE-2013-1696', 'CVE-2011-2587', 'CVE-2013-1693', 'CVE-2012-2669', 'CVE-2011-2378', 'CVE-2011-2373', 'CVE-2008-4989', 'CVE-2011-2371', 'CVE-2010-4347', 'CVE-2014-4048', 'CVE-2011-3619', 'CVE-2010-4343', 'CVE-2010-4342', 'CVE-2010-4263', 'CVE-2013-2128', 'CVE-2013-5717', 'CVE-2014-9319', 'CVE-2014-9318', 'CVE-2013-2234', 'CVE-2013-7339', 'CVE-2014-9316', 'CVE-2013-5719', 'CVE-2013-1572', 'CVE-2013-1576', 'CVE-2011-4579', 'CVE-2010-1748', 'CVE-2013-1578', 'CVE-2012-0477', 'CVE-2014-3181', 'CVE-2014-3182', 'CVE-2014-3183', 'CVE-2014-3184', 'CVE-2014-3185', 'CVE-2006-5158', 'CVE-2013-0872', 'CVE-2013-0873', 'CVE-2013-0874', 'CVE-2013-3302', 'CVE-2013-0877', 'CVE-2013-0878', 'CVE-2011-3973', 'CVE-2009-3888', 'CVE-2013-4534', 'CVE-2015-6243', 'CVE-2015-6242', 'CVE-2013-4533', 'CVE-2013-4125', 'CVE-2014-8412', 'CVE-2013-4129', 'CVE-2015-6249', 'CVE-2011-1146', 'CVE-2011-1079', 'CVE-2015-6241', 'CVE-2010-1636', 'CVE-2014-0160', 'CVE-2013-0865', 'CVE-2012-6638', 'CVE-2010-3298', 'CVE-2012-6539', 'CVE-2010-1088', 'CVE-2014-9679', 'CVE-2010-1083', 'CVE-2014-9676', 'CVE-2012-6061', 'CVE-2010-1087', 'CVE-2010-1086', 'CVE-2010-1085', 'CVE-2009-3612', 'CVE-2015-3395', 'CVE-2013-7022', 'CVE-2013-7023', 'CVE-2013-7021', 'CVE-2013-7026', 'CVE-2013-7027', 'CVE-2013-7024', 'CVE-2013-5634', 'CVE-2012-3364', 'CVE-2012-0042', 'CVE-2008-0420', 'CVE-2011-1776', 'CVE-2010-3772', 'CVE-2005-4886', 'CVE-2014-2894', 'CVE-2011-1770', 'CVE-2010-3774', 'CVE-2005-3359', 'CVE-2013-1954', 'CVE-2014-5206', 'CVE-2012-2100', 'CVE-2014-4608', 'CVE-2009-2407', 'CVE-2005-3356', 'CVE-2011-1171', 'CVE-2010-2806', 'CVE-2013-7015', 'CVE-2010-2803', 'CVE-2014-3640', 'CVE-2009-2768', 'CVE-2010-2808', 'CVE-2009-0065', 'CVE-2013-4511', 'CVE-2008-3915', 'CVE-2010-2519', 'CVE-2012-4530', 'CVE-2014-2309', 'CVE-2014-7145', 'CVE-2010-3078', 'CVE-2007-6206', 'CVE-2007-4571', 'CVE-2010-2071', 'CVE-2013-1792', 'CVE-2011-2707', 'CVE-2011-3000', 'CVE-2011-2700', 'CVE-2011-3658', 'CVE-2013-4270', 'CVE-2011-3654', 'CVE-2011-3653', 'CVE-2014-9683', 'CVE-2005-3857', 'CVE-2014-1445', 'CVE-2013-5618', 'CVE-2013-1958', 'CVE-2009-2287', 'CVE-2013-0782', 'CVE-2011-1180', 'CVE-2011-1182', 'CVE-2013-6671', 'CVE-2013-3076', 'CVE-2013-5613', 'CVE-2013-5599', 'CVE-2009-0787', 'CVE-2011-1573', 'CVE-2010-2937', 'CVE-2007-1000', 'CVE-2013-2276', 'CVE-2013-5593', 'CVE-2013-4079', 'CVE-2011-1477', 'CVE-2013-5597', 'CVE-2009-0028', 'CVE-2014-1488', 'CVE-2008-4210', 'CVE-2014-1481', 'CVE-2014-1487', 'CVE-2010-2066', 'CVE-2013-5601', 'CVE-2015-3808', 'CVE-2015-3809', 'CVE-2013-7281', 'CVE-2014-3601', 'CVE-2011-0073', 'CVE-2013-4470', 'CVE-2013-0859', 'CVE-2012-4288', 'CVE-2012-4289', 'CVE-2012-0444', 'CVE-2011-2987', 'CVE-2013-6450', 'CVE-2012-4285', 'CVE-2012-4287', 'CVE-2014-9419', 'CVE-2013-6457', 'CVE-2013-2058', 'CVE-2010-4256', 'CVE-2010-4251', 'CVE-2014-2739', 'CVE-2014-6424', 'CVE-2011-0055', 'CVE-2011-0051', 'CVE-2014-2097', 'CVE-2012-3969', 'CVE-2012-1183', 'CVE-2012-1184', 'CVE-2010-4078', 'CVE-2013-0848', 'CVE-2010-4074', 'CVE-2008-5134', 'CVE-2010-4076', 'CVE-2012-3964', 'CVE-2012-3966', 'CVE-2010-4072', 'CVE-2009-3638', 'CVE-2013-2930', 'CVE-2014-9672', 'CVE-2012-6537', 'CVE-2012-4190', 'CVE-2014-1446', 'CVE-2014-2523', 'CVE-2014-1509', 'CVE-2014-6423', 'CVE-2014-1502', 'CVE-2012-1945', 'CVE-2012-1946', 'CVE-2010-3864', 'CVE-2012-1940', 'CVE-2013-0844', 'CVE-2012-1942', 'CVE-2014-0195', 'CVE-2010-3904', 'CVE-2013-7112', 'CVE-2010-3907', 'CVE-2009-1360', 'CVE-2014-7825', 'CVE-2006-1864', 'CVE-2013-4153', 'CVE-2013-4151', 'CVE-2013-4150', 'CVE-2013-1828', 'CVE-2013-4401', 'CVE-2014-6426', 'CVE-2011-1044', 'CVE-2009-1630', 'CVE-2012-0023', 'CVE-2011-4031', 'CVE-2012-2800', 'CVE-2012-2801', 'CVE-2010-2062', 'CVE-2012-2803', 'CVE-2013-7014', 'CVE-2008-2931', 'CVE-2012-6540', 'CVE-2013-4247', 'CVE-2011-3649', 'CVE-2015-3008', 'CVE-2012-0068', 'CVE-2012-6542', 'CVE-2011-3191', 'CVE-2014-9743', 'CVE-2013-1929', 'CVE-2009-2406', 'CVE-2006-0039', 'CVE-2009-1337', 'CVE-2014-1510', 'CVE-2011-3484', 'CVE-2006-0035', 'CVE-2013-5600', 'CVE-2012-2319', 'CVE-2013-1920', 'CVE-2013-7265', 'CVE-2010-3850', 'CVE-2013-7267', 'CVE-2014-2286', 'CVE-2011-4102', 'CVE-2012-5668', 'CVE-2011-4100', 'CVE-2010-3859', 'CVE-2015-4490', 'CVE-2010-4079', 'CVE-2014-1739', 'CVE-2012-0056', 'CVE-2011-1078', 'CVE-2011-4086', 'CVE-2014-0196', 'CVE-2013-3235', 'CVE-2013-6167', 'CVE-2014-8546', 'CVE-2015-3417', 'CVE-2011-3623', 'CVE-2014-0205', 'CVE-2014-6426', 'CVE-2014-6427', 'CVE-2014-6428', 'CVE-2014-6429', 'CVE-2005-2800', 'CVE-2014-7826', 'CVE-2014-1438', 'CVE-2012-6618', 'CVE-2012-6541', 'CVE-2015-0820', 'CVE-2015-0823', 'CVE-2011-1833', 'CVE-2009-1897', 'CVE-2012-2790', 'CVE-2012-2791', 'CVE-2012-2793', 'CVE-2012-2794', 'CVE-2009-3002', 'CVE-2009-3001', 'CVE-2012-2797', 'CVE-2011-2182', 'CVE-2011-2183', 'CVE-2011-2184', 'CVE-2013-5651', 'CVE-2009-2844', 'CVE-2009-2846', 'CVE-2014-3510', 'CVE-2014-8541', 'CVE-2013-3225', 'CVE-2013-3226', 'CVE-2014-8542', 'CVE-2014-2851', 'CVE-2014-8544', 'CVE-2013-3222', 'CVE-2010-3084', 'CVE-2014-8549', 'CVE-2013-4936', 'CVE-2013-3228', 'CVE-2013-3229', 'CVE-2011-3192', 'CVE-2013-0268', 'CVE-2013-1763', 'CVE-2011-1019', 'CVE-2013-1767', 'CVE-2012-2796', 'CVE-2013-1680', 'CVE-2012-0066', 'CVE-2011-1160', 'CVE-2011-0069', 'CVE-2013-2140', 'CVE-2011-2364', 'CVE-2011-2367', 'CVE-2014-2299', 'CVE-2011-1493', 'CVE-2011-2368', 'CVE-2011-1495', 'CVE-2014-0221', 'CVE-2013-4205', 'CVE-2013-2486', 'CVE-2013-2094', 'CVE-2013-7266', 'CVE-2015-6246', 'CVE-2013-4928', 'CVE-2011-0014', 'CVE-2013-2481', 'CVE-2011-1012', 'CVE-2011-1010', 'CVE-2008-5079', 'CVE-2010-4527', 'CVE-2010-4526', 'CVE-2015-6654', 'CVE-2013-4592', 'CVE-2013-4591', 'CVE-2010-1437', 'CVE-2011-2484', 'CVE-2011-2482', 'CVE-2014-8643', 'CVE-2006-0557', 'CVE-2011-3946', 'CVE-2011-3945', 'CVE-2014-8160', 'CVE-2014-9428', 'CVE-2011-3941', 'CVE-2013-1860', 'CVE-2014-9420', 'CVE-2011-3949', 'CVE-2013-4296', 'CVE-2013-4297', 'CVE-2013-2495', 'CVE-2012-2779', 'CVE-2013-4931', 'CVE-2013-4930', 'CVE-2013-6399', 'CVE-2013-4932', 'CVE-2013-4934', 'CVE-2014-1549', 'CVE-2009-2847', 'CVE-2013-0311', 'CVE-2013-0310', 'CVE-2013-0313', 'CVE-2011-1771', 'CVE-2010-1641', 'CVE-2014-0077', 'CVE-2012-6057', 'CVE-2012-6056', 'CVE-2012-6055', 'CVE-2012-6054', 'CVE-2012-6053', 'CVE-2012-3957', 'CVE-2014-5471', 'CVE-2014-9603', 'CVE-2009-3624', 'CVE-2014-9604', 'CVE-2012-6059', 'CVE-2012-6058', 'CVE-2013-7017', 'CVE-2013-2230', 'CVE-2014-2673', 'CVE-2014-2672', 'CVE-2013-7013', 'CVE-2013-7012', 'CVE-2013-7011', 'CVE-2011-0006', 'CVE-2013-0791', 'CVE-2013-0790', 'CVE-2013-0793', 'CVE-2012-5532', 'CVE-2013-0795', 'CVE-2014-8543', 'CVE-2013-7019', 'CVE-2013-7018', 'CVE-2009-2484', 'CVE-2009-4307', 'CVE-2013-1819', 'CVE-2012-1973', 'CVE-2014-8545', 'CVE-2009-4308', 'CVE-2012-2745', 'CVE-2011-3950', 'CVE-2011-1747', 'CVE-2014-8547', 'CVE-2011-1745', 'CVE-2011-2928', 'CVE-2014-2889', 'CVE-2010-0741', 'CVE-2011-3002', 'CVE-2011-3003', 'CVE-2012-6657', 'CVE-2009-1389', 'CVE-2009-4895', 'CVE-2008-5700', 'CVE-2009-1385', 'CVE-2006-5462', 'CVE-2006-5749', 'CVE-2013-7010', 'CVE-2008-3686', 'CVE-2014-1684', 'CVE-2012-3553', 'CVE-2009-1192', 'CVE-2015-3331', 'CVE-2008-2750', 'CVE-2009-4005', 'CVE-2015-3339', 'CVE-2010-4648', 'CVE-2009-2691', 'CVE-2011-2605', 'CVE-2014-7283', 'CVE-2011-4101', 'CVE-2013-7268', 'CVE-2013-7269', 'CVE-2013-2206', 'CVE-2011-0726', 'CVE-2010-3429', 'CVE-2014-2038', 'CVE-2009-1527', 'CVE-2014-1508', 'CVE-2004-0535', 'CVE-2011-2216', 'CVE-2012-0452', 'CVE-2011-4326', 'CVE-2011-4324', 'CVE-2011-2213', 'CVE-2011-4081', 'CVE-2011-4087', 'CVE-2012-0058', 'CVE-2008-1294', 'CVE-2010-4080', 'CVE-2010-4081', 'CVE-2009-4138', 'CVE-2010-4083', 'CVE-2011-2174', 'CVE-2014-4027', 'CVE-2011-3637', 'CVE-2009-3228', 'CVE-2009-0031', 'CVE-2013-1727', 'CVE-2013-1726', 'CVE-2011-1684', 'CVE-2010-4242', 'CVE-2014-6432', 'CVE-2007-3642', 'CVE-2013-4399', 'CVE-2010-4248', 'CVE-2014-3687', 'CVE-2012-3991', 'CVE-2007-4521', 'CVE-2014-0038', 'CVE-2010-3432', 'CVE-2013-6336', 'CVE-2013-2634', 'CVE-2013-2635', 'CVE-2013-2636', 'CVE-2009-1298', 'CVE-2012-0207', 'CVE-2009-2651', 'CVE-2006-2778', 'CVE-2012-2375', 'CVE-2013-0852', 'CVE-2006-1856', 'CVE-2006-1855', 'CVE-2013-0851', 'CVE-2013-0856', 'CVE-2010-3875', 'CVE-2010-3876', 'CVE-2013-0855', 'CVE-2013-1583', 'CVE-2013-1582', 'CVE-2013-1580', 'CVE-2013-1587', 'CVE-2013-1586', 'CVE-2013-1584', 'CVE-2013-6436', 'CVE-2013-1588', 'CVE-2013-4149', 'CVE-2010-1162', 'CVE-2010-4243', 'CVE-2010-2537', 'CVE-2013-0778', 'CVE-2010-2248', 'CVE-2013-0772', 'CVE-2013-0771', 'CVE-2010-0623', 'CVE-2013-0777', 'CVE-2010-2538', 'CVE-2013-0774', 'CVE-2011-0021', 'CVE-2011-3353', 'CVE-2012-0478', 'CVE-2014-3610', 'CVE-2014-3611', 'CVE-2012-0475', 'CVE-2012-0474', 'CVE-2012-0471', 'CVE-2012-0470', 'CVE-2014-9656', 'CVE-2014-9657', 'CVE-2005-4618', 'CVE-2006-3741', 'CVE-2014-8709', 'CVE-2014-9658', 'CVE-2013-0290', 'CVE-2013-3227', 'CVE-2012-4461', 'CVE-2009-1336', 'CVE-2014-7937', 'CVE-2012-1595', 'CVE-2012-1594', 'CVE-2015-0834', 'CVE-2015-0833', 'CVE-2013-4563', 'CVE-2012-0067', 'CVE-2006-6106', 'CVE-2011-2175', 'CVE-2011-2365', 'CVE-2014-4667', 'CVE-2005-2617', 'CVE-2010-0307', 'CVE-2014-4174', 'CVE-2013-5641', 'CVE-2013-5642', 'CVE-2011-1093', 'CVE-2013-6891', 'CVE-2014-3509', 'CVE-2013-1722', 'CVE-2010-2431', 'CVE-2013-3559', 'CVE-2013-3557', 'CVE-2013-4541', 'CVE-2014-8416', 'CVE-2014-8415', 'CVE-2014-8414', 'CVE-2011-1175', 'CVE-2013-1676', 'CVE-2011-1170', 'CVE-2011-0070', 'CVE-2013-1672', 'CVE-2011-2022', 'CVE-2012-1583', 'CVE-2013-1679', 'CVE-2013-1678', 'CVE-2011-0079', 'CVE-2012-6538', 'CVE-2014-2289', 'CVE-2014-2282', 'CVE-2014-2283', 'CVE-2010-3296', 'CVE-2011-1959', 'CVE-2011-3670', 'CVE-2010-3297', 'CVE-2013-4353', 'CVE-2009-1243', 'CVE-2009-1242', 'CVE-2010-2954', 'CVE-2010-2955', 'CVE-2014-9374', 'CVE-2008-4445', 'CVE-2012-2774', 'CVE-2013-2488', 'CVE-2013-1979', 'CVE-2011-4594', 'CVE-2009-0835', 'CVE-2013-6378', 'CVE-2011-4598', 'CVE-2011-2496', 'CVE-2012-6548', 'CVE-2014-5472', 'CVE-2013-2478', 'CVE-2009-2692', 'CVE-2013-2476', 'CVE-2011-4352', 'CVE-2012-2775', 'CVE-2009-2698', 'CVE-2014-8173', 'CVE-2013-3673', 'CVE-2013-3672', 'CVE-2013-3670', 'CVE-2011-1172', 'CVE-2013-3675', 'CVE-2013-3674', 'CVE-2012-6547', 'CVE-2009-0676', 'CVE-2013-6380', 'CVE-2013-6381', 'CVE-2012-6543', 'CVE-2013-6383', 'CVE-2013-4513', 'CVE-2013-4512', 'CVE-2009-4141', 'CVE-2012-4467', 'CVE-2013-4516', 'CVE-2013-4515', 'CVE-2013-1774', 'CVE-2013-2547', 'CVE-2011-1748', 'CVE-2008-4302', 'CVE-2011-1076', 'CVE-2011-1746', 'CVE-2008-4554', 'CVE-2014-3153', 'CVE-2014-9529', 'CVE-2013-2852', 'CVE-2005-3181', 'CVE-2011-1581', 'CVE-2015-3636', 'CVE-2011-1957', 'CVE-2013-1957', 'CVE-2014-5045', 'CVE-2010-3015', 'CVE-2012-1961', 'CVE-2013-0850', 'CVE-2011-2518', 'CVE-2013-4514', 'CVE-2013-4922', 'CVE-2013-4923', 'CVE-2013-4921', 'CVE-2013-4927', 'CVE-2013-4924', 'CVE-2010-5313', 'CVE-2010-4650', 'CVE-2010-4158', 'CVE-2014-0069', 'CVE-2010-4157', 'CVE-2013-2850', 'CVE-2010-2492']
    #l = ['CVE-2016-5278', 'CVE-2015-5154', 'CVE-2016-9576', 'CVE-2016-2808', 'CVE-2016-1930', 'CVE-2016-2532', 'CVE-2015-4521', 'CVE-2015-4522', 'CVE-2015-7203', 'CVE-2016-5126', 'CVE-2017-6348', 'CVE-2015-8961', 'CVE-2015-8962', 'CVE-2016-5275', 'CVE-2016-4439', 'CVE-2016-7908', 'CVE-2016-7154', 'CVE-2015-4036', 'CVE-2015-3456', 'CVE-2015-2740', 'CVE-2016-3134', 'CVE-2015-5283', 'CVE-2016-9776', 'CVE-2016-7155', 'CVE-2016-9101', 'CVE-2016-7156', 'CVE-2016-2818', 'CVE-2015-8363', 'CVE-2015-7194', 'CVE-2016-6511', 'CVE-2016-5264', 'CVE-2015-5307', 'CVE-2015-4002', 'CVE-2016-9373', 'CVE-2016-1583', 'CVE-2016-7180', 'CVE-2016-1935', 'CVE-2015-2729', 'CVE-2016-5238', 'CVE-2016-1714', 'CVE-2015-0829', 'CVE-2016-2838', 'CVE-2016-2529', 'CVE-2015-4511', 'CVE-2016-4082', 'CVE-2015-4513', 'CVE-2015-4512', 'CVE-2015-2739', 'CVE-2015-8953', 'CVE-2013-4542', 'CVE-2016-9923', 'CVE-2016-2327', 'CVE-2016-2329', 'CVE-2016-2328', 'CVE-2016-1970', 'CVE-2015-8817', 'CVE-2016-1974', 'CVE-2016-5829', 'CVE-2016-2847', 'CVE-2016-7161', 'CVE-2017-6474', 'CVE-2017-6470', 'CVE-2016-2530', 'CVE-2016-6507', 'CVE-2016-6506', 'CVE-2015-4517', 'CVE-2015-0830', 'CVE-2016-6508', 'CVE-2016-4002', 'CVE-2015-8785', 'CVE-2015-4500', 'CVE-2015-4501', 'CVE-2016-4006', 'CVE-2015-4504', 'CVE-2015-4487', 'CVE-2015-2724', 'CVE-2015-2725', 'CVE-2016-8909', 'CVE-2016-2330', 'CVE-2016-4805', 'CVE-2015-7178', 'CVE-2015-7179', 'CVE-2015-7176', 'CVE-2015-7177', 'CVE-2015-7174', 'CVE-2015-7175', 'CVE-2016-9104', 'CVE-2015-3906', 'CVE-2016-5280', 'CVE-2016-6513', 'CVE-2016-2814', 'CVE-2016-2819', 'CVE-2015-8365', 'CVE-2016-4952', 'CVE-2016-8910', 'CVE-2016-7910', 'CVE-2016-7913', 'CVE-2016-7912', 'CVE-2017-6214', 'CVE-2016-10154', 'CVE-2016-6351', 'CVE-2016-9685', 'CVE-2016-1957', 'CVE-2016-1956', 'CVE-2016-6213', 'CVE-2016-1953', 'CVE-2016-1952', 'CVE-2016-7425', 'CVE-2015-6252', 'CVE-2015-1872', 'CVE-2015-8663', 'CVE-2015-8662', 'CVE-2015-8661', 'CVE-2014-5388', 'CVE-2016-4080', 'CVE-2015-4482', 'CVE-2015-1339', 'CVE-2016-5728', 'CVE-2015-4484', 'CVE-2015-1333', 'CVE-2016-4998', 'CVE-2016-2550', 'CVE-2016-9103', 'CVE-2016-3156','CVE-2016-4952', 'CVE-2016-9923', 'CVE-2016-9685', 'CVE-2016-2329', 'CVE-2015-0829', 'CVE-2016-2838', 'CVE-2016-2529', 'CVE-2015-4511', 'CVE-2015-4513', 'CVE-2015-4512', 'CVE-2015-4517', 'CVE-2016-4082', 'CVE-2015-8953', 'CVE-2015-4511', 'CVE-2015-0829', 'CVE-2016-2838', 'CVE-2016-2529', 'CVE-2015-0824', 'CVE-2016-2837', 'CVE-2016-2836', 'CVE-2016-2523', 'CVE-2016-2522', 'CVE-2016-7179', 'CVE-2016-7177', 'CVE-2016-7176', 'CVE-2016-8658', 'CVE-2015-3209', 'CVE-2016-7170', 'CVE-2016-2824', 'CVE-2016-5106', 'CVE-2016-5107', 'CVE-2016-6833', 'CVE-2015-5366', 'CVE-2016-6835', 'CVE-2016-4454', 'CVE-2015-6526', 'CVE-2015-7220', 'CVE-2015-7221', 'CVE-2016-5276', 'CVE-2016-5277', 'CVE-2016-5274', 'CVE-2015-4651', 'CVE-2017-5547', 'CVE-2016-9793', 'CVE-2015-7180', 'CVE-2016-3955', 'CVE-2014-0182', 'CVE-2015-3810', 'CVE-2016-4453', 'CVE-2015-4493', 'CVE-2016-6828', 'CVE-2015-2710', 'CVE-2015-7217', 'CVE-2016-7094', 'CVE-2016-4441', 'CVE-2015-5156', 'CVE-2015-4473', 'CVE-2016-4079', 'CVE-2015-5364', 'CVE-2015-6820', 'CVE-2015-3815', 'CVE-2015-7198', 'CVE-2015-7199', 'CVE-2015-5158', 'CVE-2017-6353', 'CVE-2016-9376', 'CVE-2015-2712', 'CVE-2016-4568', 'CVE-2015-2716', 'CVE-2016-5258', 'CVE-2016-5259', 'CVE-2015-7512', 'CVE-2015-8554', 'CVE-2015-7201', 'CVE-2015-7202', 'CVE-2016-5254', 'CVE-2016-5255', 'CVE-2016-5256', 'CVE-2016-5257', 'CVE-2016-2213', 'CVE-2017-5548', 'CVE-2016-0718', 'CVE-2016-7042', 'CVE-2015-0827', 'CVE-2015-0826', 'CVE-2016-4568', 'CVE-2015-2716', 'CVE-2016-7466', 'CVE-2016-8666', 'CVE-2015-8743', 'CVE-2016-3062', 'CVE-2015-3214', 'CVE-2016-5258', 'CVE-2016-5259', 'CVE-2015-7512', 'CVE-2015-8554', 'CVE-2015-7201', 'CVE-2015-7202', 'CVE-2016-5254', 'CVE-2016-5255', 'CVE-2016-5256', 'CVE-2016-5257', 'CVE-2016-2213', 'CVE-2017-5548', 'CVE-2016-0718', 'CVE-2016-1981', 'CVE-2015-2726', 'CVE-2016-5400', 'CVE-2016-5403', 'CVE-2016-2857', 'CVE-2015-1779', 'CVE-2016-7042', 'CVE-2015-0827', 'CVE-2015-0826', 'CVE-2016-4568', 'CVE-2015-2716', 'CVE-2016-7466', 'CVE-2016-8666', 'CVE-2015-8743', 'CVE-2016-1977', 'CVE-2016-3062', 'CVE-2015-3214', 'CVE-2015-0824', 'CVE-2016-2837', 'CVE-2016-2836', 'CVE-2016-2523', 'CVE-2016-2522', 'CVE-2016-7179', 'CVE-2016-7177', 'CVE-2016-7176', 'CVE-2016-8658', 'CVE-2015-3209', 'CVE-2016-7170']
    #print len(list(set(l)))
    #exit()
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
    store_filepath = "C/test_data/4/arraysuse_slices.txt"
    f = open("arrayuse_slice_points.pkl", 'rb')
    dict_unsliced_pointers = pickle.load(f)
    f.close()
    #l = ['CVE-2010-2068', 'CVE-2015-1158', 'CVE-2006-1530', 'CVE-2012-2802', 'CVE-2010-4165', 'CVE-2014-3523', 'CVE-2012-6062', 'CVE-2013-1672', 'CVE-2007-4997', 'CVE-2013-4082', 'CVE-2012-4186', 'CVE-2013-4512', 'CVE-2013-6450', 'CVE-2011-2534', 'CVE-2014-1690', 'CVE-2011-2536', 'CVE-2012-2319', 'CVE-2012-0957', 'CVE-2011-3936', 'CVE-2004-1151', 'CVE-2013-4929', 'CVE-2010-3296', 'CVE-2011-4102', 'CVE-2012-5668', 'CVE-2011-4100', 'CVE-2011-1959', 'CVE-2012-3969', 'CVE-2012-1183', 'CVE-2011-0726', 'CVE-2013-0756', 'CVE-2004-0535', 'CVE-2010-2495', 'CVE-2012-2393', 'CVE-2015-3811', 'CVE-2012-2776', 'CVE-2009-2909', 'CVE-2014-3633', 'CVE-2014-1508', 'CVE-2011-2529', 'CVE-2014-3537', 'CVE-2012-1947', 'CVE-2013-0844', 'CVE-2012-1942', 'CVE-2014-0195', 'CVE-2012-4293', 'CVE-2012-4292', 'CVE-2008-1390', 'CVE-2011-0021', 'CVE-2012-3991', 'CVE-2007-4521', 'CVE-2009-0746', 'CVE-2011-1147', 'CVE-2012-5240', 'CVE-2013-2634', 'CVE-2014-8133', 'CVE-2006-2778', 'CVE-2012-4288', 'CVE-2015-0253', 'CVE-2012-0444', 'CVE-2013-1726', 'CVE-2013-7112', 'CVE-2006-1856', 'CVE-2013-0850', 'CVE-2011-3623', 'CVE-2013-1582', 'CVE-2013-1732', 'CVE-2014-8884', 'CVE-2013-0772', 'CVE-2014-9374', 'CVE-2014-1497', 'CVE-2014-0221', 'CVE-2013-1696', 'CVE-2011-1833', 'CVE-2013-1693', 'CVE-2013-0872', 'CVE-2012-2790', 'CVE-2012-2791', 'CVE-2012-2796', 'CVE-2012-0477', 'CVE-2012-2652', 'CVE-2006-4790', 'CVE-2013-0867', 'CVE-2013-4932', 'CVE-2013-0860', 'CVE-2014-3511', 'CVE-2014-3510', 'CVE-2013-0868', 'CVE-2014-8541', 'CVE-2014-2739', 'CVE-2014-9319', 'CVE-2006-4813', 'CVE-2014-8544', 'CVE-2011-3973', 'CVE-2013-1848', 'CVE-2014-9316', 'CVE-2012-1594', 'CVE-2013-1573', 'CVE-2012-0068', 'CVE-2015-0833', 'CVE-2010-1748', 'CVE-2012-0067', 'CVE-2011-3362', 'CVE-2014-3182', 'CVE-2013-5641', 'CVE-2013-5642', 'CVE-2011-3484', 'CVE-2013-6891', 'CVE-2014-8712', 'CVE-2014-8713', 'CVE-2014-8714', 'CVE-2013-4534', 'CVE-2010-2431', 'CVE-2014-8412', 'CVE-2011-1175', 'CVE-2012-5237', 'CVE-2011-1173', 'CVE-2012-5238', 'CVE-2014-4611', 'CVE-2015-0564', 'CVE-2014-5271', 'CVE-2011-0055', 'CVE-2014-3470', 'CVE-2014-8643', 'CVE-2015-0204', 'CVE-2014-2286', 'CVE-2012-6537', 'CVE-2011-3945', 'CVE-2011-3944', 'CVE-2011-2896', 'CVE-2010-2955', 'CVE-2013-2495', 'CVE-2013-4931', 'CVE-2013-4933', 'CVE-2012-2775', 'CVE-2013-4934', 'CVE-2013-4936', 'CVE-2011-4594', 'CVE-2014-6424', 'CVE-2013-0311', 'CVE-2011-4598', 'CVE-2006-2935', 'CVE-2011-4352', 'CVE-2012-1184', 'CVE-2005-3356', 'CVE-2012-6059', 'CVE-2012-6058', 'CVE-2011-3950', 'CVE-2014-9672', 'CVE-2010-2803', 'CVE-2013-7011', 'CVE-2013-3674', 'CVE-2009-0676', 'CVE-2013-6380', 'CVE-2009-2768', 'CVE-2015-3008', 'CVE-2013-0796', 'CVE-2009-2484', 'CVE-2013-4264', 'CVE-2013-4928', 'CVE-2014-8542', 'CVE-2012-6540', 'CVE-2015-0228', 'CVE-2013-7008', 'CVE-2013-7009']
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
    store_filepath = "C/test_data/4/integeroverflow_slices.txt"
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
