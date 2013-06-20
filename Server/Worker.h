#pragma once
 
#include <vector>
#include <map>
#include <boost/asio.hpp>
#include <boost/pool/pool.hpp>
#include <boost/function.hpp>
#include <boost/shared_array.hpp>
#include <boost/shared_ptr.hpp>
#include "lockfreequeue.h"

#define NET_INSERT_VEC 0
#define NET_SEARCH_VEC 1
#define NET_CHECK_SERVER 2
#define WORKER_SIZE 30
#define MEM_SIZE 1024*1024*512
typedef boost::function<void (unsigned char*)> TYPE_SEND_CB;


struct SWorkData
{
    int nID;
    int nSize;
    unsigned char* pData;
};

class MatchCount
{
public:

	MatchCount(void)
	{
		ID=0;
		count=0;
	};
	MatchCount(int c_id,int c_count)
	{
		ID=c_id;
		count=c_count;
	};
	int ID;
	int count;
};

struct requestKeyData
{
	int nType;
	int nId;
	int nSeq;
	boost::shared_array<unsigned char> pData;
};

struct responseKeyData
{
	int nType;
	int nId;
	int nSeq;
	std::vector<boost::shared_ptr<MatchCount> > pData;
};

class CWorker
{
private:
    boost::pool<> m_Pool;
	LockFreeQueue<SWorkData> m_WorkList;
    std::map<int, TYPE_SEND_CB> m_SendAdress;
  
    enum EEnum
    {
        eBufSize = 128,
    };
 
public:
	boost::shared_ptr<LockFreeQueue<requestKeyData> > reqQ[WORKER_SIZE];
	boost::shared_ptr<LockFreeQueue<responseKeyData> > resQ[WORKER_SIZE];
    void AdrInsert(int nID, TYPE_SEND_CB cb)
    {
        m_SendAdress.insert(std::map<int, TYPE_SEND_CB>::value_type(nID, cb));
    }
  
    bool SendToAdr(int nID, int nSize, unsigned char* pData)     // ¹Þ» id, º¸³¾ data
    {
        std::map<int, TYPE_SEND_CB>::const_iterator it = m_SendAdress.find(nID);
        if(it != m_SendAdress.end())
            (it->second)(pData);
        else
            return false;
  
        return true;
    }
  
    void AddWork(int nID, int nSize, unsigned char* pData)
    {
        SWorkData temp;
        temp.nID = nID;
        temp.nSize = nSize;
        temp.pData = (unsigned char*)m_Pool.ordered_malloc(nSize);
        std::copy(pData, pData+nSize, temp.pData);
		m_WorkList.Produce(temp);
    }
    bool GetWork(SWorkData &wd)
    {
		return m_WorkList.Consume(wd);
		//return false;
    }
  
    void Worker()
    {
        while(true)
        {
            usleep(50000);
            //std::cout << "Worker !!!" << std::endl;
            SWorkData temp;
            if(GetWork(temp))
            {

                if(temp.pData != NULL)
                {
                    std::cout << "Dequeue " << temp.nID << "'s : " << (*(char*)(temp.pData)) << std::endl;
                }
            }
        }
    }
  
    CWorker(void) : m_Pool(sizeof(eBufSize)) {};
    virtual ~CWorker(void) {};
};
