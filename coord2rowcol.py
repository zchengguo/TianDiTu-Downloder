import math
import os
from PIL import Image
from PIL import ImageFile
from config import *

ImageFile.LOAD_TRUNCATED_IMAGES = True


class Coord2RowCol(object):
    def __init__(self, level=16, maptype=1, grid="all"):
        self._tilesize = 256
        self._originX = -180
        self._originY = 90
        self._mapUrl = MAPURL
        self._satilateUrl = MAPURL
        self._grid = grid
        self._fileList = []

        self._mapleveldic = MAPRESOLUTION

        if maptype == 2:
            self._mapUrl = self._satilateUrl
        self._level = level
        self._strTmpDir = os.getcwd() + "/" + str(self._level) + "/"
        if not os.path.exists(self._strTmpDir):
            os.mkdir(self._strTmpDir)
        try:
            self._resolution = self._mapleveldic[self._level][1]
        except:
            print("地图级别设置错误：支持8-18级")

    def longitudeLatitude2ColRow(self, longitude, latitude):
        col = int(math.floor((longitude - self._originX) / (self._resolution * self._tilesize)))
        row = int(math.floor((self._originY - latitude) / (self._resolution * self._tilesize)))
        return col, row

    def coordtoQuant(self, topleftLongitude, topleftLatutide, bottomrightLongitude, bottomrightLatitude):
        topLeftCol, toplefRow = self.longitudeLatitude2ColRow(topleftLongitude, topleftLatutide)
        boRightCol, boRightRow = self.longitudeLatitude2ColRow(bottomrightLongitude, bottomrightLatitude)

        minCol = topLeftCol if topLeftCol < boRightCol else boRightCol
        minRow = toplefRow if toplefRow < boRightRow else boRightRow
        maxCol = topLeftCol if topLeftCol >= boRightCol else boRightCol
        maxRow = toplefRow if toplefRow >= boRightRow else boRightRow

        # modify in 20161124, correct the coordinate problem,switch the Col and Row
        self._topleftx = minCol
        self._toplefty = minRow

        urls = {}
        for i in range(minRow, maxRow + 1):
            imagerow = []
            for j in range(minCol, maxCol + 1):
                filename = self._strTmpDir + str(i) + "-" + str(j)
                imagerow.append(filename+".png")
                url = "".join([self._mapUrl, str(self._level), "/", str(i), "/", str(j)])
                urls[filename] = url
            self._fileList.append(imagerow)

        return urls

    def mergemap(self, imgtype=TILETYPE):
        if not self._fileList:
           return

        #_filetype = ".jpg"
        _filetype = TILETYPE
        _coordfiletype = ".jpw"

        if imgtype == 'tiff':
            _filetype = ".tif"
            _coordfiletype = ".tfw"

        imagewidth = len( self._fileList[0]) * self._tilesize
        imageheight = len( self._fileList) * self._tilesize

        if os.path.exists(os.getcwd() + "/" + "result/" + str(self._level) + "/" + str(self._grid) +_filetype):
            return

        try:
            map = Image.new("RGBA", (imagewidth, imageheight), (0, 0, 0))
            if not os.path.exists(os.getcwd() + "/" + "result/" + str(self._level)):
                os.mkdir(os.getcwd() + "/" + "result/" + str(self._level))

            for i in range(0, len(self._fileList)):
                for j in range(0, len(self._fileList[0])):
                    try:
                        im = Image.open(self._fileList[i][j])
                    except:
                        im = Image.new("RGBA", (self._tilesize, self._tilesize), (255, 255, 255, 255))
                    map.paste(im, (j * self._tilesize, i * self._tilesize))
            map.save(os.getcwd() + "/" + "result/" + str(self._level) + "/" + str(self._grid) +_filetype)

            longitude = self._topleftx * self._tilesize * self._resolution + self._originX
            latitude = self._originY - self._toplefty * self._tilesize * self._resolution
            fp = open(os.getcwd() + "/" + "result/" + str(self._level) + "/" + str(self._grid) + _coordfiletype, 'w')
            fp.write(str(self._resolution))
            fp.write("\n")
            fp.write("0")
            fp.write("\n")
            fp.write("0")
            fp.write("\n")
            fp.write(str(-self._resolution))
            fp.write("\n")
            fp.write(str(longitude))
            fp.write("\n")
            fp.write(str(latitude))
            fp.close()
        except Exception as e:
            print("拼接图像出错")
            print(e)


