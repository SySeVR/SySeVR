# -*- coding:utf-8 -*-

from optparse import OptionParser
import re
import os
import pickle

def autoGetVulLine(rawPath,fileName):
    with open(fileName) as f:
        flag = 0
        path = ''
        txtstring = ''
        vulLineFile = open(fileName[:-4]+'.pkl','wb')
        txtfile = open(fileName[:-4]+'.txt','w')
        #print fileName
        flawLineList = set([])
        file2FlawLineDict = {}
        for line in f.readlines():
            filePath = re.findall('<file path=\"(.+)\" language=\"',line)
            if not filePath:
                fileEndFlag = re.findall('</file>',line)
                flawLine = re.findall('<flaw line=\"(\d+)\" name=\"',line)
                mixLine = re.findall('<mixed line=\"(\d+)\" name=\"',line)
                if flag == 1 and flawLine:
                    flawLineList.add(flawLine[0])
                    #txtstring1 = txtstring + os.path.join(rawPath,path)+' '+flawLine[0] + '\n'
                    #print flawLine[0]
                if flag == 1 and mixLine:
                    flawLineList.add(mixLine[0])
                    #txtstring2 = txtstring + os.path.join(rawPath,path)+' '+mixLine[0] + '\n'
                if flag == 1 and fileEndFlag:
                    flag = 0
                    if flawLineList and os.path.exists(os.path.join(rawPath,path)) and path.find('shared') == -1:
                        file2FlawLineDict[os.path.join(rawPath,path)] = set(flawLineList)
                        txtstring1 =  ''
                        txtstring2 = ''
                        '''
                        for num in flawLineList:
                            if num == '0':
                                continue
                            vulLineFile.write( path + ' ' + num + '\n')
                        '''
                        #vulLineFile.write('\n')
                    path = ''
                    flawLineList.clear()
                continue
            else:
                path = filePath[0]
                flag = 1
        pickle.dump(file2FlawLineDict,vulLineFile)
        #txtfile.write(txtstring)
        for key in file2FlawLineDict.keys():
            for line in file2FlawLineDict[key]:
                txtstring = txtstring + key +' '+line + '\n'
        txtfile.write(txtstring) 



if __name__ == '__main__':
    #若需要输入路径，请输入绝对路径
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) != 2:
        print 'Usage error, you need to declare original path.\n'
    else:
        autoGetVulLine(args[0],args[1])
