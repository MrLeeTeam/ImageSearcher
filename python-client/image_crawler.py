import psycopg2
import datetime
import random
import requests
import os
import hashlib
from functools import partial
import StringIO
import struct


__author__ = 'grace'

def init():
    global con
    con = psycopg2.connect(host="", database="", user="", password="")

    #cursor = con.cursor()
    #cursor.execute("UPDATE blog_meta set crawler_id = 0, last_crawl = %s where b_id = %s", [datetime.datetime.now(), b_id])
    #con.commit()

def getImageInfo(data):
    data = str(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
          and (data[12:16] == 'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # handle JPEGs
    elif (size >= 2) and data.startswith('\377\330'):
        content_type = 'image/jpeg'
        jpeg = StringIO.StringIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            while (b and ord(b) != 0xDA):
                while (ord(b) != 0xFF): b = jpeg.read(1)
                while (ord(b) == 0xFF): b = jpeg.read(1)
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    jpeg.read(3)
                    h, w = struct.unpack(">HH", jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
                b = jpeg.read(1)
            width = int(w)
            height = int(h)
        except struct.error:
            pass
        except ValueError:
            pass

    return content_type, width, height


def image_downloader(url):
    random.seed()

    dirs="tmp"
    if not os.path.isdir(dirs):
        os.makedirs(dirs)

    fname=str(int(random.random()*10000000000))
    path = os.path.join(dirs,fname)

    try:

        r = requests.get(url,timeout=0.5)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                is_first=True
                for chunk in r.iter_content(1024):
                    if is_first:
                        tp,width,height= getImageInfo(chunk)
                        if width<100 or height < 100:
                            return None

                    is_first=False
                    f.write(chunk)
    except:
        return None

    return path

def getMd5sum(fname):
    with open(fname, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def getMd5Path(v):
    return os.path.join("bucket",v[0],v[1],v[2])

def movePath(tmp,path,fname):
    if not os.path.isdir(path):
        os.makedirs(path)

    fPath = os.path.join(path,fname)

    if not os.path.isfile(fPath):
        os.rename(tmp,fPath)

    if os.path.isfile(tmp):
        os.remove(tmp)

    return

def commitMd5(image_id,md5Value,result):
    global con


    try:
        cursor = con.cursor()
        cursor.execute("UPDATE blog_image set image_hash = '%s',stored_flag = '%s' where image_id = %d " % (md5Value,result,image_id))
        con.commit()

    except:
        print "commit Md5 error"
        if con:
            con.rollback()


    return

def getNextImageUrl():
    global con

    image_id = None
    image_url = None
    succ_flag = False
    try:
        cursor = con.cursor()
        cursor.execute("select image_id,image_url from blog_image where stored_flag='f' limit 1")
        record = cursor.fetchone()
        if record:
            image_id,image_url = record
            succ_flag = True
            cursor.execute("UPDATE blog_image set stored_flag = 't' where image_id = %d " % (image_id))
            con.commit()

    except:
        print "get next image url error"
        if con:
            con.rollback()

    return image_id,image_url, succ_flag

init()
while True:
    #-----------------------------------------
    result ='x'
    md5Value = ""
    #-----------------------------------------
    try:
        image_id,image_url,succ_flag = getNextImageUrl()
        print image_id, "," ,image_url,",",succ_flag
        if succ_flag:
            tmpPath = image_downloader(image_url)
            if tmpPath !=None:
                result = 't'
                md5Value = getMd5sum(tmpPath)
                md5Path = getMd5Path(md5Value)

                movePath(tmpPath,md5Path,md5Value)
                print md5Value

            commitMd5(image_id,md5Value,result)
        else:
            print "finish!!"
    except:
        print "error!"

