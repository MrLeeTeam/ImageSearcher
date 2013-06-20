#pragma once

#include <boost/atomic.hpp>
#include <boost/thread.hpp>

template <typename T>
class LockFreeQueue
{
private:
	boost::mutex mutex;
    struct Node
    {
        Node(T val) : value(val), next(NULL) { }
        T value;
        Node* next;
    };
    Node* first; // for producer only
    boost::atomic<Node*> divider;  // shared
    boost::atomic<Node*> last; // shared

public:
    LockFreeQueue()
    {
        first = new Node(T());
        divider = first;
        last= first;
    }

    ~LockFreeQueue()
    {
        while(first != NULL) // release the list
        {
            Node* tmp = first;
            first = tmp->next;
            delete tmp;
        }
    }

    void Produce(const T& t)
    {
		mutex.lock();
        last.load()->next = new Node(t); // add the new item
        last = last.load()->next;
        while(first != divider) // trim unused nodes
        {
            Node* tmp = first;
            first = first->next;
            delete tmp;
        }
		mutex.unlock();
    }

    bool Consume(T& result)
    {
		mutex.lock();
        if(divider != last) // if queue is nonempty
        {
            result = divider.load()->next->value; // C: copy it back
            divider = divider.load()->next;
            mutex.unlock();
			return true;  // and report success
        }
        mutex.unlock();
		return false;  // else report empty
		
    }
};
