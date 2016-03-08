# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.template import Template
from django.contrib.auth.decorators import login_required
from owade.forms import AnalyzeForm

from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from owade.program import Program
from owade.models import HardDrive, Partition
from owade.constants import HASHCAT_DIR

categoryList = [
        #{'name':'Index','address':'index','pages':[]},
        {'name':'Cases','address':'result','pages':[]},
        {'name':'Tasks','address':'launch','pages':[{'name':'Add', 'address':'launch_new'},
                                                    {'name':'Analyze', 'address':'launch_analyze'}]},
        ]

g_program = Program()


@login_required(redirect_field_name='/')
def index(request):
    if request.method == "GET":
        context = {
                'user': request.user.username,
                'form': AnalyzeForm,
        }
        return render(request, "index.html", context)
    elif request.method == "POST":

        form = AnalyzeForm(request.POST, request.FILES)
        if form.is_valid():

            print form.cleaned_data.get('image')
            file = form.cleaned_data.get('image')

            print file

            context = {
                'user': request.user.username,
                'form': AnalyzeForm,
            }
        return render(request, "index.html", context)


def extractView(request):
    class ExtractForm(forms.Form):
        hardDrives = forms.ModelChoiceField(queryset=HardDrive.objects.all(), empty_label=None)
        chromePasswords = forms.BooleanField(initial=True,required=False)
        chromeHistory = forms.BooleanField(initial=True,required=False)
        firefoxPassword = forms.BooleanField(initial=True,required=False)
        firefoxHistory = forms.BooleanField(initial=True,required=False)
        wifi = forms.BooleanField(initial=True,required=False)
        outlook = forms.BooleanField(initial=True,required=False)

    launch = False
    if request.method == 'POST':
        form = ExtractForm(request.POST)
        if form.is_valid():
            launch = True
            hardDrive = form.cleaned_data['hardDrives']
            task = '0'
            report = False
            chromePasswords = form.cleaned_data['chromePasswords']
            chromeHistory = form.cleaned_data['chromeHistory']
            firefoxPassword = form.cleaned_data['firefoxPassword']
            firefoxHistory = form.cleaned_data['firefoxHistory']
            wifi = form.cleaned_data['wifi']
            outlook = form.cleaned_data['outlook']

    else:
        form = ExtractForm()

    if launch:
        if g_program.task(task, hardDrive, report, chromePasswords, chromeHistory,firefoxPassword,firefoxHistory, wifi, outlook):
            return HttpResponseRedirect('launch')
        else:
            status = "Launch failure, a process is probably running"
    else:
        if g_program.available():
            status = "Choose an hard drive to analyze"
        else:
            status = "A process is running, you may need to stop it"

    return render_to_response("extract.html", {
        'category':'Tasks',
        'page':'Analyze',
        'status':status,
        'form': form,
        'categoryList':categoryList,
        }, context_instance=RequestContext(request))

def analizeView(request):
    class AnalyzeForm(forms.Form):
        hardDrives = forms.ModelChoiceField(queryset=HardDrive.objects.all(), empty_label=None)
        report = forms.BooleanField(initial=False, required=False)
        dictionary = forms.CharField(initial=HASHCAT_DIR + "/rockyou.txt",required=False)
        chromePasswords = forms.BooleanField(initial=True,required=False)
        chromeHistory = forms.BooleanField(initial=True,required=False)
        firefoxPassword = forms.BooleanField(initial=True,required=False)
        firefoxHistory = forms.BooleanField(initial=True,required=False)
        wifi = forms.BooleanField(initial=True,required=False)
        outlook = forms.BooleanField(initial=True,required=False)

    launch = False
    if request.method == 'POST':
        form = AnalyzeForm(request.POST)
        if form.is_valid():
            launch = True
            hardDrive = form.cleaned_data['hardDrives']
            task = '5'
            report = form.cleaned_data['report']
            dictionary = form.cleaned_data['dictionary']
            chromePasswords = form.cleaned_data['chromePasswords']
            chromeHistory = form.cleaned_data['chromeHistory']
            firefoxPassword = form.cleaned_data['firefoxPassword']
            firefoxHistory = form.cleaned_data['firefoxHistory']
            wifi = form.cleaned_data['wifi']
            outlook = form.cleaned_data['outlook']

    else:
        form = AnalyzeForm()

    if launch:
        if g_program.task(task, hardDrive, report, dictionary, chromePasswords, chromeHistory,firefoxPassword,firefoxHistory, wifi, outlook):
            return HttpResponseRedirect('launch')
        else:
            status = "Launch failure, a process is probably running"
    else:
        if g_program.available():
            status = "Choose an hard drive to analyze"
        else:
            status = "A process is running, you may need to stop it"

    return render_to_response("analyze.html", {
        'category':'Tasks',
        'page':'Analyze',
        'status':status,
        'form': form,
        'categoryList':categoryList,
        }, context_instance=RequestContext(request))

def launchView(request):
    if request.method == 'POST'and request.POST.get("cancel") != None:
        if g_program.interupt():
            status = "Process canceled with success"
        else:
            status = "Process refused to stop"
    else:
        if g_program.available():
            status = "No process is running"
        else:
            status = "A process is running"

    return render_to_response("launch.html", {
        'category':'Tasks',
        'page':'Main',
        'status':status,
        'categoryList':categoryList,
        }, context_instance=RequestContext(request))

###############################################
##### Launch Process
###############################################

@login_required(login_url="/admin")
def refreshInternLogView(request):
    log = g_program.internLog_.getLog()
    return render_to_response("refresh_log.html", {
        'log':log,
        }, context_instance=RequestContext(request))

@login_required(login_url="/admin")
def refreshTerminalLogView(request):
    log = g_program.terminalLog_.getLog()
    return render_to_response("refresh_log.html", {
        'log':log,
        }, context_instance=RequestContext(request))