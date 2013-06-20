g++ -o server -I/tmp/boost_1_53_0 -L/tmp/boost_1_53_0/stage server.cpp -lboost_system -lboost_thread -std=gnu++0x -m64 -msse4.2 -O3
