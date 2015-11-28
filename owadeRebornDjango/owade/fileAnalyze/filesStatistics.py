
#############################################################################
##                                                                         ##
## This file is part of Owade : www.owade.org                              ##
## Offline Windows Analyzer and Data Extractor                             ##
##                                                                         ##
##  Authors:                                                               ##
##  Elie Bursztein <owade@elie.im>                                         ##
##  Ivan Fontarensky <ivan.fontarensky@cassidian.com>                      ##
##  Matthieu Martin <matthieu.mar+owade@gmail.com>                         ##
##  Jean-Michel Picod <jean-michel.picod@cassidian.com>                    ##
##                                                                         ##
## This program is distributed under GPLv3 licence (see LICENCE.txt)       ##
##                                                                         ##
#############################################################################
__author__="ashe"
__date__ ="$Jun 28, 2011 6:48:12 PM$"

from owade.models import *
from owade.process import Process

class FilesStatistics(Process):
    def __init__(self, internLog, terminalLog, hardDrive, overWrite):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive_ = hardDrive
        self.overWrite_ = overWrite

    def run(self):
        self.internLog_.addLog("File Analysis process launched", 1)
        for partition in Partition.objects.filter(harddrive=self.hardDrive_):
            if not self.overWriteCategory(partition, self.__class__.__name__, self.overWrite_):
                continue
            fileInfos = FileInfo.objects.filter(partition=partition)
            files = File.objects.filter(fileinfo__in=fileInfos)
            values = {}
            values['Number of files'] = fileInfos.count()
            values['Number of different files'] = files.count()
            movies = files.filter(extension__in=self.EXT_MOVIES)
            values['Number of videos'] = movies.count()
            images = files.filter(extension__in=self.EXT_IMAGES)
            values['Number of images'] = images.count()
            musics = files.filter(extension__in=self.EXT_MUSICS)
            values['Number of musics'] = musics.count()
            self.updateDbGenericDic({self.__class__.__name__:values}, partition)

    EXT_MOVIES=['avi', 'mpeg', 'mpg', 'mov', 'qt', 'wmv', 'rm', 'mp4', 'ogm', 'mkv']
    EXT_IMAGES=['gif', 'bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'psd']
    EXT_MUSICS=['wav', 'aif', 'mp3', 'mid', 'ogg', 'flac', 'wma']

    hardDrive_ = None
    overWrite_ = None