# -*- coding: utf-8 -*-
import codecs

import types
import re
import pdb
import sys


class NotIntegerError(Exception):
    pass

class OutOfRangeError(Exception):
    pass

_MAPPING = (u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九' )

_P0 = (u'', u'十', u'百', u'千', )
_S4, _S8, _S16 = 10 ** 4 , 10 ** 8, 10 ** 16
_MIN, _MAX = 0, 9999999999999999
_SPEPUNC = (u'点')
_RATIOPUNC= (u'比')
_FROMPUNC =(u'至')
_PERCENTPUNC = u'百分之'
_GRADPUNC = u'分之'
typelist = [u'人',u'个',u'元',u'路',u'名',u'次',u'分',u'只',u'月',u'日',u'年',u'万',u'台',u'车',u'吨']
spellist = [u'年',u'号']
spellKeyWords = [u'电话',u'座机',u'固话',u'手机',u'拨打',u'热线',u'联系方式',u'电话',u'UID',u'uid',u'ID',u'id',u'编号',u'尺码',u'qq',u'QQ']
timeWords = [u'时间',u'上午',u'下午',u'今晚',u'早晨',u'晚上',u'几点',u'现在']
ratioWords = [u'比分',u'比赛',u'几比几',u'比率']
numpattern = "\d+,\d"
timepattern = "\d+:\d+"
numberpatern = "\d+"


def _to_chinese4(num):
    '''转换[0, 10000)之间的阿拉伯数字
    '''
    assert(0 <= num and num < _S4)
    if num < 10:
        return _MAPPING[num]
    else:
        lst = [ ]
        while num >= 10:
            lst.append(num % 10)
            num = num / 10
        lst.append(num)
    
        c = len(lst)    # 位数
        result = u''
        for idx, val in enumerate(lst):
            if val != 0:
                result += _P0[idx] + _MAPPING[val]
            if idx < c - 1 and lst[idx + 1] == 0:
                result += u'零'
    result = result[::-1]

    result = result.replace(u'一十', u'十')
    result = result.replace(u'百十', u'百一十')
    #result = result.replace(u'零零', u'零')
    if result[-1]=="零" and result[-2] !="零":
        result = result[:-1]

    return result


def to_chineseTime(strnum,flag):
    outstr = ""
    strlst = []
    strnum = strnum.split("~")
    id = 0
    for item in strnum:
        #print "item",item,len(strnum)
        outstr += timeconvert(item,flag)
        if id == 0 and len(strnum)>1:
            outstr+=_FROMPUNC
        id +=1
    return outstr


def timeconvert(item,flag):
    item = item.split(":")
    hour = item[0]
    minut = item[1]
    minut = re.sub("00","",minut)
    #print hour
    outstr=to_chineseNum(hour,flag)
    if flag == "1T": #TIME
        outstr += _SPEPUNC
    elif int(hour)>24:
        #print "R flag",outstr
        outstr +=_RATIOPUNC
    if(minut):
        outstr+=to_chineseNum(minut,flag)
    return outstr


def chineseSpell(strnum,flag):
    outstr = ""
    tstrnum = strnum.split("-")
    if flag == "2S" and len(tstrnum) > 1:
        try:
            strnum = tstrnum[0]
            monnum = tstrnum[1]
            daynum = tstrnum[2]
            monthout = _to_chinese4(int(monnum))
            dayout = _to_chinese4(int(daynum))
            strnum += u'年'
            monthout += u'月'
            dayout += u'日'
            outstr = strnum + monthout + dayout
        except:
            pass
    return outstr

def mappingVal(strlst):
    result = u""
    for val in strlst:
        if val == " " or val == u'、' or val == "]":
            result += " "
            continue
        elif val == u'年' or val == '.' or val == "/" or val == ")":
            result += u'年'
            continue
        elif val <= '9' and val >= '0':
            val = int(val)
            result += _MAPPING[val]
        else:
            result += val
    return result


    
def to_chineseSpell(strnum,flag):
    outstr = ""
    result = u''
    conflag = 0
    strlst = list(strnum)
    if "." in strnum:
        tstrnum = strnum.split(".")
        prenum = tstrnum[0]
        afternum =tstrnum[1]
        if len(prenum)<3 and flag[1] !="P":
   
            strconvert = _to_chinese4(int(prenum))
        else:
 
            strconvert =mappingVal(list(prenum))

            conflag =1
        monconvert = mappingVal(list(afternum))

        result = strconvert+"点"+monconvert
    else:
        if len(strnum)<3 and flag[1] !="P":
            result = _to_chinese4(int(strnum))
        else:

            result = mappingVal(strlst)
          
    outstr += result

    if flag == "MP" or flag == "LP" or flag == "D" or flag == "3P" or conflag ==1:
        outstr = outstr.replace(u'一',u'幺')

    return outstr
    
    '''
    if flag == "A1" and len(tstrnum)>1:
        strnum = tstrnum[0]
        monnum =tstrnum[1]
        # "monnum",monnum
        moout = _to_chinese4(int(monnum))
        moout += u'月'
    elif flag =="N1" and len(tstrnum)>1:
       """yearNum = tstrnum[0:3]
        monthNum = re.compile(tstrnum,"\\.\d\\.")
        dayNum = tstrnum[8:9]"""
    elif flag == "AP" :
        moout = u'年'
    '''
    
   
    
def _to_chinese8(num):
    assert(num < _S8)
    to4 = _to_chinese4
    if num < _S4:
        return to4(num)
    else:
        mod = _S4
    high, low = num / mod, num % mod
    if low == 0:
        return to4(high) + u'万'
    else:
        if low < _S4 / 10:
            return to4(high) + u'万零' + to4(low)
        else:
            return to4(high) + u'万' + to4(low)


def _to_chinese16(num):
    assert(num < _S16)
    to8 = _to_chinese8
    mod = _S8
    high, low = num / mod, num % mod
    if low == 0:
        return to8(high) + u'亿'
    else:
        if low < _S8 / 10:
            return to8(high) + u'亿零' + to8(low)
        else:
            return to8(high) + u'亿' + to8(low)


def to_chineseNum(strnum,flag):
    #if type(num) != types.IntType and type(num) != types.LongType:
    #    raise NotIntegerError(u'%s is not a integer.' % num)
    #if num < _MIN or num > _MAX:
    #    raise OutOfRangeError(u'%d out of range[%d, %d)' % (num, _MIN, _MAX))
    floatpart = 0
    outstr = ""
    if "%" in strnum:
        strnum = strnum.replace("%","")
        num = int(strnum)
        outstr +=_PERCENTPUNC
    elif "." in strnum:
        num = int(strnum.split(".")[0])
        floatpart = int(strnum.split(".")[1])
        floatpart = _to_chinese4(floatpart)
    elif "-" in strnum:
        num = int(strnum.split("-")[0])
        floatpart = int(strnum.split("-")[1])
        floatpart = _to_chinese4(floatpart)
    elif "/" in strnum:
        floatpart = int(strnum.split("/")[0])
        num = int(strnum.split("/")[1])
        floatpart = _to_chinese4(floatpart)
    else:
        num = int(strnum)
    if num < _S4:
        if ("-" in strnum):
            outstr += _to_chinese4(num)+_FROMPUNC+floatpart
        elif ("." in strnum):
            outstr += _to_chinese4(num) + _SPEPUNC + floatpart
        elif "/" in strnum:
            outstr +=_to_chinese4(num) +_GRADPUNC+floatpart
        else:
            outstr +=  _to_chinese4(num)
    elif num < _S8:
        if floatpart!=0:
            outstr += _to_chinese8(num)+floatpart
        else:
            outstr +=_to_chinese8(num)
    elif num>=_S8 and num < _S16:
        outstr += _to_chinese16(num)+floatpart
    else:
        outstr += strnum

    return outstr


