from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

# Create your views here.

def index(request):
    context = {}
    return render(request, 'recommend/index.html', context)

def predict(request):
    movieanem = request.POST['moviename']
    print(movieanem)
    finalbookresult = "mast"
    return HttpResponseRedirect(reverse('result', kwargs={'finalbookresult':finalbookresult}))

def result(request, finalbookresult):
    context = {'finalbookdata':finalbookresult, }
    return render(request, 'recommend/result.html', context)
