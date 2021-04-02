#-*- coding:utf-8 -*-
'''
This python file is used to get the linenums of vullines in source code file.
'''
import os
import pickle

def get_vulline_context(code_path,diff_path):
    vulline_dict = {}
    patchline_dict = {}
    _dict_vul_code = {} 
    _dict_patch_code = {} 
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
                        if sen.startswith('@@ ') is True:
                            index_start.append(index)
                    for i in range(0,len(index_start)):
                        if i < len(index_start)-1:
                            diff_sens = sens[index_start[i]:index_start[i+1]] 
                        else:
                            diff_sens = sens[index_start[i]:]
                        startline = diff_sens[0]
                        vul_linenum = int(startline.split('-')[1].split(',')[0])
                        patch_linenum = int(startline.split('+')[1].split(',')[0])
                        diff_sens = diff_sens[1:] 
                        index = -1
                        for sen in diff_sens:
                            if sen.startswith('-') is True and sen.startswith('---') is False: 
                                index += 1
                                linenum = index + vul_linenum 
                                _dict_vul_code[filepath][linenum] = sen.strip('-').strip()
                            elif sen.startswith('+') is True and sen.startswith('+++') is False: 
                                linenum = index + patch_linenum 
                                _dict_patch_code[filepath][linenum] = sen.strip('+').strip()
                            else:
                                index += 1
        
                    if code_path.find('Old') != -1: 
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
                                if vul_sen != _dict_vul_code[filepath][line] : 
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

    code_path = './source/data_source/linux_kernel/' 
    diff_path = './source/diff_source/linux_kernel/' 

    get_vulline_context(code_path,diff_path)
                
                    
                    
                    
