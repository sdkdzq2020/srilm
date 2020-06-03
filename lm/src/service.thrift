namespace cpp ais

struct PrintTextStats
{
 1: string SegmengResult;
 2: string OOVWords;
 3: string ZerosProbWords;
 4: string ProbLog;
 5: string SentLog;
}

service NgramService {

   list<PrintTextStats> lm(1:list<string> src)

}
