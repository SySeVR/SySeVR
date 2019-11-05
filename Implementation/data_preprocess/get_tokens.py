# -*- coding:utf-8 -*-

import re
import os
import string
import xlrd


def isphor(s, liter):
    m = re.search(liter,s)
    if m is not None:
        return True
    else: 
        return False

    
def doubisphor(forward, back):
    double = ('->','--','-=','+=','++','>=','<=','==','!=','*=','/=','%=','/=','&=','^=','||','&&','>>','<<')
    string=forward+back
    
    if string in double:
        return True
    else:  
        return False

    
def trisphor(s,t):
    if (s=='>>')|(s=='<<')and(t=='='):
        return True
    else:
        return False
    

def create_tokens(sentence):
    formal='^[_a-zA-Z][_a-zA-Z0-9]*$'
    phla='[^_a-zA-Z0-9]'
    space='\s'
    spa=''
    string=[]
    j=0
    str = sentence
    i=0
    
    while(i<len(str)):
        if isphor(str[i],space):
            if i>j:
                string.append(str[j:i])
                j=i+1
            else:
                j=i+1
                
        elif isphor(str[i],phla):    
            if (i+1<len(str))and isphor(str[i+1],phla):
                m=doubisphor(str[i],str[i+1])
                
                if m:
                    string1=str[i]+str[i+1]
                    
                    if (i+2<len(str))and (isphor(str[i+2],phla)):
                        if trisphor(string1,str[i+2]):
                            string.append(str[j:i])
                            string.append(str[i]+str[i+1]+str[i+2])
                            j=i+3
                            i=i+2
                            
                        else:
                            string.append(str[j:i])
                            string.append(str[i]+str[i+1])
                            string.append(str[i+2])
                            j=i+3
                            i=i+2
                            
                    else:
                        string.append(str[j:i])
                        string.append(str[i]+str[i+1])
                        j=i+2
                        i=i+1
                        
                else:
                    string.append(str[j:i])
                    string.append(str[i])
                    string.append(str[i+1])
                    j=i+2
                    i=i+1
                    
            else:
                string.append(str[j:i])
                string.append(str[i])
                j=i+1
                
        i=i+1
        
    count=0
    count1=0
    sub0='\r'
    
    if sub0 in string:
        string.remove('\r')
        
    for sub1 in string:
        if sub1==' ':
            count1=count1+1
            
    for j in range(count1):
        string.remove(' ')
        
    for sub in string:
        if sub==spa:
            count=count+1
            
    for i in range(count):
        string.remove('')
        
    return string
