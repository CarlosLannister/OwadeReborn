
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

from owade import views
from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    #(r'^$', 'indexView'),
    #(r'^index$', 'indexView'),


    #Direcciones nuevas
    url(r'^$', views.indexView),
    url(r'^index$', views.indexView),
    url(r'^login$', views.loginView),

    url(r'^extract$', views.extractView),
    url(r'^analyze$', views.analizeView),
    url(r'^timeline$', views.timelineView),

    url(r'^settings$', views.settingsView),
    url(r'^help$', views.helpView),
    url(r'^logout$', views.logoutView),

    #Direcciones antiguas
    url(r'^results', views.resultView),
    url(r'^launch$', views.launchView),
    url(r'^launch_new$', views.launchNewView),
    url(r'^launch_analyze$', views.launchAnalyze),

    url(r'^refresh_intern_log$', views.refreshInternLogView),
    url(r'^refresh_terminal_log$', views.refreshTerminalLogView),

    url(r'^result$', views.resultView),
    url(r'^result_harddrive_(?P<hardDrive_id>\d+)$', views.resultHardDriveView),
    url(r'^result_partition_(?P<partition_id>\d+)$', views.resultPartitionView),
    url(r'^result_linkedin_(?P<partition_id>\d+)$', views.resultLinkedinView),
    url(r'^result_passwords_(?P<partition_id>\d+)$', views.resultPasswordsView),
    url(r'^result_history_(?P<partition_id>\d+)$', views.resultHistoryView),

    url(r'^exemple_text$', TemplateView.as_view(template_name='exemple_text.html')),
    url(r'^exemple_form$', TemplateView.as_view(template_name='exemple_form.html')),
    url(r'^exemple_table$', TemplateView.as_view(template_name='exemple_table.html')),
]
'''
urlpatterns += [
    url(r'^login$', auth_views.login, TemplateView.as_view(template_name='login.html')),
                        ]
'''