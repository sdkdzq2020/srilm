/*
//»ùÓÚngram·Ö´ÊµÄ·½·¨ÔÚÆäÖÐ
//Ö÷Òª½Ó¿Ú£º
pplFile()    ¶Ô´ý·Ö´ÊÎÄ¼þÖÐ¾ä×Ó£¬°¤¸ö¸ø³ö·Ö´Ê½á¹û¼°¶ÔÓ¦¾ä×Ó¸ÅÂÊ
* ngram --
*	Create and manipulate ngram (and related) models
*/

#ifndef lint
static char Copyright[] = "Copyright (c) 1995-2011 SRI International, 2012-2015 Microsoft.  All Rights Reserved.";
static char RcsId[] = "@(#)$Id: ngram.cc,v 1.138 2015-10-13 21:04:27 stolcke Exp $";
#endif

#ifdef PRE_ISO_CXX
# include <iostream.h>
#else
#include <iostream>
#if defined(_MSC_VER) || defined(WIN32)
#include <direct.h>
#else
#include <unistd.h>
#endif
using namespace std;
#endif
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <assert.h>
#ifndef _MSC_VER
#include <unistd.h>
#define GETPID getpid
#else
#include <process.h>
#define GETPID _getpid
#endif
#include <string.h>
#include <time.h>
#include <fstream>
#include <stdlib.h>
#ifdef NEED_RAND48
extern "C" {
	void srand48(long);
}
#endif

#include "option.h"
/*
#include "version.h"
*/
#include "File.h"
#include "Vocab.h"
/*
#include "SubVocab.h"
#include "MultiwordVocab.h"
#include "MultiwordLM.h"
#include "NonzeroLM.h"
#include "NBest.h"
#include "TaggedVocab.h"
*/

#include "Ngram.h"
#include "Debug.h"
/*
#include "TaggedNgram.h"
#include "StopNgram.h"
#include "ClassNgram.h"
#include "SimpleClassNgram.h"
#include "DFNgram.h"
#include "SkipNgram.h"
#include "HiddenNgram.h"
#include "HiddenSNgram.h"
#include "NullLM.h"
#include "LMClient.h"
#include "BayesMix.h"
#include "LoglinearMix.h"
#include "AdaptiveMix.h"
#include "AdaptiveMarginals.h"
#include "NgramCountLM.h"
#include "MSWebNgramLM.h"
#include "CacheLM.h"
#include "DynamicLM.h"
#include "DecipherNgram.h"
#include "HMMofNgrams.h"
#include "RefList.h"
#include "ProductNgram.h"
*/
#include "Array.cc"
#include "MEModel.h"
/*
#include "MStringTokUtil.h"
#include "BlockMalloc.h"
*/
#if defined(_MSC_VER) || defined(WIN32)
# define DEFAULT_MAX_CLIENTS	1

#else 
# define DEFAULT_MAX_CLIENTS	0		// unlimited
#endif

#define DEBUG_PRINT_WORD_PROBS		2

const unsigned defaultBeamSize = 4;
static unsigned order = defaultNgramOrder;
static unsigned beamsize = defaultBeamSize;
static unsigned debugid = 0;
static char *pplFile = 0;
static char* preclean = 0;
static char *lmFile = 0;
static char *lmFile2 = 0;
static int limitVocab = 0;
static char *escape = 0;
static int textFileHasWeights = 0;
static int seed = 0;  /* default dynamically generated in main() */


					  //ÃüÁîÐÐ£¬±£ÁôÓÐÓÃµÄÈýÏî£º-order 3 -lm model.lm -ppl testinput.txt
static Option options[] = {

	{ OPT_STRING, "seg", &pplFile, "text file to compute perplexity from" },
	{ OPT_UINT, "order", &order, "max ngram order" },
	{ OPT_STRING, "lm", &lmFile, "file in ARPA LM format for segment" },
	{ OPT_STRING, "lm2", &lmFile2, "file in ARPA LM format for prob get" },
	{ OPT_STRING,"pre",&preclean,"pre text clean for input text" },
	{ OPT_UINT, "debug", &debugid, "debugging level for lm" },
};

int execmd(char* cmd,char* result) {
	char buffer[128];                         //定义缓冲区                        
	FILE* pipe = popen(cmd, "r");            //打开管道，并执行命令 
	if (!pipe)
		return 0;                      //返回0表示运行失败 

	while(!feof(pipe)) {
		if(fgets(buffer, 128, pipe)){             //将管道输出到result中 
			strcat(result,buffer);
		//	cout<<"result:"<<result<<endl;
		}
	}
	pclose(pipe);                            //关闭管道 
	return 1;                                 //返回1表示运行成功 
}


int
main(int argc, char **argv)
{
	setlocale(LC_CTYPE, "");
	setlocale(LC_COLLATE, "");

	/* set default seed for randomization */
	seed = time(NULL) + GETPID();

	Opt_Parse(argc, argv, options, Opt_Number(options), 0);

	LM::initialDebugLevel = debugid;
	string curpwd = (string)argv[0];
	int index = curpwd.find_last_of("//");
	string subcwd = curpwd.substr(0, index);
	Vocab *vocab;
	Vocab *vocab2;
	Ngram *ngramLM;
	Ngram *ngramLM2;
	LM *useLM = 0;
	LM *probLM = 0;
	vocab = new Vocab;
	vocab2 = new Vocab;
	assert(vocab != 0);
	assert(vocab2 != 0);

	vocab->unkIsWord() = false;
	vocab->toLower() = false;
	ngramLM = new Ngram(*vocab, 1);  //ÉùÃ÷ºÍ³õÊ¼»¯Ò»¸öngramLM½á¹¹
	assert(ngramLM != 0);
	ngramLM2 = new Ngram(*vocab2, order);  //µÚÒ»¸ölmÓÃÀ´Í¨¹ý´ó´Êµä·Ö´Ê£¬ËùÒÔÊÇ1orderÈ·¶¨£¬µÚ¶þ¸öÊÇ²é·Ölm£¬ËùÒÔorder¿ÉÒÔÖ¸¶¨
	assert(ngramLM2 != 0);
	if (lmFile) {
		/*
		* Read just a single LM
		*/
		File file(lmFile, "r");

		if (!ngramLM->read(file, limitVocab)) {  //´Ë´¦ÎªloadNgramLMµÄÈë¿Ú£¬¼ÓÔØÄ£ÐÍ£¬´¢´æÔÚngramLM½á¹¹ÖÐ
			cerr << "format error in lm file " << lmFile << endl;
			exit(1);
		}
		useLM = ngramLM;
	}

	if (lmFile2) {
		/*
		* Read just a single LM
		*/
		File file2(lmFile2, "r");

		if (!ngramLM2->read(file2, limitVocab)) {  //´Ë´¦ÎªloadNgramLMµÄÈë¿Ú£¬¼ÓÔØÄ£ÐÍ£¬´¢´æÔÚngramLM½á¹¹ÖÐ
			cerr << "format error in lm file " << lmFile2 << endl;
			exit(1);
		}
		probLM = ngramLM2;
	}


	/*
	* Operations that apply to any Ngram LM created by one of the above steps
	*/
	if (useLM != ngramLM)
	{
		cerr << "need at least an -lm file specified\n";
		exit(1);
	}

	char* getline;
	char* buffer;
	buffer = getcwd(NULL, 0);
	if (pplFile)
	{
	//	string templine =pplFile;// "拨打电话10086";
		string filename=pplFile;
		 char result[1024*4]="";
		if (preclean) //need pre text clean
		{
			string outfile = (string)pplFile + "_cleanOut";
			string cmd;
			if (DEFAULT_MAX_CLIENTS)
				cmd = "C:\\Python27\\python StartTextCleanFinal_ID.py " + (string)pplFile + " " + outfile;
			else
				cmd = "python " + subcwd + "//StartTextCleanFinal_ID.py " + (string)pplFile + " " + outfile;
		//cout<<"cmd:"<<cmd<<endl;
	/*	char* tempcmd = (char*)cmd.c_str();
			if(execmd(tempcmd,result) == 1)
			{
			
			   getline = result;
		//	   cout<<"getline:"<<getline;
			}*/
			system(cmd.c_str());
			filename = outfile;
		}
		File file(filename.c_str(), "r");
		useLM->dout(cout);
		vector<string> lineVec;
		int totalwordnum = 0; int totaloovnum = 0;
		double totalsentprob = 0.0;
		int totalzeroprob = 0;
		int totalsentnum = 0;
		int numOOVs = 0;
		int zeroProbs = 0;
		while(getline = file.getline())
		{
			TextStats stats;
			totalsentnum += 1;
			vector<pair<string, string>> pathCanWordVP;
			double sentprobsum = 0.0;
			int sentwordnum = 0;
			int sentoovnum = 0;
			int sentzeroProb;
			vector<pair<string, int>> wordcodeCheckV;
			string outresult;
			string wordproblog;
			vector<string> getlineVec = useLM->split(getline,"\t");
			string id = getlineVec[0];
			string tline  = getlineVec[1];
			useLM->ngramModelSegment(tline, order, pathCanWordVP, beamsize);
			vector<string> pathresultVec = useLM->split(pathCanWordVP[0].first.c_str(), "_");
			outresult = pathresultVec[0].substr(4, pathresultVec[0].length());
			//probLM->pplLine((char*)outresult.c_str(), stats);
			//map<string, int>::iterator it;

			//map<string, int> submap = stats.OOVWordsMap;
			cout <<id<<"\t"<<outresult.c_str()<<endl;// "SegmentResult: \n" << outresult.c_str() << endl;
	//	cout << "problog: \n" << stats.problog.c_str();
		//	cout << "sentlog: \n" << stats.sentlog.c_str() << endl;
		//	cout << "OOVWords: " << endl;
		/*	for (it = submap.begin(); it != submap.end(); it++)
				cout << it->first.c_str() << ",";
			cout << endl;
			cout << "ZEROWords: " << endl;
			map<string,int> zeromap = stats.ZEROWordsMap;
			for (it = zeromap.begin(); it != zeromap.end(); it++)
				cout << it->first.c_str() << ",";
			cout << endl;
			cout << endl;*/
		}
	}

#ifdef DEBUG
	if (&ngramLM->vocab != vocab) {
		delete &ngramLM->vocab;
	}
	if (ngramLM != useLM) {
		delete ngramLM;
	}
	delete useLM;


	delete vocab;

	if (&ngramLM2->vocab != vocab2) {
		delete &ngramLM2->vocab;
	}
	if (ngramLM2 != probLM) {
		delete ngramLM2;
	}
	delete probLM;


	delete vocab2;

	return 0;
#endif /* DEBUG */

	exit(0);
}

