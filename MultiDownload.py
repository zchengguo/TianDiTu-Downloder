import shapefile

from coord2rowcol import Coord2RowCol
import asynMapLoader
import multiprocessing
import os
import time
from config import *

def work(records,f):
    for record in records:
        minx = record[1]
        maxx = record[2]
        miny = record[3]
        maxy = record[4]

        ml = Coord2RowCol(level=f, maptype=2, grid=record[0])
        listUrl = ml.coordtoQuant(minx, miny, maxx, maxy)
        try:
            asynMapLoader.main(listUrl, str(os.getpid())+":"+str(record[0]))
            ml.mergemap()
        except Exception as e:
            with open('download_log.txt', 'a') as logfile:
                logfile.write(str(record[0]) + "|" + str(e) + "\n")
            print(e)

if __name__ == "__main__":

    start = time.clock()
    MAXPROCESS = MULTIPROCESS#5
    sf = shapefile.Reader(SHAPEFILE)

    records = sf.records()
    print(len(records))
    _num_re = len(records)
    
    maplv = MAPLEVEL #设定下载级别
    for f in maplv:
        pool = multiprocessing.Pool(processes=MAXPROCESS)
        perProcess = int(_num_re/MAXPROCESS)
        print(perProcess)

        for i in range(MAXPROCESS):
        #for i in range(_num_re): --zcg
            a=records[i*perProcess: (i+1)*perProcess]
            print(i)
            print(a)
            tmp_re = records[i*perProcess: (i+1)*perProcess]
            # wk = multiprocessing.Process(target=work, args=(tmp_re,))
            # wk.start()
            pool.apply_async(work, (tmp_re,f,))

        laskrec = records[(MAXPROCESS*perProcess):]
        # lastwk = multiprocessing.Process(target=work, args=(laskrec,))
        # lastwk.start()
        pool.apply_async(work, (laskrec,))

        # pool.apply_async(work, (records[:perProcess],))
        # pool.apply_async(work, (records[perProcess:],))

        pool.close()
        pool.join()

    end = time.clock()
    print("The function run time is : %.03f seconds" % (end - start))

