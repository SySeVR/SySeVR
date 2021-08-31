## coding:utf-8
import os
import pickle

def make_label(path, _dict):
    print(path)
    f = open(path, 'r')
    slicelists = f.read().split('------------------------------')[:-1]
    f.close()
    
    labels = []
    if slicelists[0] == '':
        del slicelists[0]
    if slicelists[-1] == '' or slicelists[-1] == '\n' or slicelists[-1] == '\r\n':
        del slicelists[-1]
    
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
            
        slicename = sentences[0].split(' ')[1].split('/')[-4] + sentences[0].split(' ')[1].split('/')[-3] + sentences[0].split(' ')[1].split('/')[-2] + '/' + sentences[0].split(' ')[1].split('/')[-1]
        sentences = sentences[1:]
        
        label = 0
        
        if slicename not in _dict.keys():
	    labels.append(label)
            continue
        else:
            vulline_nums = _dict[slicename]
            for sentence in sentences:
                if (is_number(sentence.split(' ')[-1])) is False:
					continue
                linenum = int(sentence.split(' ')[-1])
                if linenum not in vulline_nums:
                    continue
                else:
                    label = 1
                    break
        labels.append(label)
    
    return labels
       
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
       
def main():
    f = open("./contain_all.txt", 'r')
    vullines = f.read().split('\n')
    f.close()

    _dict = {}
    for vulline in vullines:
        key = vulline.split(' ')[0].split('/')[-4] + vulline.split(' ')[0].split('/')[-3] + vulline.split(' ')[0].split('/')[-2] + '/' + vulline.split(' ')[0].split('/')[-1]
        linenum = int(vulline.split(' ')[-1])
        if key not in _dict.keys():
            _dict[key] = [linenum]
        else:
            _dict[key].append(linenum)

    lang = './C/test_data/data_source_add/sard/'
    
    path = os.path.join(lang, 'api_slices.txt')
    list_all_apilabel = make_label(path, _dict)
    dec_path = os.path.join(lang, 'api_slices_label.pkl')
    f = open(dec_path, 'wb')
    pickle.dump(list_all_apilabel, f, True)
    f.close()
    
    path = os.path.join(lang, 'array_slices.txt')
    list_all_arraylabel = make_label(path, _dict)
    dec_path = os.path.join(lang, 'array_slices_label.pkl')
    f = open(dec_path, 'wb')
    pickle.dump(list_all_arraylabel, f, True)
    f.close()
    
    path = os.path.join(lang, 'pointer_slices.txt')
    list_all_pointerlabel = make_label(path, _dict)
    dec_path = os.path.join(lang, 'pointer_slices_label.pkl')
    f = open(dec_path, 'wb')
    pickle.dump(list_all_pointerlabel, f, True)
    f.close()
 
    path = os.path.join(lang, 'expr_slices.txt')
    list_all_exprlabel = make_label(path, _dict)
    dec_path = os.path.join(lang, 'expr_slices_label.pkl')
    f = open(dec_path, 'wb')
    pickle.dump(list_all_exprlabel, f, True)
    f.close()
    

if __name__ == '__main__':
    main()
