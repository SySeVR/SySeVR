import pickle

list_delete = []
def dodelete(dict1, dict2):
    list_key1 = []
    list_key2 = []
    for k1 in dict1.keys():
        list_key1.append(k1)
    print(list_key1)
    for k2 in dict2.keys():
        list_key2.append(k2)
    print(list_key2)
    for k in list_key2:
        print(k)
        for x in range(0,len(dict2[k])):
            for dx in range(list_key2.index(k), 1):
                if dx == list_key2.index(k):
                    for y in range(x,len(dict2[k])):
                        if dict2[k][x] ==dict2[k][y] :
                            if x!= y:
                                p="api_slices_label"+k[-1]
                                if dict1[p][x]==dict1[p][y]:
                                    unit = k + "$" + str(x)
                                    list_delete.append(unit)
                                    print("delete")
                                else:
                                    unit1 = k + "$" + str(x)
                                    list_delete.append(unit1)
                                    unit2 = k + "$" + str(y)
                                    list_delete.append(unit2)
                                    print("delete")
                else:
                    for y in range(0,len(dict2[list_key2[dx]])):
                        if dict2[k][x] == dict2[list_key2[dx]][y]:
                            p1="api_slices_label"+k[-1]
                            p2="api_slices_label"+list_key2[dx][-1]
                            if dict1[p1][x]==dict1[p2][y]:
                                unit=k+"$"+str(x)
                                list_delete.append(unit)
                                print("delete")
                            else:
                                unit1 = k + "$" + str(x)
                                list_delete.append(unit1)
                                unit2 = list_key2[dx] + "$" + str(y)
                                list_delete.append(unit2)
                                print("delete")
    print(list_delete)
    print("done")
    
def test():
    dict1 = {}
    dict2 = {}

    f1 = open("./label_source/pointer_slices_label.pkl",'rb')
    f2 = open("./hash_slices/pointer_slices.pkl",'rb')
    dict1['api_slices_label'] = pickle.load(f1)
    dict2['api_slices'] = pickle.load(f2)
    print("load")
    dodelete(dict1,dict2)


if __name__ == '__main__':
    test()
    f = open("./dedoule_list/pointer_delete.pkl", "wb")
    list3 = list(set(list_delete))
    print("saving")
    pickle.dump(list3,f)
