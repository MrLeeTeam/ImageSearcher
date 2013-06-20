#include <stdio.h>
#include <time.h>  
#include <ctime>
#include <cstdio>
#include <iostream>
#include <sstream>
#include <string>
#include <boost/asio.hpp>
#include <ctime>
#include <vector>
#include <boost/bind.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/enable_shared_from_this.hpp>
#include <boost/asio.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/thread.hpp>
#include <boost/shared_array.hpp>
#include <smmintrin.h>

#include "Worker.h"
#include "ThreadPool.h"
#include "lockfreequeue.h"

using boost::asio::ip::tcp;

CWorker g_Worker;
  
#ifndef NDEBUG
#define DEBUGMSG(msg...) {fprintf(stderr, msg);fprintf(stderr, "\n");}
#else
#define DEBUGMSG(msg...)
#endif


class CConnection : public boost::enable_shared_from_this<CConnection>
{
private:
    tcp::socket m_Socket;
    int m_nID;
 
    enum EEnum
    {
        eBufSize = 102400,
    };

  
    std::string m_sMsg;
	boost::asio::streambuf m_RecvBuf;
    //boost::array<unsigned char, eBufSize> m_RecvBuf;
  
    CConnection(boost::asio::io_service& io) : m_Socket(io), m_nID(-1)
    {
        g_Worker.AdrInsert(m_nID, std::bind1st(std::mem_fun(&CConnection::SendTo), this));
    }
  
    // 날짜시간 메세지를 만든다.
    std::string make_daytime_string()
    {
        //time_t now = time(0);
        //return ctime(&now); // ctime_s 권장. 예제니까 그냥 쓰고 넘어가지만
        return "1234567890";
    }
  
    void handle_Accept(const boost::system::error_code& /*error*/, size_t /*bytes_transferred*/)
    {
        // Recv 대기
		boost::asio::async_read_until(m_Socket,m_RecvBuf,"[!end!]",boost::bind(&CConnection::handle_Read, shared_from_this(),
            boost::asio::placeholders::error,
            boost::asio::placeholders::bytes_transferred));
    }
  
    void handle_Write(const boost::system::error_code& error, size_t /*bytes_transferred*/)
    {
    }
  
    void handle_Read(const boost::system::error_code& error, size_t /*bytes_transferred*/)
    {

        if(!error)  // 0 이 성공 나머지는 오류 플러그
        {
            // 데이터 처리
			if(m_RecvBuf.size())
            {
                std::cout << "Enqueue " << m_nID << "'s"<< std::endl;


                std::stringstream stream;

                stream << "[start]";


				unsigned char msg[9];
				int type=0;

				DEBUGMSG("Packet_Size=%d\n",m_RecvBuf.size());

				boost::shared_array<unsigned char> recvBuf = boost::shared_array<unsigned char>(new unsigned char[102400]);
				memcpy(recvBuf.get(),boost::asio::buffer_cast<const unsigned char*>(m_RecvBuf.data()),m_RecvBuf.size());


				memcpy(msg,recvBuf.get(),8);

				type = atoi((char*)msg);
				msg[8]=9;
				DEBUGMSG("type:%d\n",type);


				printf("Packet_Size=%d\n",m_RecvBuf.size());
				printf("type:%d\n",type);


				// if ( type != 0 )
				// {
				// 	DEBUGMSG("Packet_Size=%d\n",m_RecvBuf.size());
				// 	printf("type:%d\n",type);

				// 	memcpy(msg,recvBuf.get()+8,8);

				// 	type = atoi((char*)msg);
				// 	printf("type:%d\n",type);

				// 	memcpy(msg,recvBuf.get()+16,8);

				// 	type = atoi((char*)msg);
				// 	printf("type:%d\n",type);
				// }


				m_RecvBuf.consume(m_RecvBuf.size());
				
				
				if(type==0)
				{
					requestKeyData req;
					req.nType=type;
					req.nSeq=m_nID;
					req.nId=0;
					req.pData=recvBuf;
					g_Worker.reqQ[m_nID%WORKER_SIZE]->Produce(req);
				}
				else if(type==1)
				{
					std::vector<int> waitQueue;
					std::vector<boost::shared_ptr<MatchCount> > vMatchReducer;
					for(int i=0;i<WORKER_SIZE;i++)
					{
						requestKeyData req;
						req.nType=type;
						req.nSeq=m_nID;
						req.nId=0;
						req.pData=recvBuf;
						g_Worker.reqQ[i]->Produce(req);
						waitQueue.push_back(i);
					}
					int j=0;
					while(true)
					{
						
						DEBUGMSG("wait Queue: %d,%d\n",waitQueue.size(),j);
						if(waitQueue.size()<=0)
							break;
						j=j%waitQueue.size();
						

						responseKeyData res;
						if(g_Worker.resQ[waitQueue[j]]->Consume(res))
						{
							//vMatchReducer
							//DEBUGMSG("--------------------%d\n",res.pData.size());
							if(res.pData.size()>0)
							{
								//DEBUGMSG("--------------------%d\n",res.pData.size());
								for(int i=0;i<res.pData.size();i++)
								{
									vMatchReducer.push_back(res.pData[i]);
									DEBUGMSG("oh Yeah!: %d,%d \n",res.pData[i]->count,res.pData[i]->ID);
									stream << res.pData[i]->ID << "." << res.pData[i]->count << ",";

								}
							}
							waitQueue.erase(waitQueue.begin()+j);
						}
						usleep(50000);
						j++;
					}

					m_sMsg = stream.str();
					int len = strlen(m_sMsg.c_str());

					sprintf((char*)msg,"%08d",len);

					msg[8]=0;
					printf("%s,%d\n",msg,std::string((char*)msg).size());


					boost::asio::async_write(m_Socket, boost::asio::buffer(std::string((char*)msg)),
		            boost::bind(&CConnection::handle_Accept, shared_from_this(),
		            boost::asio::placeholders::error,
		            boost::asio::placeholders::bytes_transferred));


					boost::asio::async_write(m_Socket, boost::asio::buffer(m_sMsg),
		            boost::bind(&CConnection::handle_Accept, shared_from_this(),
		            boost::asio::placeholders::error,
		            boost::asio::placeholders::bytes_transferred));
					//
					DEBUGMSG("End of Search !\n");
				}
				
                //m_RecvBuf.assign(NULL); // 버퍼 초기화
            }
            // Recv 대기
            //m_Socket.async_read_some(boost::asio::buffer(m_RecvBuf), boost::bind(&CConnection::handle_Read, shared_from_this(), boost::asio::placeholders::error, boost::asio::placeholders::bytes_transferred));

        }
        else
		{
            std::cout << m_nID << " Disconnect(Write) : " << error.message() << std::endl;
		}
		
    }
  
    void SendTo(unsigned char *pData)
    {
        std::cout << m_nID << " SendTo" << std::endl;
    }
  
public:
    typedef boost::shared_ptr<CConnection> pointer;
  
    static pointer create(boost::asio::io_service& io)
    {
        return pointer(new CConnection(io));
    }
 
    tcp::socket& socket()
    {
        return m_Socket;
    }
  
    void start(int nID)
    {
        std::cout << "new connect id : "<< nID << " ::: Welcome !" << std::endl;
        m_nID = nID;
  
        // 접속 기념으로 접속 시간 한번 보내주고
        m_sMsg = make_daytime_string();
        boost::asio::async_write(m_Socket, boost::asio::buffer(m_sMsg),
            boost::bind(&CConnection::handle_Accept, shared_from_this(),
            boost::asio::placeholders::error,
            boost::asio::placeholders::bytes_transferred));
    }
};
  
class CTCP_Server
{
private:
    tcp::acceptor m_Acceptor;
    int m_nAcceptCnt;
  
    void WaitAccept()
    {
        ++m_nAcceptCnt;
        CConnection::pointer new_connection =
            CConnection::create(m_Acceptor.get_io_service());
  
        m_Acceptor.async_accept(new_connection->socket(),
            boost::bind(&CTCP_Server::handle_Accept, this, new_connection,
            boost::asio::placeholders::error));
    }
  
    void handle_Accept(CConnection::pointer new_connection, const boost::system::error_code& error)
    {
        if (!error)
        {
            new_connection->start(m_nAcceptCnt);
            WaitAccept();
        }
    }
  
public:
    CTCP_Server(boost::asio::io_service& io) : m_Acceptor(io, tcp::endpoint(tcp::v4(), 58824)), m_nAcceptCnt(0)
    {
        WaitAccept();
    }
};


void swapByteOrder(uint64_t* ull)
{
    *ull = (*ull >> 56) |
          ((*ull<<40) & 0x00FF000000000000) |
          ((*ull<<24) & 0x0000FF0000000000) |
          ((*ull<<8) & 0x000000FF00000000) |
          ((*ull>>8) & 0x00000000FF000000) |
          ((*ull>>24) & 0x0000000000FF0000) |
          ((*ull>>40) & 0x000000000000FF00) |
          (*ull << 56);
}
char *int2bin(uint64_t n, char *buf)
{
    #define BITS (sizeof(n) * CHAR_BIT)

    static char static_buf[BITS + 1];
	//DEBUGMSG("%d\n",BITS);
    int i;

    if (buf == NULL)
        buf = static_buf;

    for (i = BITS - 1; i >= 0; --i) {
        buf[i] = (n & 1) ? '1' : '0';
        n >>= 1;
    }

    buf[BITS] = '\0';
    return buf;

    #undef BITS
}
int POPCNT64(uint64_t v)
{
	unsigned int v1, v2;

	v1 = (unsigned int) (v & 0xFFFFFFFF);
	v1 -= (v1 >> 1) & 0x55555555;
	v1 = (v1 & 0x33333333) + ((v1 >> 2) & 0x33333333);
	v1 = (v1 + (v1 >> 4)) & 0x0F0F0F0F;
	v2 = (unsigned int) (v >> 32);
	v2 -= (v2 >> 1) & 0x55555555;
	v2 = (v2 & 0x33333333) + ((v2 >> 2) & 0x33333333);
	v2 = (v2 + (v2 >> 4)) & 0x0F0F0F0F;
	return ((v1 * 0x01010101) >> 24) + ((v2 * 0x01010101) >> 24);
}
 
uint64_t *findLastPointer(uint64_t *memPool)
{
	uint64_t *pos = memPool;
	while(*pos!=0)
	{
		//DEBUGMSG("---> %p\n",pos - lpvBase);
		pos=pos+(*pos+2);

	}
	//DEBUGMSG("%x,%x,%.2f%\n",pos,memPool,((double)(pos-memPool)/(double)(MEM_SIZE))*100);
	//DEBUGMSG("findLastPointer : %d\n",(pos-memPool));
	DEBUGMSG("memory : %.2f%\n",((double)(pos-memPool)/(double)(MEM_SIZE))*100*8);
	return pos;
}
int insertVec(uint64_t *memPool,int Size,uint64_t *src)
{
	//DEBUGMSG("insertVec!\n");
	uint64_t *lastPointer = findLastPointer(memPool);

	//lastPointer[0]=Size/64;

	memcpy(lastPointer,src,Size+16);

	return 0;
}
int searchVec(uint64_t *memPool,int Size,uint64_t *key,responseKeyData *res)
{
	int kSizeArr[1000];
	int kSize = (int)*key;

	for(int j=0;j<1000;j++)
	{
		kSizeArr[j]=0;		
	}

	for(int j=0;j<kSize/8;j++)
	{
		/*
		if(POPCNT64(mask[j+2])<50)
			DEBUGMSG("%d\n",POPCNT64(mask[j+2]));
		*/
		//key[j+2] = key[j+2]&mask[j+2];
	}
	int count2= 0;
	int maxc= 0;
	int maxv= -1;
	uint64_t *pos = memPool;
	while(*pos!=0)
	{
		//DEBUGMSG("---> %p\n",pos - lpvBase);

		int Size = *pos;

		//DEBUGMSG("%d,%d : %p,%p\n",Size,kSize,pos[2],key[2]);
		
		int count = 0;
		
		for(int i=0;i<(Size/2)/8;i++)
		{
			for(int j=0;j<(kSize/2)/8;j++)
			{
				//DEBUGMSG("%p,%p\n",pos[i+2],key[j+2]);


				//DEBUGMSG("%d\n",POPCNT64(pos[i+2]^key[j+2]));


				//if(__popcnt64(pos[i+2]^key[j+2])<13)
				//{
				//	count++;
				//}

				
				if(_mm_popcnt_u64(pos[(i*2)+1]^key[(j*2)+1])<15)
				{
					if(_mm_popcnt_u64(pos[(i*2)+2]^key[(j*2)+2])<7)
					{
						count++;
						kSizeArr[j]++;
					}
				}

				

				/*
				if(POPCNT64(Size)>300)
				{
					count++;
				}
				*/
				
				/*
				if(POPCNT64(pos[i+2]^key[j+2])<13)
				{
					count++;
				}
				*/

				/*if(pos[i+2]==key[j+2])
				{
					count++;
				}
				*/
			}
			
			if(i==300)
			{
				if(count<1)
				{
					count2++;
					break;
				}
			}
			
		}

		/*
		if((float)count/(Size/8.0f)>0.5&&count>100)
		{
			DEBUGMSG("---------------------------------------------------\n");
			DEBUGMSG("%f,%d,%d\n",(float)count/(Size/8.0f),count,Size/8);
			DEBUGMSG("[%d]\n%s\n",pos[1],vecFileList[pos[1]]);
		}
		*/

		//if(count>((kSize/2)/8)/5)
		//if(count>5)
		if(count>10)
		{
			(*res).pData.push_back(boost::shared_ptr<MatchCount>(new MatchCount(pos[1],count)));
			//(*res).nId=pos[1];
			DEBUGMSG("---------------------------------------------------\n");
			DEBUGMSG("%d\n",count);
			DEBUGMSG("[%d]\n",pos[1]);
		}

		if(maxc<count)
		{
			maxc=count;
			maxv=pos[1];
			DEBUGMSG("count : %d, maxv : %d\n",count,maxv);
		}

		pos=pos+(*pos+2);
	}


	for(int j=0;j<1000;j++)
	{
		if(kSizeArr[j]>1)
		{
			printf("[%d] count : %d\n",j,kSizeArr[j]);
		}
	}


	DEBUGMSG("count2 : %d\n",count2);
	return maxv;

}

bool recv_Insert_Vector(uint64_t *memPool,unsigned char *message)
{
	int imgID;
	int Size;
	unsigned char msg[8];

	memcpy(msg,message+8,8);
	msg[8]=0;
	imgID=atoi((char*)msg);
	DEBUGMSG("imgID:%d\n",imgID);

	memcpy(msg,message+16,8);
	msg[8]=0;
	Size=atoi((char*)msg);
	DEBUGMSG("Size:%d\n",Size);

	uint64_t *tmp = (uint64_t*)malloc(16+Size);
	memset(tmp,0,16+Size);

	memcpy(tmp,message+8,16+Size);
		
	tmp[0]=Size;
	tmp[1]=imgID;
	
	for(int i=0;i<Size/8;i++)
	{
		swapByteOrder(tmp+(i+2));
		//DEBUGMSG("%p\n",(uint64_t)*(tmp+(i+2)));
		//DEBUGMSG("%s\n", int2bin((uint64_t)*(tmp+(i+2)), NULL));
	}

	insertVec(memPool,Size,tmp);
	//memcpy(VecKey,tmp,Size+16);

	free(tmp);
	//sDEBUGMSG(message,"%d",imgID);

	return true;
}
bool recv_Search_Vector(uint64_t *memPool,unsigned char *message,responseKeyData *res)
{

	/*
	int imgID;
	int Size;
	unsigned char msg[8];

	memcpy(msg,message,8);
	imgID=atoi((char*)msg);
	DEBUGMSG("%d",imgID);

	memcpy(msg,message+8,8);
	Size=atoi((char*)msg);

	uint64_t *tmp = (uint64_t*)malloc(16+Size);
	memset(tmp,0,16+Size);

	memcpy(tmp,message,16+Size);
		
	tmp[0]=Size;
	tmp[1]=imgID;
		
	*/
	int Size;
	unsigned char msg[9];
	memcpy(msg,message+8,8);
	msg[8]=0;

	
	Size=atoi((char*)msg);

	//DEBUGMSG("%s\n",message);
	DEBUGMSG("%d\n",Size);

	uint64_t *tmp = (uint64_t*)malloc(16+Size);
	memset(tmp,0,16+Size);

	memcpy(tmp,message,16+Size);

	
	tmp[0]=Size;
	tmp[1]=0;
	
	for(int i=0;i<Size/8;i++)
	{
		swapByteOrder(tmp+(i+2));
		//DEBUGMSG("%p\n",(uint64_t)*(tmp+(i+2)));
		//DEBUGMSG("%s\n", int2bin((uint64_t)*(tmp+(i+2)), NULL));
	}
	int result = searchVec(memPool,(int)*tmp,tmp,res);
	free(tmp);

	return true;
}

void workFunc(int i)
{
	requestKeyData req;
	responseKeyData res;


	uint64_t* mempool = (uint64_t*)malloc(MEM_SIZE);
	memset(mempool,0,MEM_SIZE);

	while(true)
	{
		/*
		if(g_Worker.reqQ[i]->Consume(req))
		{
			DEBUGMSG("1\n");
		}*/

		if(g_Worker.reqQ[i]->Consume(req))
		{
			DEBUGMSG("[Worker %3d], live.\n",i);
			if(req.nType==NET_INSERT_VEC)
			{
				recv_Insert_Vector(mempool,req.pData.get());
				//insertVec(mempool,req.nSize,(uint64_t*)req.pData);
			}
			else if(req.nType==NET_SEARCH_VEC)
			{
			    clock_t start_time, end_time;      // clock_t 

			    start_time = clock();                  // Start_Time

			    res.pData.clear();
				recv_Search_Vector(mempool,req.pData.get(),&res);
				res.nId=req.nId;
				res.nSeq=req.nSeq;
				DEBUGMSG("[OH]%d\n",res.pData.size());
				g_Worker.resQ[i]->Produce(res);


			    end_time = clock();                   // End_Time
			    DEBUGMSG("Time : %f\n", ((double)(end_time-start_time)) / CLOCKS_PER_SEC); 

			}
			else if(req.nType==NET_CHECK_SERVER)
			{
			}

		}
		boost::this_thread::sleep(
			boost::posix_time::milliseconds(50)
		);
	}
}

int main()
{
    try
    {


        boost::thread_group gThread;

		// queue a bunch of "work items"
		for(int i = 0;i<WORKER_SIZE;++i)
		{
			g_Worker.reqQ[i]=boost::shared_ptr<LockFreeQueue<requestKeyData> >(new LockFreeQueue<requestKeyData>());
			g_Worker.resQ[i]=boost::shared_ptr<LockFreeQueue<responseKeyData> >(new LockFreeQueue<responseKeyData>());
			
			gThread.add_thread(new boost::thread(boost::bind(&workFunc, i)));
		}
		///////////////////////////////////.loading server.///////////////////////////////////////////

        boost::asio::io_service io;
  
        CTCP_Server server(io);
  
        boost::thread_group WorkerThread;
        WorkerThread.create_thread(boost::bind(&CWorker::Worker, &g_Worker));
        WorkerThread.add_thread(new boost::thread(boost::bind(&CWorker::Worker, &g_Worker)));
        io.run();
  
		gThread.join_all();
        WorkerThread.join_all();

    }
    catch (std::exception& e)
    {
        std::cerr << e.what() << std::endl;
    }
  
    return 0;
}
