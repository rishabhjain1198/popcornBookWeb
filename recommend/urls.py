from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^predictor/$', views.predict, name='predict'),
    url(r'^result/(?P<movieid>[0-9]+)/(?P<finalbookresult>.*)/$', views.result, name='result'),
    url(r'^explain/$', views.explain, name='explain'),
                   
]
