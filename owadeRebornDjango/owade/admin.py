from django.contrib import admin
from owade.models import *
# Register your models here.

##################################################
#### File Extraction
##################################################

class HardDriveAdmin(admin.ModelAdmin):
    list_display = ('id', 'serial', 'size')
    search_fields = ['serial']
admin.site.register(HardDrive, HardDriveAdmin)

class PartitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'slot', 'harddrive', 'size', 'type')
    search_fields = ['type']
admin.site.register(Partition, PartitionAdmin)

class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'extension', 'checksum', 'size')
    search_fields = ['extension', 'checksum']
admin.site.register(File, FileAdmin)

class FileInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dir_path', 'partition', 'file')
    search_fields = ['name', 'dir_path']
admin.site.register(FileInfo, FileInfoAdmin)


##################################################
#### File Analyze
##################################################

#class HiveRegisteryAdmin(admin.ModelAdmin):
#    list_display = ('file', 'root')
#admin.site.register(HiveRegistery, HiveRegisteryAdmin)
#
#class NodeRegisteryAdmin(admin.ModelAdmin):
#    list_display = ('id', 'name', 'father')
#    search_fields = ['name']
#admin.site.register(NodeRegistery, NodeRegisteryAdmin)
#
#class ValueRegisteryAdmin(admin.ModelAdmin):
#    list_display = ('id', 'key', 'value', 'type')
#    search_fields = ['key']
#admin.site.register(ValueRegistery, ValueRegisteryAdmin)


##################################################
#### Generic Model
##################################################

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'partition', 'father')
    search_fields = ['name']
admin.site.register(Category, CategoryAdmin)

#class SubCategoryAdmin(admin.ModelAdmin):
#    list_display = ('name', 'category')
#admin.site.register(SubCategory, SubCategoryAdmin)

class ValueAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'category')
    search_fields = ['key', 'value']
admin.site.register(Value, ValueAdmin)
