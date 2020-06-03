#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import pdb
import types
import re
import time
import sys



reload(sys)
sys.setdefaultencoding('utf-8')



sys.path.append("./");

#from langconv import *
from toChineseNumB2Q import *

numkeywords = []
NomodiList = ["4g","3g","5g","4d","3d","2d","4s","6s","7s"]
numendwords =[u'日',u'码',u'度',u'元',u'分',u'个',u'页',u'只',u'人',u'米',u'天',u'期',u'月',u'号']
spellKeyWords = [u'拨',u'拨通',u'fm',u'尾号',u'pm',u'电话',u'号码',u'座机',u'固话',u'手机',u'拨打',u'热线', \
        u'联系方式',u'10000',u'112',u'114',u'10086',u'10088',u'10010',u'110',u'119',u'120', \
        u'电话',u'UID',u'uid',u'ID',u'id',u'编号',u'尺码',u'qq',u'QQ']
punclist = [u",",u"°",u"+","}","≡","-","¤","×","←","※","↑","∧","↓","\\","\"","*","@","(",")","{","[","]","]","~","`","^","|","&",":","=",">","/","_","-","<","%","*","."]
punclistFull = ["|","《","》","“","”","·","】","【","§","、","丨","﹊","—","﹏","¨","ˉ","#","～","∴","α","丶","≥","﹉","-","…","‘","’","﹐","＊","：","――"];
subsentPunc = [u",",u",",u"，",u'。',u'！',u'？',',','\.','!','?',';',u'；']
set_miss = {}
numlist = ["1","2","3","4","5","6","7","8","9","0"]  #"0S":"(pm2.5|3g|4g|5g|2d|3d|es8)",
patterndic = {"1T":"\d+:\d+(~\d+:\d+)?","2S":"(\d+( |-)\d+([ -]\d+)?|0\d+( |-)\d+([ -]\d+)?)","MP":"\d{11}", \
        "2P":"(?<![\dmM])((19)?[89]\d|(20)?[012]\d)(?![\.\%\d])","N1":"(?<!0)\d+\.\d+","N0":"(?<!0)\d+(\.)?\d+%","LP":"\d{16,}", \
        "3P":"(0\d+|\d{3,11})(?![-\.])","N3":"\d+[\-\/\×\÷]\d+","N31":"\d+×\d+","N4":"\d{1,15}(?!\×)","N5":"1\d{10}(?!\d)"}
outlinelist = []
poslist = []


def ischinese(char):
    if char >= u'\u4e00' and char <= u'\u9fa5':
        return 1
    else:
        return 0

def isenglish(char):
    if char >= 'a' and char <= 'z':
        return 1
    elif char >= 'A' and char <= 'Z':
        return 1
    else:
        return 0





def isnumber(char):
    if char in numlist:
        return 1
    else:
        return 0

def ispun(char):
    if char in punclist:
        return ""
    elif char in punclistFull:
        return ""
    elif char in subsentPunc:
        return " "
    else:
        return char


def puncReplace(line):
    tline = line
    outline = ""
    for char in tline:
        out =ispun(char)
        if out!="":
            outline +=out
    return outline


def FullToHalf(s):
    n = []
    #s = s.decode('utf-8')
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        num = unichr(num)
        n.append(num)
    return ''.join(n)


def tradition2simple(line):
    
    return line
  
def checkDicExist(worddic,line,fantidic):
    outstr = ""
    outset = set()
    #print "inputline:",line
    tline = puncReplace(line)
    if tline=="":
        return
    flag = 0
    for char in tline:
        if fantidic.has_key(char):
            transw = fantidic[char]
        else:
        	transw = char
        transw = FullToHalf(transw)
        outstr += transw

#        if worddic.has_key(transw) or transw == ' ' or isenglish(transw):
            #outstr +=transw
 #           flag = 0
  #      else:
        #    flag = 1
    if outstr!="":
        outstr = re.sub("\s+"," ",outstr)
    return outstr

    
def getWordList(curpath):
    global f_w
    
    f_w = codecs.open(curpath+"/BigWordForNomi_wordlist.txt","r","utf-8")
    worddict = {}
    for line in f_w.readlines():
        line = line.strip()
        word = line[0]
        #if isenglish(word):
            #continue
        for item in word:
            worddict[item] = 1
    #for key in worddict.keys():
    #    print key
    f_w.close()
    return worddict

    
def getfantiList(curpath):
    global f_w
    
    f_w = codecs.open(curpath+"/fan2jian.dict","r","utf-8")
    fantidict = {}
    for line in f_w.readlines():
        line = line.strip().split("\t")
        word = line[0]
        jianword = line[1]
        fantidict[word] = jianword
    #for key in worddict.keys():
    #    print key
    f_w.close()
    return fantidict

    

def KeyWordCheckStart(line,secondflag,numflag): #查找句子中时间，电话等数字，记住标签以及标签的开始截止位置
    #print "keyline:",line
    if len(line) <1:
        return 
    pqueue = []
    qqueue = [] #写入起头位置，
    pqueue.append(0) #写入end位置，前一个的end位置到后一个的起头位置，之间的是suffix
    flag = ""
    flagdic = {}
    sortdic = {}
    endlist = []
    end = 0

    #pdb.set_trace()  # python单点调试的命令 n->单步前进
    for item in patterndic:
        poslist = []
        pattern = re.compile(patterndic[item])
        m = pattern.search(line.lower())
        if m:
            flag = item
            if m.start() in flagdic.keys():
                break
            if m.end() in endlist:
                break
            if line[m.end()-1] == "%":
                numflag = "1"
            if m.end()<len(line):
                if m.group()+line[m.end()]=="90后" or m.group()+line[m.end()]=="80后" :
                    flag = "2P"
                #elif m.group()+line[m.end()] in NomodiList:
                #    flag = "4P"
                elif line[m.end()] in numendwords and len(m.group())<=3:
                    flag = "N4"
                    secondflag = "0"
                elif len(m.group())==3 and line[m.end()]=="年":
                    flag = "N4"
                elif line[m.end()]=="年":
                    if m.end()+1<len(line) and line[m.end()+1]=="代":
                        flag = "N4"
                    else:
                        flag = "2P"
                elif flag =="2P" and line[m.end()]!="年":
                    numflag = "1"


            pqueue.append(m.end())
            qqueue.append(m.start())
            poslist.append(m.end())
            poslist.append(flag)
            flagdic[m.start()] = poslist
            endlist.append(m.end())
    sortdic = sorted(flagdic.iteritems(), key=lambda d:d[0], reverse=False)
    #key是起始位置，value是flag和结束位置，然后按照起始位置排序，可以得到对应的flag从前往后的顺序
    qqueue.append(len(line))
    pqueue = sorted(pqueue)
    qqueue = sorted(qqueue)
    return sortdic,pqueue,qqueue,secondflag,numflag
  
def numtextConvert(tline,secondflag,numflag):
    breakflag = 0
    outdic,pqueue,qqueue,secondflag,numflag = KeyWordCheckStart(tline,secondflag,numflag)
    #print "outdic:",outdic
    #if outdic == {}:
     #   outstr = tline
     #   breakflag = 1
     #   return outstr,secondflag,breakflag
    outstr = ""
    for obj in outdic:
        stpos = pqueue.pop(0)
        enpos = qqueue.pop(0)
        suffixline = tline[stpos:enpos]
        outstr += suffixline  #用队列形式，逐一得到每个前缀的起始位置和结束位置
        trnum = PatternMatchModi(tline,obj,secondflag,numflag)
        outstr += trnum  #和数字串拼接

    while(pqueue):
        stpos = pqueue.pop(0)
        enpos = qqueue.pop(0)
        suffixline = tline[stpos:enpos]
        outstr += suffixline
    return outstr,secondflag,numflag

def spKeyWords(string):
    #特殊关键词拼读
    secondflag = ""
    numflag = ""
    string = string.decode('utf-8')
    for i in spellKeyWords:
        p = re.compile(i)
        m = p.findall(string)
        if m:
            secondflag = "1"
            break
        else:
            secondflag = "0"
    for i in numkeywords:
        p = re.compile(i)
        m = p.findall(string)
        if m:
            numflag = "1"
            break
        else:
            numflag = "0"
    return secondflag,numflag


def PatternMatchModi(str,obj,secondflag,numflag):
    flag = obj[1][1]
#    print "flag:",flag
 #   print "secondflag:",secondflag
  #  print "numflag:",numflag
    needstr = str[obj[0]:obj[1][0]] #截取中间的数字串
    p = re.compile(patterndic[flag]) #根据不同的标签转移不同的数字处理
    trnum = ""
    for i in re.finditer(p, needstr):
        if numflag =="1":
            trnum = to_chineseNum(needstr,"N4")
        elif flag == "1T":
            trnum = to_chineseTime(needstr,flag)
        elif flag[1] == "P":# and secondflag == "0":
            trnum = to_chineseSpell(needstr,flag)
        elif flag[0] == "N" : 
            if secondflag == "0": 
                trnum = to_chineseNum(needstr,flag)
            elif secondflag == "1":
                trnum = to_chineseSpell(needstr, flag)
        elif flag[1] == "S" and secondflag == "0":
            trnum = chineseSpell(needstr, flag)

    return trnum


def lineFilter(strline):
    strline = re.sub("\(.*\)","",strline)  #将括号内的内容不保留（多数为编号，解释等）
    strline = re.sub("{.*}",'',strline)
    dicount = 0
    blcount = strline.count(" ")
    if strline.lower().find("http")!=-1 or strline.lower().find(".com")!=-1:  #网页链接的去掉
        return ""
    elif strline.find(u'买价') !=-1 or strline.find(u'散户')!=-1 or strline.find(u'万股')!=-1 or strline.find(u':-')!=-1 or strline.find(u'股票代码')!=-1:
        return ""
    elif len(strline)<=8:   #太短的去掉
        return ""
    elif float(blcount)/float(len(strline))>0.2:   #空格数目占字数的1/5 多为表格内容 去掉
        return ""
    for char in strline:
        if char.isdigit():
            dicount+=1
    if dicount > blcount and float((dicount+blcount))/float(len(strline)) >=0.5:  #如果一个句子中数字个数占2/3以上，该句子抛弃
        return ""
    strline = re.sub("^ +","",strline)
    strline = re.sub(" +$","",strline)
    strline = re.sub(" +"," ",strline)
    return strline


def removeDupLine(line):
    tlen = len(line)
    tset = set(line)
    slen = len(tset)
    if (slen*1.0/tlen*1.0) <0.5:
        return ""
    else:
        return line


def splitLongSents(line):
    line = line.strip()
    linelist = []
    outline = ""
    tid=0
    id = 0
    tlen = len(line)
    if tlen >=100:
        sublist = []
        id = 0
        tid = 0
        for tchar in line:
            id +=1
            tid+=1
            sublist.append(tchar)
            if id >=100:
                outline = "".join(sublist)
                #outline = removeDupLine(subline)
                #outline = lineFilter(outline)
                if len(outline)>1:
                    linelist.append(outline)
                id = 0
                sublist = []

    if id!=0:
        index = len(linelist)*100
        outline = line[index+1:tlen]
        linelist.append(outline)

    return linelist

def strQ2B(ustring):
    #把字符串全角转半角
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code==0x3000:
            inside_code=0x0020
        else:
            inside_code-=0xfee0
        if inside_code<0x0020 or inside_code>0x7e:
            rstring += uchar
        else:
            rstring += unichr(inside_code)
    return rstring



def lineReplace(strline):
    strline = re.sub(u'。',".",strline)
    strline = re.sub(u'？',"?",strline)
    strline = re.sub(u'！',"!",strline)
    strline = re.sub(u'，',",",strline)
    strline = re.sub(u'：',":",strline)
    strline = re.sub(u'－',"-",strline)
    strline = re.sub(u'°',"度",strline)
    strline = re.sub(u'（',"(",strline)
    strline = re.sub(u'℃',"摄氏度",strline)
    pattern = ":\d+-\d+-\d+:\d+"
    strline = re.sub(pattern,"",strline)
    return strline



def checkEnglishValid(outstr,Engset):
    p = re.compile("\w+")
    m = p.findall(outstr)
    flag = 0
    Englist = list(Engset)
    for item in m:
        if item in Englist:
            continue
        else:
            flag = 1
            outstr = outstr.replace(item,"")
    return outstr


def fullNumberConvert(tline):
    strline = re.sub(u'０',"0",tline)
    strline = re.sub(u'１',"1",strline)
    strline = re.sub(u'２',"2",strline)
    strline = re.sub(u'３',"3",strline)
    strline = re.sub(u'４',"4",strline)
    strline = re.sub(u'５',"5",strline)
    strline = re.sub(u'６',"6",strline)
    strline = re.sub(u'７',"7",strline)
    strline = re.sub(u'８',"8",strline)
    strline = re.sub(u'９',"9",strline)
    return strline



def textClean(tline,worddic,fantidic):
    id = 0
    id += 1
    tline = strQ2B(tline)
    strline = re.sub("\(.[^\)]*\)","",tline)  #将括号内的内容不保留（多数为编号，解释等）
    tline = re.sub("{.*}",'',strline)
    tline = re.sub("\[.*\]", "", tline)
    phanzi = re.compile(u'[\u4e00-\u9fa5]');
    chflag = phanzi.search(tline)
    #if chflag == None:
    #    return 
    #tline = lineFilter(tline)  #一开始就过滤掉一些句子
    if tline == "":
        return 
    #print "time2:",time.clock()
    numf = re.compile("\d+")
    outstr = tline
    breakflag = 0
    secondflag = ""
    try:
        while(numf.search(outstr)): #用数字串在句子中匹配，如果有匹配到，做数字转换处理
            #print "inputnum:",outstr
            secondflag,numflag = spKeyWords(outstr) #判断是否有关键词
            outstr,secondflag,numflag = numtextConvert(outstr,secondflag,numflag)
    except:
        pass
        #pdb.set_trace()
    #englistf = re.compile("\w+")
    #outstr = re.sub(englistf,"",outstr)
    outstr = re.sub(u'年年',u'年',outstr)
    #outstr = lineFilter(outstr)
    outstr = outstr.rstrip()
    tline = outstr
    tline = checkDicExist(worddic,tline,fantidic)
    if tline=="" or tline==None:
        return    
    tline = tline.strip()
    if tline !="" and len(tline)>0:
        return tline
         

def read_input(file):
    for line in file:
        yield line.rstrip()#rstrip()去除字符串右边的空格
        

        
if __name__ == "__main__":
    curpath = sys.path[0]
    worddic = getWordList(curpath)
    fantidic = getfantiList(curpath)
    #input = read_input(sys.stdin)#依次读取每行的数据
    id = 0
#    if len(sys.argv)<=1:
 #       print "Usage:inputfile outputfile"
  #      sys.exit(0)
    input = sys.argv[1]#依次读取每行的数据
    output =input+"_cleanOut"# sys.argv[2]
    fp = codecs.open(input,"r","utf-8")
    fpo = codecs.open(output,"w","utf-8")
    for line in fp.readlines():
        line = line.strip().lower()
	itemout = line.decode('utf-8')
	if "\t" in line:
        	strline = line.strip().split("\t")[1]
        	id = line.strip().split("\t")[0]
	else:
		strline = line.strip()
        strline = fullNumberConvert(strline)
        strline = lineReplace(strline)
        if strline == "":
             continue
        outline = textClean(strline,worddic,fantidic)
        if outline =="" or outline==None:
            continue
        else:
	    if "\t" in line:
		fpo.write(id+"\t"+outline+"\n")
	    else:
		fpo.write(outline+"\n")
    fpo.close()
    fp.close()


    

