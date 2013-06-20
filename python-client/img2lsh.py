# *encoding:utf8-*
__author__ = 'grace'

import os
import cv2
import struct
import random
import math
from socket import *


detector_type = "SIFT"
detector = detector_type


def insertPlainDesc():
    #paths = os.path.join("\\..\\").decode("utf8")
    paths = "C:\\Users\\grace\\Desktop\\root\\grace\\work\\[2013]soma\\movie_image.csv\\imgs\\"
    for imgfile in os.listdir(paths): #"*" is for subdirectory
        try:
            if imgfile.endswith(".jpg"):
                image = cv2.imread(paths+imgfile)
                out = open(paths+imgfile+".vec","wb")
                print imgfile

                if image==None:
                    continue

                featureDetector = cv2.FeatureDetector_create(detector)

                gridAdaptedDetector = cv2.GridAdaptedFeatureDetector(featureDetector, 1000)
                descriptorExtractor = cv2.DescriptorExtractor_create(detector)

                feature_points = gridAdaptedDetector.detect(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
                (feature_points, descriptors) = descriptorExtractor.compute(image, feature_points)



                # descriptorExtractor = cv2.DescriptorExtractor_create(detector)
                # feature_points = featureDetector.detect(image) #cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # (feature_points, descriptors) = descriptorExtractor.compute(image, feature_points)

                print len(descriptors)

                for x in descriptors:
                    imgVecStr = ""
                    for y in x:
                        if y<(15+30)/2:
                            imgVecStr +="0"
                        else:
                            imgVecStr +="1"

                    #print imgVecStr[60:124]
                    data = struct.pack(">Q",int(imgVecStr[60:124],2))
                    out.write(data)
                out.close()

        except:
            print "error!"
def searchPlainDesc():
    paths = os.path.join(".\\").decode("utf8")
    for imgfile in os.listdir(paths): #"*" is for subdirectory
        if imgfile.endswith(".jpg"):
            image = cv2.imread(imgfile)

            outKey = open(imgfile+".key","wb")
            outMask = open(imgfile+".mask","wb")
            print imgfile

            featureDetector = cv2.FeatureDetector_create(detector)

            gridAdaptedDetector = cv2.GridAdaptedFeatureDetector(featureDetector, 1000)
            descriptorExtractor = cv2.DescriptorExtractor_create(detector)

            feature_points = gridAdaptedDetector.detect(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
            (feature_points, descriptors) = descriptorExtractor.compute(image, feature_points)


            for x in descriptors:
                imgKeyStr = ""
                imgMaskStr = ""

                for y in x:
                    if y<(15+30)/2:
                        imgKeyStr +="0"
                    else:
                        imgKeyStr +="1"

                    if y>=15 and y<30:
                        imgMaskStr += "0"
                    else:
                        imgMaskStr += "1"

                #print imgKeyStr[60:124]
                #print imgMaskStr[60:124]
                data = struct.pack(">Q",int(imgKeyStr[60:124],2))
                outKey.write(data)

                data = struct.pack(">Q",int(imgMaskStr[60:124],2))
                outMask.write(data)
            outKey.close()
            outMask.close()


def dotProduct(vec1,vec2):
    return sum(p*q for p,q in zip(vec1, vec2))
def insertCosineDesc(rVec):
    #paths = os.path.join("\\..\\").decode("utf8")
    paths = "C:\\Users\\grace\\Desktop\\root\\grace\\work\\[2013]soma\\movie_image.csv\\imgs\\"
    for imgfile in os.listdir(paths): #"*" is for subdirectory
        try:
            if imgfile.endswith(".jpg"):
                image = cv2.imread(paths+imgfile)
                out = open(paths+imgfile+".vec","wb")
                print imgfile

                if image==None:
                    continue

                featureDetector = cv2.FeatureDetector_create(detector)

                gridAdaptedDetector = cv2.GridAdaptedFeatureDetector(featureDetector, 1000)
                descriptorExtractor = cv2.DescriptorExtractor_create(detector)

                feature_points = gridAdaptedDetector.detect(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
                (feature_points, descriptors) = descriptorExtractor.compute(image, feature_points)



                # descriptorExtractor = cv2.DescriptorExtractor_create(detector)
                # feature_points = featureDetector.detect(image) #cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # (feature_points, descriptors) = descriptorExtractor.compute(image, feature_points)

                print len(descriptors)

                for x in descriptors:
                    imgVecStr = ""
                    # for y in x:
                    #     if y<(15+30)/2:
                    #         imgVecStr +="0"
                    #     else:
                    #         imgVecStr +="1"
                    for y in range(64):
                        if 0 <= dotProduct(x,rVec[y]):
                            imgVecStr += "0"
                        else:
                            imgVecStr += "1"

                    #print imgVecStr

                    #print imgVecStr[60:124]
                    data = struct.pack(">Q",int(imgVecStr,2))
                    out.write(data)
                out.close()

        except:
            print "error!"
def searchCosineDesc(rVec):
    paths = os.path.join(".\\").decode("utf8")
    for imgfile in os.listdir(paths): #"*" is for subdirectory
        if imgfile.endswith(".jpg"):
            image = cv2.imread(imgfile)

            outKey = open(imgfile+".key","wb")
            #outKey2 = open(imgfile+".key2","wb")
            outMask = open(imgfile+".mask","wb")
            print imgfile

            featureDetector = cv2.FeatureDetector_create(detector)

            gridAdaptedDetector = cv2.GridAdaptedFeatureDetector(featureDetector, 1000)
            descriptorExtractor = cv2.DescriptorExtractor_create(detector)

            feature_points = gridAdaptedDetector.detect(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
            (feature_points, descriptors) = descriptorExtractor.compute(image, feature_points)

            print len(descriptors)

            datas=""

            for x in descriptors:
                imgVecStr = ""

                for y in range(64):
                    if 0 <= dotProduct(x,rVec[y]):
                        imgVecStr += "0"
                    else:
                        imgVecStr += "1"

                #print imgVecStr

                #print imgVecStr[60:124]

                #if datas=="":
                #print imgVecStr
                data = struct.pack(">Q",int(imgVecStr,2))
                outKey.write(data)


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
            # clientsock = socket(AF_INET, SOCK_STREAM)
            # clientsock.connect(('127.0.0.1',58824))
            # clientsock.send("{0:08d}".format(len(datas)))
            # clientsock.send(datas)
            #print clientsock.recv(4)
            #clientsock.close()


            outKey.close()
            # outKey2.close()
            outMask.close()


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
def loadRandomVector():
    vec =[]
    paths = os.path.join(".\\").decode("utf8")
    for rvfile in os.listdir(paths): #"*" is for subdirectory
        if rvfile.endswith(".rv"):
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
searchCosineDesc(lvec)


#clientsock.send('22')


#
# for x in range(len(vec)):
#     if vec != lvec:
#         print "error!"
#         exit;
#     else:
#         print "OK!"
#

#searchDesc()
#insertDesc()
