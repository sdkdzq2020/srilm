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
# include <iostream>
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

#ifdef NEED_RAND48
extern "C" {
	void srand48(long);
}
#endif

#include "option.h"
#include "version.h"
#include "File.h"
#include "Vocab.h"
#include "SubVocab.h"
#include "MultiwordVocab.h"
#include "MultiwordLM.h"
#include "NonzeroLM.h"
#include "NBest.h"
#include "TaggedVocab.h"
#include "Ngram.h"
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
#include "Array.cc"
#include "MEModel.h"
#include "MStringTokUtil.h"
#include "BlockMalloc.h"

#if defined(_MSC_VER) || defined(WIN32)
# define DEFAULT_MAX_CLIENTS	1
#else 
# define DEFAULT_MAX_CLIENTS	0		// unlimited
#endif

static unsigned order = defaultNgramOrder;
static unsigned debug = 0;
static char *pplFile = 0;
static char *lmFile = 0;
static int limitVocab = 0;
static char *escape = 0;
static int textFileHasWeights = 0;
static int seed = 0;  /* default dynamically generated in main() */


					  //命令行，保留有用的三项：-order 3 -lm model.lm -ppl testinput.txt
static Option options[] = {

	{ OPT_STRING, "ppl", &pplFile, "text file to compute perplexity from" },
{ OPT_UINT, "order", &order, "max ngram order" },
{ OPT_STRING, "lm", &lmFile, "file in ARPA LM format" },
{ OPT_UINT, "debug", &debug, "debugging level for lm" }
};



int
main(int argc, char **argv)
{
	setlocale(LC_CTYPE, "");
	setlocale(LC_COLLATE, "");

	/* set default seed for randomization */
	seed = time(NULL) + GETPID();

	Opt_Parse(argc, argv, options, Opt_Number(options), 0);



	/*
	* Set random seed
	*/
	srand48((long)seed);

	/*
	* Construct language model
	*/

	LM::initialDebugLevel = debug;

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
	string sentSegResult;
	char* getline;
	vector<string> WordProbVec;

	if (pplFile) 
	{
		File file(pplFile, "r");
		TextStats stats;

		/*
		* Send perplexity info to stdout
		*/
		useLM->dout(cout);
		while ((getline = file.getline()))
		{
		useLM->pplFile(getline, stats, sentSegResult, WordProbVec, escape, textFileHasWeights);
		for (int i = 0; i < WordProbVec.size(); i++)
		{
			cout << WordProbVec[i].c_str();
		}
		cout << sentSegResult.c_str() << endl;
		useLM->dout(cerr);
		}
		cout << "file " << pplFile << ": " << stats;
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

