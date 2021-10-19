## coding: utf-8
'''
This file is used to get the hash of slices
'''
import os
import pickle

def get_hashs(slicepath, hashpath):
    """

    # Arguments
        slicepath: String type, the src of slice files		
        hashpath: String type, the src to save hash        

    # Return
        None
    """

    for filename in os.listdir(slicepath):
        if(filename.endswith(".txt") is False):
            continue
        
        print("\n", filename)
        datalist=[]

        filepath = os.path.join(slicepath, filename)
        f1 = open(filepath, 'r')
        slicelists = f1.read().split("------------------------------")
        f1.close()

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

            sentences = sentences[1:]
            new_sens = []
            for sentence in sentences:
                if (is_number(sentence.split(' ')[-1])) is False:
                    continue
                else:
                    sentence = ' '.join(sentence.split(' ')[:-1]) 
                    new_sens.append(sentence)
            
            slicelist = " ".join(new_sens)
            #print(slicelist)
            data = hash(slicelist)
            datalist.append(data)
        f = open(os.path.join(hashpath,(filename[:-4]+".pkl")),'wb')
        pickle.dump(datalist, f)
        f.close()

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
    
    SLICEPATH = './data_source/'
    HASHPATH = './data_source/hash_slices/'

    sentenceDict = get_hashs(SLICEPATH, HASHPATH)

    print('\nsuccess!')
