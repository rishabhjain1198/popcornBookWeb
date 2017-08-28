from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import json
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
import requests
from bs4 import BeautifulSoup

import os


module_dir = os.path.dirname(__file__)  # get current directory
books_path = os.path.join(module_dir, 'bookData.txt')

# Create your views here.


#THIS IS USED TO LIMIT MEMORY USAGE AND PROVIDE SLIGHTLY DIFFERENTIATED RESULTS
number_of_books_to_use = 1500
#CHANGE THIS NUMBER TO A MAXIMUM OF 16000 TO USE A LARGER PORTION OF THE BOOK DATABASE

myModel = MultinomialNB()
vectorizer = TfidfVectorizer()
fitted = False

def index(request):
    context = {}
    return render(request, 'recommend/index.html', context)

def predict(request):
    finalbookresult = 'testing'
  
    movieanem = request.POST['moviename']
    print(movieanem)
    
    
    omoviename = movieanem
    
    #CHECK FOR EMPTY MOVIENAME HERE

    moviename = omoviename.split(' ')

    if len(moviename) < 1:
        print("Invalid input for movie name")

    movnam = moviename[0]

    for word in moviename[1:]:
        movnam = movnam + '+' + word


    sr = requests.get('http://www.imdb.com/find?ref_=nv_sr_fn&q=' + movnam + '&s=all').text

    splitted = sr.split('<h3 class="findSectionHeader"><a name="tt"></a>Titles</h3>')[1]
    splitted = splitted.split('<a href="/title/tt')[1]
    movieid = splitted.split('/')[0]

    print(movieid)

    if not movieid.isdigit():
        movieid = '5472374'



    synourl = 'http://www.imdb.com/title/tt' + movieid + '/synopsis?ref_=tt_stry_pl'

    r = requests.get(synourl).text

    soup = BeautifulSoup(r, 'html.parser')

# TO GET SYNOPSIS

    finalstring = ''

    required = soup.get_text().split('Synopsis')
    finalstring = finalstring + required[5]
    finalstring = finalstring.replace('\n', '').replace('\r', '')


# If synopsis is empty, we have to do something
    if finalstring == '':
        print("NO SYNOPSIS AVAILABLE ON IMDB")
    
    #time to look for the stuff using plot summaries
    
    #CODE GOES HERE
    
        newr = requests.get('http://www.imdb.com/title/tt' + movieid +'/plotsummary?ref_=tt_stry_pl').text
        newsoup = BeautifulSoup(newr, 'html.parser')
    
        chahi = newsoup.get_text()
    
        if 'plot summaries\n\n\n' in chahi:
            chahi = chahi.split('plot summaries\n\n\n')[1]
            chahi = chahi.split('\n- Written by\n')[0]
    
        if 'plot summary\n\n\n' in chahi:
            chahi = chahi.split('plot summary\n\n\n')[1]
            chahi = chahi.split('\n\n\n')[0]
    
        finalstring = finalstring + chahi

#if final string is still empty, last resort is to simply try to suggest
#something based on the title of the movie

    if finalstring == '':
        finalstring = finalstring + omoviename

    stop_words = set(stopwords.words('english'))

    tokenizer = RegexpTokenizer(r'\w+')
    wordsTokenized = tokenizer.tokenize(finalstring)
    stringer = ''

    for w in wordsTokenized:
        w = w.lower()
        if w not in stop_words and w != "the":
            stringer = stringer + w + ' '

    print(stringer)

    global vectorizer
    global myModel
    movieproc = [stringer]
    prid = vectorizer.transform(movieproc)
    prid = prid.toarray()

    finalprediction = myModel.predict(prid)
    print(finalprediction)
    
    
    finalbookresult = finalprediction

    return HttpResponseRedirect(reverse('result', kwargs={'finalbookresult':finalbookresult}))

def result(request, finalbookresult):
    context = {'finalbookdata':finalbookresult, }
    return render(request, 'recommend/result.html', context)

class SimpleMiddleware(object):
    

    def __init__(self, get_response):
        
        self.get_response = get_response
        global fitted
        if fitted == True:
            pass
        global myModel
        global vectorizer





        #MACHINE FITTING CODE HERE

        with open(books_path) as outfile:
            bookdata = json.load(outfile)

        bookDataWords = []
        bookDataTargets = []

        bookDataStrings = []
        y_train = []

        for i, key in enumerate(bookdata):
            tobeapp = ''
    
            for word in bookdata[key]:
                tobeapp = tobeapp + word + ' '
    
            tobeapp = tobeapp[:-1]
            bookDataStrings.append(tobeapp)
            y_train.append(key)
    
            if i == number_of_books_to_use:
                break

#print(bookDataStrings)
#print(y_train)


# Time to implement the training

        vectorizer = TfidfVectorizer()
        x_train = vectorizer.fit_transform(bookDataStrings)
        x_train = x_train.toarray()

        gnb = MultinomialNB()

        print("fitting started ResidentSleeper")
        myModel = gnb.fit(x_train, y_train)
        print("fitting completed")
        fitted = True
        
        
    
    


    def __call__(self, request):
        response = self.get_response(request)
        return response
