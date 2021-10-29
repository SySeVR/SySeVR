## coding:utf-8
'''
##该程序用于处理sysevr源程序文件及获取nvd漏洞行
'''

import pickle
import os
import shutil
import re

##处理sard源程序文件格式
def dealfile_sard(folder_path):
    data_source = './newfile/SARD/'
    for folder in os.listdir(folder_path):
        #print(folder)
        length = len(folder)
        #print(length)
        new_folder = (9 - length)*'0' + folder
        testcase_1 = new_folder[:3]
        testcase_2 = new_folder[3:6]
        testcase_3 = new_folder[6:]
        if testcase_1 not in os.listdir(data_source):
            os.mkdir(os.path.join(data_source,testcase_1))
        if testcase_2 not in os.listdir(os.path.join(data_source,testcase_1)):
            os.mkdir(os.path.join(data_source,testcase_1,testcase_2))
        if testcase_3 not in os.listdir(os.path.join(data_source,testcase_1,testcase_2)):
            os.mkdir(os.path.join(data_source,testcase_1,testcase_2,testcase_3))
        for filename in os.listdir(os.path.join(folder_path,folder)):
            shutil.copyfile(os.path.join(folder_path,folder,filename),os.path.join(data_source,testcase_1,testcase_2,testcase_3,filename))
    print('success!\n')

##处理nvd的函数文件，记录漏洞行    
def dealfunc_nvd(folder_path,diff_path):
    vulline_dict = {} #记录源程序中的漏洞行行号
    for filename in os.listdir(folder_path):
        if 'PATCHED' in filename:
            continue
        pattern = re.compile(r"(?P<cve_id>CVE[-_][0-9]*[-_][0-9]*)[-_]")
        match = re.search(pattern, filename)
        cve_id = "-".join(match.group("cve_id").split("_"))
        filepath = os.path.join(folder_path,filename)
        f = open(filepath,'r')
        sentences = f.read().split('\n')
        f.close()
        diffpath = os.path.join(diff_path,cve_id,(cve_id + '.txt'))
        f = open(diffpath,'r')
        diffsens = f.read().split('\n')
        f.close()
            
        vul_code = []
        index = -1
        index_start= []
        for sen in diffsens:
            index += 1
            if sen.startswith('@@ ') is True: #记录diff文件中的@@行
                index_start.append(index)  ##记录@@段在diff文件中的行号
        for i in range(0,len(index_start)):  ##当前@@段
            if i < len(index_start)-1: 
                diff_sens = diffsens[index_start[i]:index_start[i+1]] ##该段@@段在diff文件中的行
            else:  #最后一个@@段
                diff_sens = diffsens[index_start[i]:]
            startline = diff_sens[0]
            diff_sens = diff_sens[1:] ##diff段代码
            index = -1
            for sen in diff_sens:
                index += 1
                if sen.startswith('-') is True and sen.startswith('---') is False: #减号行 
                    if sen.strip('-').strip() == '' or sen.strip('-').strip()==',' or sen.strip('-').strip() == ';' or sen.strip('-').strip() == '{' or sen.strip('-').strip() == '}':
                        continue
                    vul_code.append(sen.strip('-').strip())

        for i in range(0,len(sentences)):
            if sentences[i].strip() not in vul_code:
                continue
            else:
                linenum = i + 1
                if filepath not in vulline_dict.keys():
                    vulline_dict[filepath] = [linenum]
                else:
                    vulline_dict[filepath].append(linenum)
    with open('./vul_context_func.pkl','wb') as f:
        pickle.dump(vulline_dict,f)
    f.close()

##记录nvd的C文件，记录漏洞行
def dealfile_nvd(folder_path,diff_path):
    for folder in os.listdir(folder_path):
        vulline_dict = {}
        _dict_vul_code = {} #存储从diff文件中提取出来的减号行，字典结构{filepath:{减号行行号：{减号行代码}}}
        for filename in os.listdir(os.path.join(folder_path,folder)):
            print(filename)
            filepath = os.path.join(folder_path,folder,filename)
            if 'linux' in folder:
                cve_id = ('-').join(filename.split('_')[3:6])
            elif 'xen' in folder or 'qemu' in folder:
                cve_id = filename.split('_')[2]
            else:
                cve_id = ('-').join(filename.split('_')[2:5])
            
            diffpath = os.path.join(diff_path,cve_id +'.txt')
            f = open(diffpath,'r')
            diffsens = f.read().split('\n')
            f.close()
            if filepath not in _dict_vul_code.keys():
                _dict_vul_code[filepath] = {}
            
            index = -1
            index_start = []
            for sen in diffsens:
                index += 1
                if sen.startswith('@@') is True: #记录diff文件中的@@行
                    index_start.append(index)
                    
            for i in range(0,len(index_start)):
                if i < len(index_start)-1:
                    diff_sens = diffsens[index_start[i]:index_start[i+1]] ##该段@@段在diff文件中的行
                else:
                    diff_sens = diffsens[index_start[i]:]
                startline = diff_sens[0]
                vul_linenum = int(startline.split('-')[1].split(',')[0]) ##@@段在漏洞文件中的起始行
                diff_sens = diff_sens[1:] ##diff段代码
                index = -1
                for sen in diff_sens:
                    index += 1
                    if sen.startswith('-') is True and sen.startswith('---') is False: #减号行 
                        if sen.strip('-').strip() == '' or sen.strip('-').strip()==',' or sen.strip('-').strip() == ';' or sen.strip('-').strip() == '{' or sen.strip('-').strip() == '}':
                            continue
                        linenum = index + vul_linenum 
                        _dict_vul_code[filepath][linenum] = sen.strip('-').strip()  
                        
            #读取源程序，在源程序中匹配漏洞行
            with open(filepath,'r') as f:
                sentences = f.read().split('\n')
            f.close()
            if filepath in _dict_vul_code.keys():
                print(filepath)
                for line in _dict_vul_code[filepath].keys():
                    print(line)
                    if line > len(sentences):
                        continue
                    vul_sen = sentences[line-1].strip()
                    if vul_sen != _dict_vul_code[filepath][line] : #匹配代码行
                        continue
                    else:
                        if filepath not in vulline_dict.keys():
                            vulline_dict[filepath] = [line]
                        else:
                            vulline_dict[filepath].append(line)
                            
        with open('./vul_context_' + folder + '.pkl','wb') as f:
            pickle.dump(vulline_dict,f)
        f.close()
                
                                
if __name__ == "__main__":

    data_path = './SARD/SARD/'
    #dealfile_sard(data_path)
    
    data_source1 = './NVD/func_code/'
    diff_path = './NVD/diff/'
    #dealfunc_nvd(data_source1,diff_path)
    
    data_source2 = './NVD/source_code/'
    dealfile_nvd(data_source2,diff_path)
