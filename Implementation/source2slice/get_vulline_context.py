#-*- coding:utf-8 -*-
'''
#该文件对源程序标记漏洞行，根据diff文件中的@@行找到@@段的起始行，如果该@@段中有减号行，那么取出减号行在源程序中
的行号，即为漏洞行号.
'''
import os
import pickle

def get_vulline_context(code_path,diff_path):
    vulline_dict = {} #记录源程序中的漏洞行行号
    patchline_dict = {}
    _dict_vul_code = {} #存储从diff文件中提取出来的减号行，字典结构{filepath:{减号行行号：{减号行代码}}}
    _dict_patch_code = {} #存储从diff文件中提取出来的加号行，字典结构{filepath:{加号行行号：{加号行代码}}}
    for folder_1 in os.listdir(code_path):
        for folder_2 in os.listdir(os.path.join(code_path,folder_1)):
            for folder_3 in os.listdir(os.path.join(code_path,folder_1,folder_2)):
                for filename in os.listdir(os.path.join(code_path,folder_1,folder_2,folder_3)):
                    filepath = os.path.join(code_path,folder_1,folder_2,folder_3,filename)
                    
                    difffolder = os.path.join(diff_path,folder_1,folder_2,folder_3)
                    for filename2 in os.listdir(difffolder):
                        diffpath = os.path.join(difffolder,filename2)
                        f2 = open(diffpath,'r')
                        sens = f2.read().split('\n')
                        f2.close()
                    #print(diffpath)
                    if filepath not in _dict_vul_code.keys():
                        _dict_vul_code[filepath] = {}
                    if filepath not in _dict_patch_code.keys():
                        _dict_patch_code[filepath] = {}
                    
                    index = -1
                    index_start = []
                    for sen in sens:
                        #print(sen)
                        index += 1
                        if sen.startswith('@@ ') is True: #记录diff文件中的@@行
                            index_start.append(index)
                    for i in range(0,len(index_start)):
                        if i < len(index_start)-1:
                            diff_sens = sens[index_start[i]:index_start[i+1]] ##该段@@段在diff文件中的行
                        else:
                            diff_sens = sens[index_start[i]:]
                        startline = diff_sens[0]
                        vul_linenum = int(startline.split('-')[1].split(',')[0]) ##@@段在漏洞文件中的起始行
                        patch_linenum = int(startline.split('+')[1].split(',')[0]) ##@@段在修补文件中的起始行
                        diff_sens = diff_sens[1:] ##diff段代码
                        index = -1
                        for sen in diff_sens:
                            if sen.startswith('-') is True and sen.startswith('---') is False: #减号行 
                                index += 1
                                linenum = index + vul_linenum 
                                _dict_vul_code[filepath][linenum] = sen.strip('-').strip()
                            elif sen.startswith('+') is True and sen.startswith('+++') is False: #加号行
                                linenum = index + patch_linenum 
                                _dict_patch_code[filepath][linenum] = sen.strip('+').strip()
                            else:
                                index += 1
            
                    #print(_dict_vul_code)
                    #读取源程序，在源程序中匹配漏洞行和修补行            
                    if code_path.find('Old') != -1: #匹配减号行dict
                        with open(filepath,'r') as f1:
                            sentences = f1.read().split('\n')
                        f1.close()
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

    print(vulline_dict)            
    with open('./vul_context_linux_kernel.pkl','wb') as f:
        pickle.dump(vulline_dict,f)
    f.close()

if __name__ == '__main__':

    code_path = './source/data_source/linux_kernel/'  #源程序
    diff_path = './source/diff_source/linux_kernel/'  #diff文件

    get_vulline_context(code_path,diff_path)
                
                    
                    
                    
