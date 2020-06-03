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




sys.path.append("./");




def genWordDict(dictfile):
    # 获取词典
    f = codecs.open(dictfile,'r','utf-8')
    worddict = {}
    id = 0
    for line in f.readlines():
	id +=1
        tline = line.strip().split("\t")
        worddict[tline[0]] = tline[1]
    return worddict

    
    


def checkWordInNgramValid(inputfile,worddict):
    fpngram = codecs.open(inputfile,"r","utf-8")
    for line in fpngram.readlines():
	line = line.strip()
	if line =="\2-grams":
		return
        if line.count("\t")==0:
            continue
        line = line.strip()
        tline = line.split("\t")
        word = tline[1]
	if " " in word:
		break
        if not worddict.has_key(word):
           print "OOV word:"+word.encode("utf-8")+"\t"+line.encode("utf-8")
        else:
            continue
    fpngram.close()

if len(sys.argv)<=1:
	print "Usage: inputlmfile dictfile\n"
	sys.exit()        
inputfile = sys.argv[1]
dictfile = sys.argv[2]
worddict = genWordDict(dictfile)
if __name__ == "__main__":
    lineid = 0

    checkWordInNgramValid(inputfile,worddict)
    

