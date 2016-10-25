from django.conf.urls import patterns, url
import os

from TwitterStream import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^redirect/$', views.redirect, name='redirect'),
    url(r'^getnewtweets/$', views.getnewtweets, name='getnewtweets'),
    url(r'^gettweetswithfilter/$', views.getTweetswithFilter, name='getTweetswithFilter'),
    url(r'^gettweetswithtopic/$', views.getTweetswithTopic, name='getTweetswithTopic'),
    url(r'^test/$', views.testwebpage, name='testwebpage'),
    url(r'^image/(?P<path>.*)','django.views.static.serve',{'document_root':os.path.join(os.path.dirname(__file__)) + '/resource/image/'}),
    url(r'^js/(?P<path>.*)','django.views.static.serve',{'document_root':os.path.join(os.path.dirname(__file__)) + '/resource/js/'}),
    url(r'^css/(?P<path>.*)','django.views.static.serve',{'document_root':os.path.join(os.path.dirname(__file__)) + '/resource/css/'}),  
)