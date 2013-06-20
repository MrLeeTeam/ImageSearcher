import psycopg2
import datetime
import random
import requests
import os
import hashlib
import cv2
import struct
import math
from socket import *
import numpy as np
import sys

from functools import partial


#-------------------------- define ----------------------------#
global NET_INSERT_VEC
global NET_SEARCH_VEC
global NET_CHECK_SERVER

NET_INSERT_VEC=0
NET_SEARCH_VEC=1
NET_CHECK_SERVER=2
#-------------------------- define ----------------------------#

__author__ = 'grace'

def init():
    global con
    con = psycopg2.connect(host="", database="", user="", password="")

    #cursor = con.cursor()
    #cursor.execute("UPDATE blog_meta set crawler_id = 0, last_crawl = %s where b_id = %s", [datetime.datetime.now(), b_id])
    #con.commit()

def getImgPath(v):
    return os.path.join("bucket",v[0],v[1],v[2])

def commitPoint(image_id,result):
    global con

    try:
        cursor = con.cursor()
        cursor.execute("UPDATE blog_image_temp set extract_point='%s' where image_id = %d " % (result,image_id))
        con.commit()

    except:
        print "commit Md5 error"
        if con:
            con.rollback()


    return


def selectURL(bNo):
    global con
    image_url = None
    succ_flag = False

    try:
        cursor = con.cursor()
        cursor.execute("select image_url from blog_image where image_id='"+bNo+"' limit 1")

        record = cursor.fetchone()
        if record:
            image_url = record[0]
            succ_flag = True

    except:
        print "get next image url error"

    return image_url, succ_flag




detector_type = "SIFT"
detector = detector_type



def dotProduct(vec1,vec2):
    return sum(p*q for p,q in zip(vec1, vec2))

def searchCosineDesc(rVec,fFullPath):
    global NET_INSERT_VEC
    global NET_SEARCH_VEC
    global NET_CHECK_SERVER



    image = cv2.imread(fFullPath)

    #outKey2 = open(imgfile+".key2","wb")
    #outMask = open(fName+".mask","wb")

    featureDetector = cv2.FeatureDetector_create(detector)

    gridAdaptedDetector = cv2.GridAdaptedFeatureDetector(featureDetector, 1000)
    descriptorExtractor = cv2.DescriptorExtractor_create(detector)

    scaleX = float(image.shape[1])/450.0

    print "[Set Scale] : (",scaleX,") ",image.shape[1] / scaleX , image.shape[0] / scaleX

    image = cv2.resize(image, (image.shape[1] / scaleX, image.shape[0] / scaleX))


    feature_points = gridAdaptedDetector.detect(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    (feature_points, descriptors) = descriptorExtractor.compute(image, feature_points)

    print len(descriptors)

    datas=""

    for x in descriptors:
        imgVecStr = ""

        for y in range(64):
            if 0 <= np.dot(x,rVec[y]):
                imgVecStr += "0"
            else:
                imgVecStr += "1"

        print imgVecStr

        #print imgVecStr[60:124]

        #if datas=="":
        #print imgVecStr
        data = struct.pack(">Q",int(imgVecStr,2))
        datas += data
        #print imgVecStr

        # imgVecStr = ""
        # for y in x:
        #     if y<(15+30)/2:
        #         imgVecStr +="0"
        #     else:
        #         imgVecStr +="1"
        #
        # data = struct.pack(">Q",int(imgVecStr,2))
        #
        # outKey2.write(data)
    try:
        clientsock = socket(AF_INET, SOCK_STREAM)
        clientsock.connect(('',))
        response = clientsock.recv(10)
        #print response

        sends="{0:08d}".format(NET_SEARCH_VEC)
        sends+="{0:08d}".format(len(datas))
        sends+=datas
        clientsock.send(sends)
        clientsock.send("[!end!]")


        response = clientsock.recv(8)
        print response

        response = clientsock.recv(int(response))
        print response


        if response.find("[start]")==0:
            print "success"
            response = response[7:]
            res_arr = response.split(",")
            res_arr2=[]
            for x in res_arr:
                res_arr2.append(x.split("."))

            sorted(res_arr2,key=lambda s:s[1])

            for y in res_arr2:

                if len(y[0])>0:
                    v,k = selectURL(y[0])
                    if k:
                        print "<img src='"+v+"'/>"+y[1]
        else:
            print "Fail"


    except:
        print response+": Insert Socket Error!!"


    # outKey2.close()
    #outMask.close()


def makeRandomGauss():
    x1=0.0
    x2=0.0
    w=0.0

    while True:
        x1 = 2.0 * (float(random.randint(0,0x7fff))/float(0x7fff)) - 1.0
        x2 = 2.0 * (float(random.randint(0,0x7fff))/float(0x7fff)) - 1.0
        w = x1 * x1 + x2 * x2
        if not ( w >= 1.0  or w == 0):
            break
    return x1 * math.sqrt(-2.0 * math.log( w ) / w)
def makeRandomVector():
    norm=0.0
    cos=[]

    for i in range(128):
        cos.append(makeRandomGauss())
        norm += cos[i]*cos[i]

    norm = math.sqrt(norm)

    for i in range(128):
        cos[i] /= norm
        #print cos[i]

    return cos
def saveRandomVector(i,vec):
    out = open(str(i)+".rv","wb")
    for x in vec:
        #print x
        data = struct.pack("d",x)
        #x = struct.unpack("d",data)
        out.write(data)
# def loadRandomVector():
#     vec =[]
#     paths = os.path.join(".").decode("utf8")
#     for rvfile in os.listdir(paths): #"*" is for subdirectory
#         #print rvfile
#         if rvfile.endswith(".rv"):
#             rvec=[]
#             fin = open(rvfile,"rb")
#             i=0
#             buf = fin.read(8)
#             while buf:
#                 data = struct.unpack("d",buf)

#                 # print data
#                 # if data[0]==vec[i]:
#                 #     print "OK!"
#                 # i+=1

#                 rvec.append(data[0])

#                 buf = fin.read(8)

#             vec.append(rvec)
#             # for x in len(vec):
#             #     out.write(x)
#     return vec
# def loadRandomVector():
#     vec =[]
#     paths = os.path.join(".").decode("utf8")
#     for rvfile in range(64):
#         rvfile = str(rvfile)+".rv"
#         rvec=[]
#         fin = open(rvfile,"rb")
#         i=0
#         buf = fin.read(8)
#         while buf:
#             data = struct.unpack("d",buf)

#             # print data
#             # if data[0]==vec[i]:
#             #     print "OK!"
#             # i+=1

#             rvec.append(data[0])

#             buf = fin.read(8)

#         vec.append(rvec)
#         # for x in len(vec):
#         #     out.write(x)
#     return vec



def loadRandomVector():
    vec =[]
    paths = os.path.join(".").decode("utf8")
    for rvfile in range(64):
        rvfile = str(rvfile)+".rv"
        rvec=[]
        fin = open(rvfile,"rb")
        i=0
        buf = fin.read(8)
        while buf:
            data = struct.unpack("d",buf)

            # print data
            # if data[0]==vec[i]:
            #     print "OK!"
            # i+=1

            rvec.append(data[0])

            buf = fin.read(8)

        vec.append(rvec)
        # for x in len(vec):
        #     out.write(x)
    return vec





init()

# for x in range(64):
#     vec = makeRandomVector()
#     saveRandomVector(x,vec)

lvec = loadRandomVector()


#insertCosineDesc(lvec)

if len(sys.argv) > 1:
     searchCosineDesc(lvec,sys.argv[1])
else:
     print "plz input imagePath"
#searchCosineDesc(lvec,"bucket/d/1/3/d133911cc72a2dc311e8f574a043bd80")

'''


bucket/d/1/3/d133911cc72a2dc311e8f574a043bd80
bucket/d/1/3/d13846932fee7251c50e8e0b262c6278
bucket/d/1/3/d139a9349ea26549133dc71f8eb9d5e2
bucket/d/1/3/d136e369efd93501b987884c8a1177b5
bucket/d/1/3/d13c20682d93c134f235cc3c17aba869



bucket/0/a/4/0a4acb7f0c57e5b98db96abd5905bc39
bucket/d/5/b/d5b0e167c66dbbb5cdf2d434940e4ae3
bucket/d/8/4/d8411046f7897f2d5fa1c86291d41bca

vec/bucket/1/6/f/16fe240c57f533a78912a245efecab23.vec

d2b24edc61713217c3d9f0123c.vec
743
1234567890
bucket/1/0/b
vec/bucket/1/0/b/10b6cc578c9f65ea00cbd6cdac2b28d6.vec
414
1234567890
bucket/4/5/3
vec/bucket/4/5/3/45331049c623cdaeea33ca3c3dc47f23.vec
885
1234567890
bucket/b/2/7
vec/bucket/b/2/7/b272b30d995aeb20d94df82f5aeecfc9.vec
806
1234567890
bucket/c/a/1
vec/bucket/c/a/1/ca182ac2e1b6fd6bb1efb161e24871c7.vec
761
1234567890
bucket/1/2/3
vec/bucket/1/2/3/12351f0d024e190e0dfe203df1a2766b.vec
660
1234567890


'''
