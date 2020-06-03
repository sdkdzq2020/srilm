#ifndef __MYADD_H__
#define __MYADD_H__
#include <string>
#include <map>
#include <vector>

using namespace std;
#define MAX_NGRAM_LEN 1024
#define MAX_UTT_LEN 2048
#define UTT_END 1
#define UTT_ERR -1
#define UTT_CONTINUE 0

typedef struct tagSTRU_lmScore   //ÿһ�м�¼������id�����ʷ�ֵ��backoffֵ
{
	long long idx;
	float lmScore;
	float backoff;
}STRU_lmScore, *PST_lmScore;

typedef struct tagSTRU_ngram  //����ngram�ṹ��
{
	int ngramOrder;		//ngram������1 2 3 
	int maxWordLen;	//�������Ŀ
	int unigramNum;
	int bigramNum;
	int trigramNum;
	map <string, int> *wordSyms;		//����
	PST_lmScore lmScore;	//ÿ��gram�ķ���
}STRU_ngram, *PST_ngram;

/*********************************��������********************************************/
/**************************************************************************************/

int GetWordSymsFromNgram(map <string, int> *wordSyms, FILE *fp_lm, int size);
int LoadNgram(STRU_ngram *ngram, char *filePath, int inputNgram);
int LoadUtterance(vector <string> *utterance, char *filePath);
int MatchDict(map <string, int> *wordSyms, string head, string remain, int maxLen, vector <string> *splitUtt);
int NgramSplit(STRU_ngram ngram, string utt, int QSymNum, FILE *fp_out);
int GetSplitUttScore(string SentUtt, STRU_ngram ngram, int QSymNum, map<string, float> *ScoreMap);
vector<string> split(const string &s, const string &seperator);

#endif
