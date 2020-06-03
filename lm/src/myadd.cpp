/*
* myadd --by ljq 2017/07/05
*	Create and manipulate ngram (and related) models
*/
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <cmath>
#include "myadd.h"

using namespace std;
int MatchDict(map <string, int> *wordSyms, string head,
	string remain, int maxLen, vector <string> *splitUtt)
{

	string head2;
	for (int i = 2; i < maxLen; i += 2)	//每次递进一个汉字-gbk编码，2个字节,maxlen为一个词串的最大长度
	{
		if (remain.length() >= i)
		{
			string head1 = remain.substr(0, i);

			map<string, int>::iterator it = wordSyms->find(head1);   //词表中找一字
			if (it != wordSyms->end())  //如果找到，则该词语为head，余下为remin。继续给head拼接字
			{
				head2 = head + " " + head1;
				string remain1 = remain.substr(i, remain.length());  //余下的词语
																	 //cout<< head2.c_str()<<"    "<< remain1.c_str()<<endl;   
				int ret = MatchDict(wordSyms, head2, remain1, maxLen, splitUtt);
				if (UTT_END == ret)
				{

					break;
				}
				else if (UTT_ERR)
				{
					continue;
				}
			}
		}
		else if (remain.length() == 0)	//直到此次遍历走完，余下为空，代表head后拼接的词语未找到，则head为目前最大词串。写入
		{
			splitUtt->push_back(head);
			return UTT_END;
		}
		else
		{
			return UTT_ERR;
		}
	}

	return UTT_CONTINUE;
}