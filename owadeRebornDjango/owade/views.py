from django.shortcuts import render
import copy
import sys

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django import forms

from owade.program import Program
from owade.log import Log
from owade.fileExtraction.newHardDrive import NewHardDrive
from owade.result.passwords import Passwords
from owade.result.history import History
from owade.models import *


# Create your views here.

categoryList = [
        #{'name':'Index','address':'index','pages':[]},
        {'name':'Cases','address':'result','pages':[]},
        {'name':'Tasks','address':'launch','pages':[{'name':'Add', 'address':'launch_new'},
                                                    {'name':'Analyze', 'address':'launch_analyze'}]},
        ]

g_program = Program()


@login_required(login_url="/admin")
def indexView(request):
    return render_to_response("index.html", {
        'category':'Index',
        'page':'Main',
        'categoryList':categoryList,
        }, context_instance=RequestContext(request))

def logoutView(request):
    logout(request)
    return HttpResponseRedirect('login')



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

@login_required(login_url="/admin")
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

@login_required(login_url="/admin")
def launchNewView(request):
    class DDrescueForm(forms.Form):
        device = forms.CharField(max_length=30, initial="/dev/sd")
        overWrite = forms.BooleanField(initial=False, required=False)
        retry = forms.IntegerField(initial="3", required=False)

    launch = False
    if request.method == 'POST':
        form = DDrescueForm(request.POST)
        if form.is_valid():
            launch = True
            device = form.cleaned_data['device']
            overWrite = form.cleaned_data['overWrite']
            retry = form.cleaned_data['retry']
    else:
        form = DDrescueForm()

    if launch:
        if g_program.launch(NewHardDrive, device, overWrite, retry):
            return HttpResponseRedirect('launch')
        else:
            status = "Launch failure, a process is probably running"
    else:
        if g_program.available():
            status = "Choose a new Hard Drive to add to Owade"
        else:
            status = "A process is running, you may need to stop it"

    return render_to_response("launch_new.html", {
        'category':'Tasks',
        'page':'Add',
        'status':status,
        'form': form,
        'categoryList':categoryList,
        }, context_instance=RequestContext(request))

@login_required(login_url="/admin")
def launchAnalyze(request):
    class AnalyzeForm(forms.Form):
        hardDrives = forms.ModelChoiceField(queryset=HardDrive.objects.all(), empty_label=None)
        tasks = forms.ChoiceField(choices=g_program.tasks_form_)
        overWrite = forms.BooleanField(initial=False, required=False)

    launch = False
    if request.method == 'POST':
        form = AnalyzeForm(request.POST)
        if form.is_valid():
            launch = True
            hardDrive = form.cleaned_data['hardDrives']
            task = form.cleaned_data['tasks']
            overWrite = form.cleaned_data['overWrite']
    else:
        form = AnalyzeForm()

    if launch:
        if g_program.task(task, hardDrive, overWrite):
            return HttpResponseRedirect('launch')
        else:
            status = "Launch failure, a process is probably running"
    else:
        if g_program.available():
            status = "Choose an hard drive to analyze"
        else:
            status = "A process is running, you may need to stop it"

    return render_to_response("launch_analyze.html", {
        'category':'Tasks',
        'page':'Analyze',
        'status':status,
        'form': form,
        'categoryList':categoryList,
        }, context_instance=RequestContext(request))


###############################################
##### Result overview
###############################################

@login_required(login_url="/admin")
def resultView(request):
    hardDrives = HardDrive.objects.all()

    return render_to_response("result.html", {
        'category':'Cases',
        'page':'Main',
        'hardDrives':hardDrives,
        'categoryList':categoryList,
        }, context_instance=RequestContext(request))

@login_required(login_url="/admin")
def resultHardDriveView(request, hardDrive_id):
    hardDrive = HardDrive.objects.select_related().get(id=hardDrive_id)
    partitions = Partition.objects.filter(harddrive=hardDrive)

    #FIXME: Hardcoded
    categoryListCpy = copy.deepcopy(categoryList)
    pages = categoryListCpy[0]['pages']
    pages.insert(1, {'name':hardDrive, 'address':'result_harddrive_%d' % hardDrive.id})
    return render_to_response("result_harddrive.html", {
        'category':'Cases',
        'page':hardDrive,
        'hardDrive':hardDrive,
        'partitions':partitions,
        'categoryList':categoryListCpy,
        }, context_instance=RequestContext(request))

#def getDbGenericDic(father):
#    dic = {}
#    for category in father.category_set.all():
#        dic[category.name] = getDbGenericDic(category)
#    for value in father.value_set.all():
#        dic[value.key] = value.value
#    return dic

#def getDbGenericDic(father, depth=0):
#    infos = ""
#    for value in father.value_set.all():
#        infos = "%s<b>%s:</b> %s<br />" % (infos, value.key, value.value)
#    for category in father.category_set.all():
#        if depth == 0:
#            infos = "%s<h3>%s</h3>%s<br />" % (infos, category.name, getDbGenericDic(category, depth + 1))
#        else:
#            infos = "%s<h4>%s</h4>%s<br />" % (infos, category.name, getDbGenericDic(category, depth + 1))
#    return infos

def getDbGenericDic(father, depth=0):
    infos = ""
    for value in father.value_set.all():
        infos = "%s<li><b>%s:</b> %s</li>" % (infos, value.key, value.value)
    for category in father.category_set.all():
        infos = "%s<li>%s<ul>%s</ul></li>" % (infos, category.name, getDbGenericDic(category, depth + 1))
    return infos

@login_required(login_url="/admin")
def resultPartitionView(request, partition_id):
    partition = Partition.objects.select_related().get(id=partition_id)
    categories = partition.category_set.all()
    linkedin = False
    infos = '<ul id="treemenu1" class="treeview">'
    for category in categories:
        dic = getDbGenericDic(category)
        infos = "%s<li>%s<ul>%s</ul><li/>" % (infos, category.name, dic)
        #infos = "%s<br /><h2>%s</h2>%s<br />" % (infos, category.name, getDbGenericDic(category))
        #infos[category.name] = getDbGenericDic(category)
        if category.name == 'WebAnalyze' and 'GetLinkedinContent' in dic:
            linkedin = True
    infos = "%s</ul>" % infos

    #FIXME hardcoded
    categoryListCpy = copy.deepcopy(categoryList)
    hardDrive = partition.harddrive
    pages = categoryListCpy[0]['pages']
    pages.insert(1, {'name':hardDrive, 'address':'result_harddrive_%d' % hardDrive.id})
    pages.insert(2, {'name':partition, 'address':'result_partition_%d' % partition.id})
    return render_to_response("result_partition.html", {
        'category':'Cases',
        'page':partition,
        'partition':partition,
        'infos':infos,
        'linkedin':linkedin,
        'categoryList':categoryListCpy,
        }, context_instance=RequestContext(request))

@login_required(login_url="/admin")
def resultLinkedinView(request, partition_id):
    partition = Partition.objects.get(id=partition_id)
    try:
        father = Category.objects.get(partition=partition, name__iexact='WebAnalyze')
        father = Category.objects.get(father=father, name__iexact='GetLinkedinContent')
        value = Value.objects.get(category=father, key__iexact='pdf')
    except Exception as exp:
        print >>sys.stderr, exp.message
        return HttpResponseRedirect('result_partition_%s' % partition_id)

    pdf = value.value
    file = open(pdf)
    response = HttpResponse(file.read())
    file.close()
    response['Content-Type'] = 'application/pdf'
    response['Content-disposition'] = 'attachment'
    return response

@login_required(login_url="/admin")
def resultPasswordsView(request, partition_id):
    partition = Partition.objects.get(id=partition_id)
    process = Passwords(Log(), Log(), partition)
    process.start()
    process.join()

    #FIXME hardcoded
    categoryListCpy = copy.deepcopy(categoryList)
    hardDrive = partition.harddrive
    pages = categoryListCpy[0]['pages']
    pages.insert(1, {'name':hardDrive, 'address':'result_harddrive_%d' % hardDrive.id})
    pages.insert(2, {'name':partition, 'address':'result_partition_%d' % partition.id})
    pages.insert(2, {'name':'Credentials', 'address':'result_passwords_%d' % partition.id})
    return render_to_response("result_passwords.html", {
        'category':'Cases',
        'page':'Credentials',
        'credentials':process.credentials_,
        'passwords':process.passwords_,
        'users':process.users_,
        'mails':process.mails_,
        'categoryList':categoryListCpy,
        }, context_instance=RequestContext(request))

@login_required(login_url="/admin")
def resultHistoryView(request, partition_id):
    partition = Partition.objects.get(id=partition_id)
    process = History(Log(), Log(), partition)
    process.start()
    process.join()
    domains = process.domains_

    #FIXME hardcoded
    categoryListCpy = copy.deepcopy(categoryList)
    hardDrive = partition.harddrive
    pages = categoryListCpy[0]['pages']
    pages.insert(1, {'name':hardDrive, 'address':'result_harddrive_%d' % hardDrive.id})
    pages.insert(2, {'name':partition, 'address':'result_partition_%d' % partition.id})
    pages.insert(2, {'name':'History', 'address':'result_passwords_%d' % partition.id})
    return render_to_response("result_history.html", {
        'category':'Cases',
        'page':'History',
        'domains':domains,
        'categoryList':categoryListCpy,
        }, context_instance=RequestContext(request))
