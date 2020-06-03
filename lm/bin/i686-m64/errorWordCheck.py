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



commonRep = {
	        u" 喜 马 拉 雅 ":u" 喜马拉雅 ",
        	u" 喜 马 拉 雅$":u" 喜马拉雅",
        	u"^喜 马 拉 雅 ":u"喜马拉雅 ",
       		u" 未来 汽":u" 蔚来 汽",
        	u"^未来 汽":u"蔚来 汽",
        	u" 未 来 汽":u" 蔚来 汽",
        	u"^未 来 汽":u"蔚来 汽",
        
        	u" 蔚 来 ":u" 蔚来 ",
		u" 主 驾 ":u" 主驾 ",
		u" 副 驾 ":u" 副驾 ",
		u" 氛围 灯 ":u" 氛围灯 ",
		u" 阅读 灯 ":u" 阅读灯 ",
		u" 充电 桩 ":u" 充电桩 ",
		u" 胎 压 ":u" 胎压 ",
		u" 遮阳 帘 ":u" 遮阳帘 ",
		u" 遮 阳 帘 ":u" 遮阳帘 ",
		u" 净 化 ":u" 净化 ",

		u"^蔚 来 ":u"蔚来 ",
		u"^主 驾 ":u"主驾 ",
		u"^副 驾 ":u"副驾 ",
		u"^氛围 灯 ":u"氛围灯 ",
		u"^阅读 灯 ":u"阅读灯 ",
		u"^充电 桩 ":u"充电桩 ",
		u"^胎 压 ":u"胎压 ",
		u"^遮阳 帘 ":u"遮阳帘 ",
		u"^遮 阳 帘 ":"遮阳帘 ",
		u"^净 化 ":u"净化 ",
		u"es 八":u"es8",

		u" 蔚 来$":u" 蔚来",
		u" 主 驾$":u" 主驾",
		u" 副 驾$":u" 副驾",
		u" 氛围 灯$":u" 氛围灯",
		u" 阅读 灯$":u" 阅读灯",
		u" 充电 桩$":u" 充电桩",
		u" 胎 压$":u" 胎压",
		u" 遮阳 帘$":u" 遮阳帘",
		u" 遮 阳 帘$":u" 遮阳帘",
		u" 净 化$":u" 净化",
		u"hinomi":u" hi nomi ",
		u" nominomi":u" nomi "
	} 



def replaceLine(tline):
        for (key,value) in commonRep.items():
                tline =re.sub(key,value,tline)
        return tline

inputfile = sys.argv[1]
fp = codecs.open(inputfile,"r","utf-8")
flag = 0
prefile = ""
outfile = inputfile+"_convert"
fpo = codecs.open(outfile,"w","utf-8")
curpath = os.getcwd()
id = 0
for line in fp.readlines():
        line = line.strip()
        tsent = replaceLine(line)
	tsent = tsent.strip()
	tsent = re.sub("  +"," ",tsent)
        fpo.write(tsent+"\n")


fpo.close()
fp.close()
