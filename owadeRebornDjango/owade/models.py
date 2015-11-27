from django.db import models

# Create your models here.
##################################################
#### File Extraction
##################################################

## Represents an hard drive in the database
from owade.constants import FILE_DIR
from owade.constants import IMAGE_DIR

class HardDrive(models.Model):
    ## Serial number of the hard drive
    #serial = models.CharField(max_length=128, unique=True)
    serial = models.TextField(unique=True)
    ## Size in Byte of the hard drive
    size = models.TextField()

    def __unicode__(self):
        return "%s" % (self.serial)
    ## The path to the image of the hard drive, could be deleted
    def image_path(self):
        return "%s/%s_image" % (IMAGE_DIR, self.serial)
    ## The path to the ddrescue log of the hard drive, could be deleted
    def log_path(self):
        return "%s/%s_log_ddrescue" % (IMAGE_DIR, self.serial)

## Represents a file in the database
class File(models.Model):
    ## Md5 of the file
    #checksum = models.CharField(max_length=32)
    checksum = models.TextField()
    ## Extension of the file
    #extension = models.CharField(max_length=16, blank=True)
    extension = models.TextField(blank=True)
    ## Size in bytes of the file
    size = models.TextField()

    def __unicode__(self):
        return self.formatName()
    ## Format the name according to the extension
    def formatName(self):
        if self.extension == "":
            return "%i" % (self.id)
        return "%i.%s" % (self.id, self.extension)
    ## The path to the copy of the file on the owade server
    def file_path(self):
        return "%s/%s" % (FILE_DIR, self.formatName())


## Represents a Partition in the database
class Partition(models.Model):
    ## Slot of the partition on the hard drive
    slot = models.TextField()
    ## Offset in byte of the partition on the hard drive
    offset = models.TextField()
    ## Size in byte of the partition on the hard drive
    size = models.TextField()
    ## Type of the partition on the hard drive
    #type = models.CharField(max_length=128)
    type = models.TextField()
    ## The hard drive of the partition
    harddrive = models.ForeignKey(HardDrive)
    ## Files in the partition
    files = models.ManyToManyField(File)
    ##Operative system in the partition
    os = models.TextField()

    def __unicode__(self):
        return "%s" % (self.type)


## Represents the relation between a File and a Partition in the database
class FileInfo(models.Model):
    ## Old name of the file on the partition
    #name = models.CharField(max_length=64)
    name = models.TextField()
    ## Old directory path of the file on the partition
    #dir_path = models.CharField(max_length=256)
    dir_path = models.TextField()

    ## The related Partition
    partition = models.ForeignKey(Partition)
    ## The related File
    file = models.ForeignKey(File)

    def __unicode__(self):
        return "%s" % (self.name)


##################################################
#### File Analyze
##################################################
'''
class NodeRegistery(models.Model):
    name = models.CharField(max_length=32)

    father = models.ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        return "%s" % (self.name)

class ValueRegistery(models.Model):
    key = models.CharField(max_length=32, blank=True)
    type = models.IntegerField()
    value = models.CharField(max_length=128, blank=True)

    node = models.ForeignKey(NodeRegistery)

   def __unicode__(self):
        return "%s" % (self.key)

class HiveRegistery(models.Model):
    file = models.OneToOneField(File, primary_key=True)
    root = models.OneToOneField(NodeRegistery)

    def __unicode__(self):
        return "%s" % (self.file)

'''
##################################################
#### Generic Model
##################################################

class Category(models.Model):
    #name = models.CharField(max_length=32)
    name = models.TextField()
    description = models.TextField(blank=True)

    partition = models.ForeignKey(Partition, null=True)
    father = models.ForeignKey('self', null=True)

    def __unicode__(self):
        if self.description != "":
            return "%s (%s)" % (self.name, self.description)
        return "%s" % (self.name)

#class SubCategory(models.Model):
#    name = models.CharField(max_length=32)
#
#    category = models.ForeignKey(Category)
#
#    def __unicode__(self):
#        return "%s" % (self.name)

class Value(models.Model):
    #key = models.CharField(max_length=32)
    key = models.TextField()
    value = models.TextField(blank=True, null=True)

    category = models.ForeignKey(Category)

    def __unicode__(self):
        return "%s: %s" % (self.key, self.value)