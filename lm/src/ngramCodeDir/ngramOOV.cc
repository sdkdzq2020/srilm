/*
//基于ngram分词的方法在其中
//主要接口：
pplFile()    对待分词文件中句子，挨个给出分词结果及对应句子概率
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
//#include "json.h"
//#include "json-forwards.h"
#include <assert.h>
#ifndef _MSC_VER
#include <unistd.h>
#define GETPID getpid
#else
#include <process.h>
#define GETPID _getpid
#endif
#include <string.h>
#include <string>
#include <time.h>
#include <fstream>
#include <stdlib.h>
#ifdef NEED_RAND48
extern "C" {
	void srand48(long);
}
#endif

#include "option.h"
#include "File.h"
#include "Vocab.h"
#include "Ngram.h"
#include "Debug.h"

#include "Array.cc"
#include "MEModel.h"

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
static int limitVocab = 0;
static char *escape = 0;
static int textFileHasWeights = 0;
static int seed = 0;  /* default dynamically generated in main() */


					  //命令行，保留有用的三项：-order 3 -lm model.lm -ppl testinput.txt
static Option options[] = {

	{ OPT_STRING, "seg", &pplFile, "text file to compute perplexity from" },
	{ OPT_UINT, "order", &order, "max ngram order" },
	{ OPT_STRING, "lm", &lmFile, "file in ARPA LM format" },
	{ OPT_STRING,"pre",&preclean,"pre text clean for input text" },
	{ OPT_UINT, "debug", &debugid, "debugging level for lm" },
};



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
	Ngram *ngramLM;


	LM *useLM = 0;
	vocab = new Vocab;
	assert(vocab != 0);

	vocab->unkIsWord() = false;
	vocab->toLower() = false;
	ngramLM = new Ngram(*vocab, order);  //声明和初始化一个ngramLM结构
	assert(ngramLM != 0);
	if (lmFile) {
		/*
		* Read just a single LM
		*/
		File file(lmFile, "r");

		if (!ngramLM->read(file, limitVocab)) {  //此处为loadNgramLM的入口，加载模型，储存在ngramLM结构中
			cerr << "format error in lm file " << lmFile << endl;
			exit(1);
		}
		useLM = ngramLM;
	}

	/*
	* Operations that apply to any Ngram LM created by one of the above steps
	*/
	if (useLM != ngramLM)
	{
		cerr << "need at least an -lm file specified\n";
		exit(1);
	}


	/*
	* Compute perplexity on a text file, if requested
	如下此处，为读入待测试文件中句子，函数内给出每个句子分词结果的入口
	useLM为待使用ngramLM，file为含有待分词的句子的文件
	*/
	char* getline;
	char* buffer;
	buffer = getcwd(NULL, 0);
	if (pplFile)
	{
		string filename = pplFile;
		if (preclean) //need pre text clean
		{
			string outfile = (string)pplFile + "_cleanOut";
			string cmd;
			if (DEFAULT_MAX_CLIENTS)
				cmd = "C:\\Python27\\python StartTextCleanFinal.py " + (string)pplFile + " " + outfile;
			else
				cmd = "python " + subcwd + "//StartTextCleanFinal.py " + (string)pplFile + " " + outfile;
			//cout << "cmd:" << cmd.c_str() << endl;
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
		map<string,int> OOVWordMap;
		map<string,int> ZeroWordMap;
		int zeroProbs = 0;
		while ((getline = file.getline()))
		{
			totalsentnum += 1;
			vector<string> lineOOV;
			vector<pair<SingleTextStats, string>> pathCanWordVP;
			double sentprobsum = 0.0;
			int sentwordnum = 0;
			int sentoovnum = 0;
			int sentzeroProb;
			vector<pair<string, int>> wordcodeCheckV;
			//useLM->checkEngword((string)getline, wordcodeCheckV);
			string outresult;
			string wordproblog;
			useLM->ngramModelSegment(getline, order, pathCanWordVP, beamsize);
		
			SingleTextStats pathresult = pathCanWordVP[0].first;
			outresult.append(pathresult.preword.substr(4, pathresult.preword.length()));
			wordproblog += pathresult.problog;
			if ((pathresult.OOVWord).length()!=1)
				lineOOV = useLM->split(pathresult.OOVWord, ",");
				for(int i =0;i<lineOOV.size();i++)
				{
					OOVWordMap[lineOOV[i]] = 1;
				}
			lineOOV.clear();
		       if ((pathresult.lowProbWord).length()!=1)
                                lineOOV = useLM->split(pathresult.lowProbWord, ",");
                                for(int i =0;i<lineOOV.size();i++)
                                {
                                        ZeroWordMap[lineOOV[i]] = 1;
                                }
			lineOOV.clear();
			if (atof(pathCanWordVP[0].second.c_str()) != LogP_Zero)
				sentprobsum += atof(pathCanWordVP[0].second.c_str());
			pathCanWordVP.clear();
			cout << outresult.c_str() << endl;

			//Json::Value jsonRoot; //定义根节点
			//Json::Value jsonItem; //定义一个子对象

			// << "\t" << pathCanWordVP[0].second.c_str() << endl;
			if (debugid==2)
			{
			/*cout << "[\n\t{" << endl;
			cout << "\t\t" << "\"" << "0SegmengResult" << "\"" << " : " << "\"" << outresult.c_str() << "\"," << endl;
			cout << "\t\t" << "\"" << "1OOVWords" << "\"" << " : " << "\"" << pathresult.OOVWord.c_str() << "\"," << endl;
			cout << "\t\t" << "\"" << "2ZerosProbWords" << "\"" << " : " << "\"" << pathresult.lowProbWord.c_str() << "\"," << endl;
			cout << "\t\t" << "\"" << "3ProbLog" << "\"" << " : " << "\"" << wordproblog.c_str() << "\"," << endl;
			*/


			double denom = pathresult.wordnum - pathresult.numOOVs - pathresult.zeroProbs + 1;
			cout << wordproblog.c_str() << endl;
			cout << "1 sentence," << pathresult.wordnum << " words," << pathresult.numOOVs << " OOVs " << endl;
		
			cout << pathresult.zeroProbs<< " zeroProbs, logprobs = " << sentprobsum << " ,ppl = " << LogPtoPPL(sentprobsum / denom) << endl;


			/*string sentlog = "";
			sentlog = "1 sentence,";
			sentlog += to_string(pathresult.wordnum) + " words," + to_string(pathresult.numOOVs);
			sentlog += " OOVs, ";
			sentlog += to_string(pathresult.zeroProbs) + " zeroProbs,\n logprobs = ";
			sentlog += to_string(sentprobsum);
			sentlog += " ,ppl = ";
			sentlog += to_string(LogPtoPPL(sentprobsum / denom));*/


			}

			totalwordnum += pathresult.wordnum;
			totaloovnum += pathresult.numOOVs;
			totalzeroprob += pathresult.zeroProbs;
			totalsentprob += sentprobsum;

		}
		if (debugid == 2)
		{

		cout << "\nfile :" << totalsentnum << " sentences, " << totalwordnum << " words," << totaloovnum << " OOVs, " <<totalzeroprob<<" zeroprobs"<< endl;
		cout << " OOVWords: \n\t" ;
		map<string,int> ::iterator it;
		for(it =  OOVWordMap.begin();it!=OOVWordMap.end();it++)
			cout<< it->first.c_str() <<",";
		cout<<endl;
		cout << "logprobs = " << totalsentprob << " ppl = " << LogPtoPPL(totalsentprob / (totalwordnum - totaloovnum - totalzeroprob + totalsentnum)) << endl;


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

	return 0;
#endif /* DEBUG */

	exit(0);
}

