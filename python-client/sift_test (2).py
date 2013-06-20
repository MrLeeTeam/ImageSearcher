# *encoding:utf8-*
import os
import cv2
from pylab import *
import math
import time

__author__ = 'grace'

detector_type = "SIFT"
detector = detector_type

desc_list = []
file_name = []

dist = []

sum_dist = []
sum_count = []

max_dist = []

for x in range(256):
    sum_dist.append(0)
    sum_count.append(0)
    max_dist.append(0)

for x in range(256):
    dist.append(0)
#
# def cal_distance(desc1,desc2):
#     K=0.2
#     sum=0
#     for x in range(0,len(desc1)):
#         #print (desc1[x]**0.5)-(desc2[x]**0.5)
#         #차이가 3 미만일때, 어디가 제일 많이 차이나는지 인덳스를 찾아보자!
#         # x1 = math.log(desc1[x]+1)
#         # x1 = (x1+K)/K
#         #
#         # y1 = math.log(desc2[x]+1)
#         # y1 = (y1+K)/K
#         if abs((desc1[x])-(desc2[x]))>15:
#         # if abs(x1-y1)>4:
#             return 1000
#         sum += abs(desc1[x]-desc2[x])
#
#     return sum ** 0.5


def cal_distance(desc1,desc2):
    K=0.2
    sum=0
    for x in range(0,len(desc1)):
        #print (desc1[x]**0.5)-(desc2[x]**0.5)
        #차이가 3 미만일때, 어디가 제일 많이 차이나는지 인덳스를 찾아보자!
        # x1 = math.log(desc1[x]+1)
        # x1 = (x1+K)/K
        #
        # y1 = math.log(desc2[x]+1)
        # y1 = (y1+K)/K
        # res1=""
        # res2=""
        # if desc1[x]<(15+30)/2:
        #     res1="0"
        # else:
        #     res1="1"
        #
        #
        # if desc2[x]<15:
        #     res2="0"
        # elif desc2[x]<30:
        #     res2="_"
        # else:
        #     res2="1"
        #
        #
        # #if abs((desc1[x])-(desc2[x]))>15:
        # # if abs(x1-y1)>4:
        # if not(res2=="_" or res1==res2):
        #     return 1000
        sum += (desc1[x]-desc2[x])*(desc1[x]-desc2[x])

    return sum ** 0.5



def sum_distance(desc1,desc2):
    K=0.2
    sum=0
    for x in range(0,len(desc1)):
        #print (desc1[x]**0.5)-(desc2[x]**0.5)
        #차이가 3 미만일때, 어디가 제일 많이 차이나는지 인덳스를 찾아보자!

        #if abs((desc1[x]**0.5)-(desc2[x]**0.5))>1.5:
        sum_dist[int(abs((desc1[x])))] +=abs(desc1[x]-desc2[x])
        sum_count[int(abs((desc1[x])))] +=1

        max_dist[int(desc1[x])] = max(max_dist[int(desc1[x])],abs(desc1[x]-desc2[x]))
    return


def desc_match():
    for x in range(0,len(desc_list)):
    #     (feature_points1, descriptors1) = desc_list[x]
    #     for x1 in range(0,len(descriptors1)):
    #         for y1 in descriptors1[x1]:
    #             #print y1
    #             #y1 = int(y1/10)
    #             y1 = y1**0.5
    #             #dist[int(y1)]+=1 + y1*2
    #             dist[int(y1)]+=1
    # K = 0.2
    #
    # y1 = math.log(1+1)
    # y1 = (y1+K)/K
    # print y1
    # y1 = math.log(3+1)
    # y1 = (y1+K)/K
    # print y1
    #
    #
    # y1 = math.log(100+1)
    # y1 = (y1+K)/K
    # print y1
    #
    # y1 = math.log(200+1)
    # y1 = (y1+K)/K
    # print y1
    #


    # K = 0.2
    # for x in range(0,len(desc_list)):
    #     (feature_points1, descriptors1) = desc_list[x]
    #     for x1 in range(0,len(descriptors1)):
    #         for y1 in descriptors1[x1]:
    #             #print y1
    #             y1 = int(y1/2)
    #             # y1 = math.log(y1+1)
    #             # y1 = (y1+K)/K
    #             #y1 = math.log(y1+1)
    #             #y1 = (y1+K)/K
    #             #print y1
    #             #dist[int(y1)]+=1 + y1*2
    #             dist[int(y1)]+=1


    #
    # tt=0
    # tc=0
    # for x in range(0,len(desc_list)):
    #     (feature_points1, descriptors1) = desc_list[x]
    #     for x1 in range(0,len(descriptors1)):
    #         tc+=1
    #         v0=0
    #         v1=0
    #         v2=0
    #
    #         for y1 in descriptors1[x1]:
    #             #print y1
    #             #y1 = int(y1/10)
    #             #y1 = y1**0.5
    #             if y1 < 15:
    #                 print "0",
    #                 v0+=1
    #             elif y1 < 30:
    #                 print "_",
    #                 v1+=1
    #             else:
    #                 print "1",
    #                 v2+=1
    #                 #print y1
    #                 #dist[int(y1)]+=1
    #         print ""
    #
    #         #print str(v0)+","+str(v1)+","+str(v2)+""
    #         tt+=v1

    #print str(tt/tc)


        for y in range(0,len(desc_list)):
            if x==y: continue

            (feature_points1, descriptors1) = desc_list[x]
            (feature_points2, descriptors2) = desc_list[y]
            # print len(feature_points),
            # print ",",
            # print len(descriptors)
            mink = -1
            minv = 9999

            cc=0

            for x1 in range(0,len(descriptors1)):
                for x2 in range(0,len(descriptors2)):
                    val = cal_distance(descriptors1[x1],descriptors2[x2])
                    # if val < 1000:
                    #     sum_distance(descriptors1[x1],descriptors2[x2])
                    if minv > val:
                        minv = val
                        mink = x2
                    if val <= 100:
                        cc +=1
            if minv >= 100:
                continue

            print file_name[x],
            print ":",
            print file_name[y],
            print "->",
            print cc

            print minv



        # for y in range(x+1,len(desc_list)):
        #     print x,
        #     print ",",
        #     print y



paths = os.path.join(".\\").decode("utf8")
for imgfile in os.listdir(paths): #"*" is for subdirectory
    if imgfile.endswith(".jpg"):
        image = cv2.imread(imgfile)

        featureDetector = cv2.FeatureDetector_create(detector)
        #
        # gridAdaptedDetector = cv2.GridAdaptedFeatureDetector(featureDetector, 500)
        # descriptorExtractor = cv2.DescriptorExtractor_create(detector)
        #
        # feature_points = gridAdaptedDetector.detect(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        # (feature_points, descriptors) = descriptorExtractor.compute(image, feature_points)
        #


        descriptorExtractor = cv2.DescriptorExtractor_create(detector)
        feature_points = featureDetector.detect(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        (feature_points, descriptors) = descriptorExtractor.compute(image, feature_points)


        for feature in feature_points:
            x, y = feature.pt

            center = (int(x), int(y))
            size = int(feature.size)
            cv2.circle(image, center, size, (0,255,0))


        file_name.append(imgfile)
        desc_list.append((feature_points, descriptors))


        #cv2.imshow("aa",image)


        #cv2.waitKey()


desc_match()


#
# total = 0
# for idx,x in enumerate(dist):
#     total+=x
#     print "idx:"+ str(idx) + "," +str(x)
#
# count = 0
# for idx,x in enumerate(dist):
#     count+=x
#     print str(idx) + "," + str(float(count)/float(total))
#
#
# #print sum_dist
#
#
# #
# # for idx, x in enumerate(sum_count):
# #     if x==0:
# #         print "0 : 0"
# #     else:
# #         print str(idx) + " : " + str(sum_dist[idx]/x) + " , " + str(max_dist[idx])
# #
#
#
#
# plot(range(1,len(dist)+1), dist, 'ro')
# axis([0, len(dist), 0, max(dist)])
# #savefig('secondfig.png')
# show()
#
