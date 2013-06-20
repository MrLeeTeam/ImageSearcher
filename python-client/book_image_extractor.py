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
import time

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

def getImgNextId():
    global con

    image_id = None
    image_hash = None
    succ_flag = False

    try:
        cursor = con.cursor()
        cursor.execute("select image_id from book_image where stored_flag='t' limit 1")

        record = cursor.fetchone()
        if record:
            image_id = record[0]
            succ_flag = True

            cursor.execute("UPDATE book_image set stored_flag='x' where image_id = %d " % (image_id))
            con.commit()

    except:
        print "get next image url error"
        if con:
            con.rollback()

    return image_id, succ_flag



def getMd5sum(image_id):

    d=hashlib.md5()
    d.update(str(image_id))
    return d.hexdigest()

    '''
    with open(fname, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()
    '''
def getMd5Path(v):
    return os.path.join("book_bucket",v[0],v[1],v[2])


def extractPoint():

    return
def commitPoint(image_id,result):
    global con

    try:
        cursor = con.cursor()
        cursor.execute("UPDATE blog_image set extract_point='%s' where image_id = %d " % (result,image_id))
        con.commit()

    except:
        print "commit Md5 error"
        if con:
            con.rollback()


    return


detector_type = "SIFT"
detector = detector_type


def dotProduct(vec1,vec2):
    return sum(p*q for p,q in zip(vec1, vec2))

def insertCosineDesc(rVec,fPath,fName,imgID):
    global NET_INSERT_VEC
    global NET_SEARCH_VEC
    global NET_CHECK_SERVER

    vecPath = os.path.join("book_vec",fPath)
    vecFullPath = os.path.join(vecPath,fName+".vec")
    if not os.path.isdir(vecPath):
        os.makedirs(vecPath)

    fFullPath = os.path.join(fPath,fName)

    try:
        os.system("convert "+fFullPath+" "+fFullPath+".jpg")
    except:
        print "error@_@"

    fFullPath = fFullPath+".jpg"

    print fFullPath
    image = cv2.imread(fFullPath)
    print vecFullPath
    outVec = open(vecFullPath,"wb")
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

    data = struct.pack(">Q",imgID)
    #outVec.write(data)

    for x in descriptors:
        imgVecStr = ""

        for y in range(128):
            if 0 <= np.dot(x,rVec[y]):
                imgVecStr += "0"
            else:
                imgVecStr += "1"

        #print imgVecStr

        #print imgVecStr[60:124]

        #if datas=="":
        #print imgVecStr
        data = struct.pack(">Q",int(imgVecStr[0:64],2))
        data += struct.pack(">Q",int(imgVecStr[64:128],2))
        #outVec.write(data)
        datas += data

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

    sends="{0:08d}".format(NET_INSERT_VEC)
    sends+="{0:08d}".format(imgID)
    sends+="{0:08d}".format(len(datas))
    sends+=datas
    outVec.write(sends)
    outVec.close()

    try:
        clientsock = socket(AF_INET, SOCK_STREAM)
        clientsock.connect(('',))

        response = clientsock.recv(10)
        print response
        # clientsock.send("{0:08d}".format(NET_INSERT_VEC))
        # clientsock.send("{0:08d}".format(imgID))
        # clientsock.send("{0:08d}".format(len(datas)))
        # clientsock.send(datas)


        clientsock.send(sends)
        clientsock.send("[!end!]")
    	
    	#need sync!

    except:
        print str(imgID)+": Insert Socket Error!!"


    
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

def loadRandomVector():
    vec =[]
    paths = os.path.join(".").decode("utf8")
    for rvfile in range(128):
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




# for x in range(64):
#     vec = makeRandomVector()
#     saveRandomVector(x,vec)

lvec = loadRandomVector()

#insertCosineDesc(lvec)


init()

while True:


    try:

        result = 'x'

        image_id,succ_flag = getImgNextId()
        if succ_flag:
            image_hash = getMd5sum(image_id)
            print image_id
            print image_hash
            tmpPath = getMd5Path(image_hash)
            print tmpPath
            if tmpPath !=None:
                result = 't'
                insertCosineDesc(lvec,tmpPath,image_hash,image_id)


            #commitPoint(image_id,result)
        else:
            print "finish!!"

    except:
        print "error!"

