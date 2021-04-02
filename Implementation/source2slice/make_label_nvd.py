# -*- coding:utf-8 -*-
import pickle
import re
import os

def make_label(data_path,label_path,_dict):	

	for filename in os.listdir(data_path):
		filepath = os.path.join(data_path,filename)
		_labels = {}
		f = open(filepath,'r')
		slicelists = f.read().split('------------------------------')
		f.close()

		labelpath = os.path.join(label_path,filename[:-4]+'_label.pkl')	

		if slicelists[0] == '':
			del slicelists[0]
		if slicelists[-1] == '' or slicelists[-1] == '\n' or slicelists[-1] == '\r\n':
			del slicelists[-1]
    
		for slice in slicelists:
			sentences = slice.split('\n')
			if sentences[0] == '\r' or sentences[0] == '':
				del sentences[0]
			if sentences == []:
				continue
			if sentences[-1] == '':
				del sentences[-1]
			if sentences[-1] == '\r':
				del sentences[-1]
        
			slicename = sentences[0]
			label = 0
			key = slicename.split('/')[6]+'/'+slicename.split('/')[7]+'/'+slicename.split('/')[8]+'/'+slicename.split('/')[-1].split(' ')[0] #源程序的key
			if key not in _dict.keys():
				_labels[slicename] = 0
				continue
			if len(_dict[key]) == 0:
				_labels[slicename] = 0
				continue
			sentences = sentences[1:]
			for sentence in sentences:
				if (is_number(sentence.split(' ')[-1])) is False:
					continue
				linenum = int(sentence.split(' ')[-1])  
				vullines = _dict[key]
				if linenum in vullines:
					label = 1
					_labels[slicename] = 1
					break 
			if label == 0:
				_labels[slicename] = 0	
	
		with open(labelpath,'wb') as f1:
			pickle.dump(_labels,f1)
		f1.close()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False	
	
if __name__ == '__main__':

	with open('./vul_context_linux_kernel.pkl','rb') as f:
		_dict = pickle.load(f)
	f.close()
	#print(_dict)

	code_path = './source/data_source/linux_kernel/' 
	label_path = './C/label_source/linux_kernel/' 
	
	make_label(code_path,label_path,_dict)	
