# -*- coding: utf-8 -*-
import re
import copy
import os
import string
import xlrd
from get_tokens import *
import pickle


keywords_0 = ('auto', 'typedf', 'const', 'extern', 'register', 'static', 'volatile', 'continue', 'break',
              'default', 'return', 'goto', 'else', 'case')

keywords_1 = ('catch', 'sizeof', 'if', 'switch', 'while', 'for')

keywords_2 = ('memcpy', 'wmemcpy', '_memccpy', 'memmove', 'wmemmove', 'memset', 'wmemset', 'memcmp', 'wmemcmp', 'memchr',
              'wmemchr', 'strncpy', 'lstrcpyn', 'wcsncpy', 'strncat', 'bcopy', 'cin', 'strcpy', 'lstrcpy', 'wcscpy', '_tcscpy',
              '_mbscpy', 'CopyMemory', 'strcat', 'lstrcat', 'fgets', 'main', '_main', '_tmain', 'Winmain', 'AfxWinMain', 'getchar',
              'getc', 'getch', 'getche', 'kbhit', 'stdin', 'm_lpCmdLine', 'getdlgtext', 'getpass', 'istream.get', 'istream.getline',
              'istream.peek', 'istream.putback', 'streambuf.sbumpc', 'streambuf.sgetc', 'streambuf.sgetn', 'streambuf.snextc', 'streambuf.sputbackc',
              'SendMessage', 'SendMessageCallback', 'SendNotifyMessage', 'PostMessage', 'PostThreadMessage', 'recv', 'recvfrom', 'Receive',
              'ReceiveFrom', 'ReceiveFromEx', 'CEdit.GetLine', 'CHtmlEditCtrl.GetDHtmlDocument', 'CListBox.GetText', 'CListCtrl.GetItemText',
              'CRichEditCtrl.GetLine', 'GetDlgItemText', 'CCheckListBox.GetCheck', 'DISP_FUNCTION', 'DISP_PROPERTY_EX', 'getenv', 'getenv_s', '_wgetenv',
              '_wgetenv_s', 'snprintf', 'vsnprintf', 'scanf', 'sscanf', 'catgets', 'gets', 'fscanf', 'vscanf', 'vfscanf', 'printf', 'vprintf', 'CString.Format',
              'CString.FormatV', 'CString.FormatMessage', 'CStringT.Format', 'CStringT.FormatV', 'CStringT.FormatMessage', 'CStringT.FormatMessageV',
              'vsprintf', 'asprintf', 'vasprintf', 'fprintf', 'sprintf', 'syslog', 'swscanf', 'sscanf_s', 'swscanf_s', 'swprintf', 'malloc',
              'readlink', 'lstrlen', 'strchr', 'strcmp', 'strcoll', 'strcspn', 'strerror', 'strlen', 'strpbrk', 'strrchr', 'strspn', 'strstr',
              'strtok', 'strxfrm', 'kfree', '_alloca')

keywords_3 = ('_strncpy*', '_tcsncpy*', '_mbsnbcpy*', '_wcsncpy*', '_strncat*', '_mbsncat*', 'wcsncat*', 'CEdit.Get*', 'CRichEditCtrl.Get*',
              'CComboBox.Get*', 'GetWindowText*', 'istream.read*', 'Socket.Receive*', 'DDX_*', '_snprintf*', '_snwprintf*')

keywords_5 = ('*malloc',)


xread = xlrd.open_workbook('function.xls')
keywords_4 = []
for sheet in xread.sheets():
    col = sheet.col_values(0)[1:]
    keywords_4 += col

typewords_0 = ('short', 'int', 'long', 'float', 'doubule', 'char', 'unsigned', 'signed', 'void' ,'wchar_t', 'size_t', 'bool')
typewords_1 = ('struct', 'union', 'enum')
typewords_2 = ('new', 'delete')
operators = ('+', '-', '*', '/', '=', '%', '?', ':', '!=', '==', '<<', '&&', '||', '+=', '-=', '++', '--', '>>', '|=')
function = '^[_a-zA-Z][_a-zA-Z0-9]*$'
variable = '^[_a-zA-Z][_a-zA-Z0-9(->)?(\.)?]*$'
number = '[0-9]+'
stringConst = '(^\'[\s|\S]*\'$)|(^"[\s|\S]*"$)'
constValue = ['NULL', 'false', 'true']
phla = '[^a-zA-Z0-9_]'
space = '\s'
spa = ''
def isinKeyword_3(token):
    for key in keywords_3:
        if len(token) < len(key)-1:
            return False
        if key[:-1] == token[:len(key)-1]:
            return True
        else:
            return False
def isinKeyword_5(token):
    for key in keywords_5:
        if len(token) < len(key)-1:
            return False
        if token.find(key[1:]) != -1:
            return True
        else:
            return False
def isphor(s, liter):
    m = re.search(liter, s)
    if m is not None:
        return True
    else:
        return False
def var(s):
    m = re.match(function, s)
    if m is not None:
        return True
    else:
        return False
def CreateVariable(string, token):
    length = len(string)
    stack1 = []
    s = ''
    i = 0
    while (i < length):
        if var(string[i]): 
            while stack1 != []:
                s = stack1.pop() + s
            s = s + string[i]
            token.append(s)
            s = ''
            i = i + 1
        else:
            token.append(string[i])
            i = i + 1

def mapping(list_sentence):
    list_code = []
    for code in list_sentence:
        _string = ''
        for c in code:
            _string = _string + ' ' + c
        _string = _string[1:]
        list_code.append(_string)   
    _func_dict = {}
    _variable_dict = {}
    index = 0
    while index < len(list_code):
        string = []
        token = []
        j = 0
        str1 = copy.copy(list_code[index])
        i = 0
        tag = 0
        strtemp = ''
        while i < len(str1):
            if tag == 0:
                if isphor(str1[i], space): 
                    if i > 0:
                        string.append(str1[j:i])
                        j = i + 1

                    else:
                        j = i + 1
                    i = i + 1

                elif i + 1 == len(str1):
                    string.append(str1[j:i + 1])
                    break

                elif isphor(str1[i], phla): 
                    if i + 1 < len(str1) and str1[i] == '-' and str1[i + 1] == '>':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '<' and str1[i + 1] == '<':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '>' and str1[i + 1] == '>':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '&' and str1[i + 1] == '&':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '|' and str1[i + 1] == '|':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '|' and str1[i + 1] == '=':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '=' and str1[i + 1] == '=':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '!' and str1[i + 1] == '=':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '+' and str1[i + 1] == '+':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '-' and str1[i + 1] == '-':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2

                    elif i + 1 < len(str1) and str1[i] == '+' and str1[i + 1] == '=':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2
                    elif i + 1 < len(str1) and str1[i] == '-' and str1[i + 1] == '=':
                        string.append(str1[i] + str1[i + 1])
                        j = i + 2
                        i = i + 2
                    elif str1[i] == '"':
                        strtemp = strtemp + str1[i]
                        i = i + 1
                        tag = 1
                    elif str1[i] == '\'':
                        strtemp = strtemp + str1[i]
                        i = i + 1
                        tag = 2
                    else:
                        string.append(str1[i])
                        j = i + 1
                        i += 1
                else:
                    i += 1
            elif tag == 1:
                if str1[i] != '"':
                    strtemp = strtemp + str1[i]
                    i = i + 1
                else:
                    strtemp = strtemp + str1[i]
                    string.append(strtemp)
                    strtemp = ''
                    tag = 0
                    j = i + 1
                    i += 1
            elif tag == 2:
                if str1[i] != '\'':
                    strtemp = strtemp + str1[i]
                    i = i + 1
                else:
                    strtemp = strtemp + str1[i]
                    string.append(strtemp)
                    strtemp = ''
                    tag = 0
                    j = i + 1
                    i += 1
        count = 0
        for sub in string:
            if sub == spa:
                count += 1
        for i in range(count):
            string.remove('')
        CreateVariable(string, token)
        j = 0
        while j < len(token):
            if token[j] in constValue:
                token[j] = token[j]
                j += 1
            elif j < len(token) and isphor(token[j], variable): 
                if (token[j] in keywords_0) or (token[j] in typewords_0) or (token[j] in typewords_1 or token[j] in typewords_2):  
                    j += 1
                elif j - 1 >= 0 and j + 1 < len(token) and token[j-1] == 'new' and token[j + 1] == '[':
                    j = j + 2
                elif j + 1 < len(token) and token[j + 1] == '(':  
                    if token[j] in keywords_1:  
                        j = j + 2
                    elif token[j] in keywords_2: 
                        j = j + 2
                    elif isinKeyword_3(token[j]):
                        j = j + 2
                    elif token[j] in keywords_4:
                        j = j + 2
                    elif isinKeyword_5(token[j]): 
                        j = j + 2
                    else:
                        if token[j] in _func_dict.keys():
                            token[j] = _func_dict[token[j]]
                        else:
                            list_values = _func_dict.values()
                            if len(list_values) == 0:
                                _func_dict[token[j]] = 'func_0'
                                token[j] = _func_dict[token[j]]                               
                            else:
                                if token[j] in _func_dict.keys():
                                    token[j] = _func_dict[token[j]]
                                else:
                                    list_num = []
                                    for value in list_values:
                                        list_num.append(int(value.split('_')[-1]))
                                    _max = max(list_num)
                                    _func_dict[token[j]] = 'func_' + str(_max+1)
                                    token[j] = _func_dict[token[j]]
                            j = j + 2
                elif j + 1 < len(token) and (not isphor(token[j + 1], variable)):  
                    if token[j + 1] == '*':
                        if j + 2 < len(token) and token[j + 2] == 'const':
                            j = j + 3
                        elif j - 1 >= 0 and token[j - 1] == 'const':
                            j = j + 2
                        elif j - 1 > 0 and (token[j - 1] in operators):
                            list_values = _variable_dict.values()
                            if len(list_values) == 0:
                                _variable_dict[token[j]] = 'variable_0'
                                token[j] = _variable_dict[token[j]]                               
                            else:
                                if token[j] in _variable_dict.keys():
                                    token[j] = _variable_dict[token[j]]
                                else:
                                    list_num = []
                                    for value in list_values:
                                        list_num.append(int(value.split('_')[-1]))
                                    _max = max(list_num)
                                    _variable_dict[token[j]] = 'variable_' + str(_max+1)
                                    token[j] = _variable_dict[token[j]]
                            j = j + 2
                        elif j + 2 < len(token) and token[j + 2] == ')':
                            j = j + 2
                        elif j - 2 > 0 and (token[j - 1] == '(' and token[j - 2] in operators): 
                            list_values = _variable_dict.values()
                            if len(list_values) == 0:
                                _variable_dict[token[j]] = 'variable_0'
                                token[j] = _variable_dict[token[j]]                             
                            else:
                                if token[j] in _variable_dict.keys():
                                    token[j] = _variable_dict[token[j]]
                                else:
                                    list_num = []
                                    for value in list_values:
                                        list_num.append(int(value.split('_')[-1]))
                                    _max = max(list_num)
                                    _variable_dict[token[j]] = 'variable_' + str(_max+1)
                                    token[j] = _variable_dict[token[j]]
                            j = j + 2
                        else:
                            list_values = _variable_dict.values()
                            if len(list_values) == 0:
                                _variable_dict[token[j]] = 'variable_0'
                                token[j] = _variable_dict[token[j]]
                            else:
                                if token[j] in _variable_dict.keys():
                                    token[j] = _variable_dict[token[j]]
                                else:
                                    list_num = []
                                    for value in list_values:
                                        list_num.append(int(value.split('_')[-1]))
                                    _max = max(list_num)
                                    _variable_dict[token[j]] = 'variable_' + str(_max+1)
                                    token[j] = _variable_dict[token[j]]

                            j = j + 2
                    else:
                        list_values = _variable_dict.values()
                        if len(list_values) == 0:
                            _variable_dict[token[j]] = 'variable_0'
                            token[j] = _variable_dict[token[j]]                             
                        else:
                            if token[j] in _variable_dict.keys():
                                token[j] = _variable_dict[token[j]]
                            else:
                                list_num = []
                                for value in list_values:
                                    list_num.append(int(value.split('_')[-1]))
                                _max = max(list_num)
                                _variable_dict[token[j]] = 'variable_' + str(_max+1)
                                token[j] = _variable_dict[token[j]]
                        j = j + 2
                elif j + 1 == len(token):
                    list_values = _variable_dict.values()
                    if len(list_values) == 0:
                        _variable_dict[token[j]] = 'variable_0'
                        token[j] = _variable_dict[token[j]]                              
                    else:
                        if token[j] in _variable_dict.keys():
                            token[j] = _variable_dict[token[j]]
                        else:
                            list_num = []
                            for value in list_values:
                                list_num.append(int(value.split('_')[-1]))
                            _max = max(list_num)
                            _variable_dict[token[j]] = 'variable_' + str(_max+1)
                            token[j] = _variable_dict[token[j]]
                        break
                else:
                    j += 1
            elif j < len(token) and isphor(token[j], number): 
                j += 1
            elif j < len(token) and isphor(token[j], stringConst): 
                j += 1
            else:
                j += 1
        stemp = ''
        i = 0
        while i < len(token):
            if i == len(token) - 1:
                stemp = stemp + token[i]
            else:
                stemp = stemp + token[i] + ' '
            i += 1

        list_code[index] = stemp
        index += 1
    return list_code

