#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import pdb
import types
import Queue
import re
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')



sys.path.append("./");

dictfile = "./BigWordForNomi_wordlist.txt"


# 由规则处理的一些特殊符号
numMath = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
numMath_suffix = [u'.', u'%', u'亿', u'万', u'千', u'百', u'十', u'个']
numCn = [u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'〇', u'零']
numCn_suffix_date = [u'年', u'月', u'日']
numCn_suffix_unit = [u'亿', u'万', u'千', u'百', u'十', u'个']
special_char = [u'(', u')']
 
def isenglish(word):
    flag = 0
    for char in word:
        if char >= 'a' and char <= 'z':
            flag = 1
            continue
        elif char >= 'A' and char <= 'Z':
            flag = 1
            continue
        else:
            return 0
    if flag ==1:
            return 1


def getWordList():
    global f_w
    #得到词典中所有字的列表，为了判断例外字
    f_w = codecs.open(dictfile,"r","utf-8")
    chardict = {}
    for line in f_w.readlines():
        line = line.strip()
        word = line[0]
        if isenglish(word):
            continue
        for item in word:
            chardict[item] = 1

    f_w.close()
    return chardict


def genDict(cuppath):
    # 获取词典
    f = codecs.open(cuppath+"//"+dictfile,'r','utf-8')
    worddict = {}
    newlist = set()
    for line in f.readlines():
        word = line.strip()
        newlist.add(word)
        worddict[word] = 1
    # 建立词典
    # key为词首字，value为以此字开始的词构成的List
    truedict = {}
    for item in newlist:
        if len(item)>0 and item[0] in truedict:
            value = truedict[item[0]]
            value.append(item)
            truedict[item[0]] = value
        else:
            truedict[item[0]] = [item]
    return truedict,worddict

def engprocess(line):

    tline = line.split("-")
    outline = ""
    for item in tline:
        item = item.strip()
        if isenglish(item):
            outline +=item
        else:
            outline +="-"
            outline +=item
            outline += "-"
    outline = re.sub("-+"," ",outline)
    return outline

def divideWords(mydict, sentence,worddict):
    """ 
    根据词典对句子进行分词,
    使用正向匹配的算法，从左到右扫描，遇到最长的词，
    就将它切下来，直到句子被分割完闭
    """
    ruleChar = []
    ruleChar.extend(numCn)
    ruleChar.extend(numMath)
    result = []
    start = 0
    senlen = len(sentence)
    while start < senlen:
        curword = sentence[start]
        maxlen = 1
        # 首先查看是否可以匹配特殊规则
        #if curword in numCn or curword in numMath:
        #    maxlen = rules(sentence, start)
        # 寻找以当前字开头的最长词
        if curword in mydict:
            words = mydict[curword]
            for item in words:
                itemlen = len(item)
                if sentence[start:start+itemlen] == item and itemlen > maxlen:
                    maxlen = itemlen
        else:
            #print "not in dict:",curword+"\t"+sentence
            return ""
        result.append(sentence[start:start+maxlen])
        start = start + maxlen
    checkresult = []
    for item in result:
        #print "item:",item
        if item not in worddict.keys():
           # print "not in :",item
            continue
        else:
            checkresult.append(item)
    out = "-".join(checkresult)

    return out

    
    
def divideSent(line,segdict,worddict):
    line = line.strip()
    if line !="":
        if len(line)==0:
            return
        if line.count('\n')==len(line):
            return
        else:
            try:
                tline = line.decode("utf-8")
                tline = tline.split(" ")
                toutline = ""
                for item in tline:
                    item = item.lower()
                    tresult = divideWords(segdict,item,worddict)
                    strlin=re.sub(" +"," ",tresult)
                   
                    outline = engprocess(strlin)
                    toutline +=outline
                    toutline +=" "
                toutline = re.sub(" +"," ",toutline)
                #toutlist = toutline.split(" ")
                #for item in toutlist:
                 #   if item not in worddict.keys():
                if toutline!="":
                    print toutline.strip().encode("utf-8")

            except:
                return
        

if __name__ == "__main__":
    cuppath = sys.path[0]
    segdict,worddict= genDict(cuppath)
    lineid = 0
    
    for line in sys.stdin:
        lineid +=1
        divideSent(line,segdict,worddict)
    

