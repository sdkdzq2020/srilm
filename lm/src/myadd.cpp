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
	for (int i = 2; i < maxLen; i += 2)	//ÿ�εݽ�һ������-gbk���룬2���ֽ�,maxlenΪһ���ʴ�����󳤶�
	{
		if (remain.length() >= i)
		{
			string head1 = remain.substr(0, i);

			map<string, int>::iterator it = wordSyms->find(head1);   //�ʱ�����һ��
			if (it != wordSyms->end())  //����ҵ�����ô���Ϊhead������Ϊremin��������headƴ����
			{
				head2 = head + " " + head1;
				string remain1 = remain.substr(i, remain.length());  //���µĴ���
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
		else if (remain.length() == 0)	//ֱ���˴α������꣬����Ϊ�գ�����head��ƴ�ӵĴ���δ�ҵ�����headΪĿǰ���ʴ���д��
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