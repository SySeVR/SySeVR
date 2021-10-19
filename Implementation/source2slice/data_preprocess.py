## coding:utf-8

import pickle
import os

slice_path = './slices/'
label_path = './label_source/'
folder_path = './slice_label/'
for filename in os.listdir(slice_path):
    if filename.endswith('.txt') is False:
        continue
    print(filename)
    filepath = os.path.join(slice_path,filename)
    f = open(filepath,'r')
    slicelists = f.read().split('------------------------------')
    f.close()
    labelpath = os.path.join(label_path,filename[:-4]+'.pkl')
    f = open(labelpath,'rb')
    labellists = pickle.load(f)
    f.close()
	
    if slicelists[0] == '':
        del slicelists[0]
    if slicelists[-1] == '' or slicelists[-1] == '\n' or slicelists[-1] == '\r\n':
        del slicelists[-1]

    file_path = os.path.join(folder_path,filename)
    f = open(file_path,'a+')
    for slicelist in slicelists:
        sentences = slicelist.split('\n')
        if sentences[0] == '\r' or sentences[0] == '':
            del sentences[0]
        if sentences == []:
            continue
        if sentences[-1] == '':
            del sentences[-1]
        if sentences[-1] == '\r':
            del sentences[-1]
        key = sentences[0]
	label = labellists[key]
        for sentence in sentences:
            f.write(str(sentence)+'\n')
        f.write(str(label)+'\n')
        f.write('------------------------------'+'\n')
    f.close()
print('\success!')
        
            
    
    
