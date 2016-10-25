from django.shortcuts import render
import datetime
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from TwitterStream.models import Tweet
from django.shortcuts import render_to_response  
import os
import tweepy
import json


consumer_token = 'link_credential1'
consumer_secret = 'link_credential2'

requesttoken = None
myStream = None

class MyStreamListener(tweepy.StreamListener):
	def on_status(self, status):
		try:
			if not status.coordinates == None:
				print 'tweet saved'
				newtweet = Tweet(content = status.text, longitude = status.coordinates['coordinates'][0], 
					latitude = status.coordinates['coordinates'][1], 
					topic = '', 
					date = status.created_at)
				newtweet.save()
		except Exception, e:
			print e

# Create your views here.
def index(request):
	global myStream
	if myStream != None:
		print myStream.running
	if myStream != None and myStream.running:
		return HttpResponseRedirect('/TwitterStream/test/')
	auth = tweepy.OAuthHandler(consumer_token, consumer_secret, "http://127.0.0.1:8000/TwitterStream/redirect")
	try:
		redirect_url = auth.get_authorization_url()
	except tweepy.TweepError as e:
		print e
		print 'Error! Failed to get request token.'
	global requesttoken
	requesttoken = auth.request_token	
	return HttpResponseRedirect(redirect_url)

def redirect(request):
	verifier = request.GET.get('oauth_verifier')
	auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
	global requesttoken
	auth.request_token = requesttoken
	try:
		auth.get_access_token(verifier)
	except tweepy.TweepError as e:
		print e
		print e.reason
		print 'Error! Failed to get access token.'
	try:
		auth.set_access_token(auth.access_token, auth.access_token_secret)
		api = tweepy.API(auth)
		myStreamListener = MyStreamListener()
		global myStream
		myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
		myStream.filter(track=['food', 'music', 'book', 'movie', 'game', 'sports', 'the', 'a', 
			'and', 'to', 'i', 'in', 'it', 'you', 'of', 'for', 'on'], async=['true'])
	except Exception as e:
		print e
		print 'Error! Failed to get tweets.'
	return HttpResponseRedirect('/TwitterStream/test/')

def testwebpage(request):
	return render_to_response('resource/html/test.html') 

def getnewtweets(request):
	final = ''
	try:
		timefrom =  request.GET.get('timefrom','')
		timeto =  request.GET.get('timeto','')
		ctimefrom = datetime.datetime.strptime(timefrom, '%a, %d %b %Y %H:%M:%S %Z')+ datetime.timedelta(seconds = -10)
		ctimeto = datetime.datetime.strptime(timeto, '%a, %d %b %Y %H:%M:%S %Z')+ datetime.timedelta(seconds = -10)
		tweetlist = Tweet.objects.filter(date__range = (ctimefrom, ctimeto))
		res = []
		for tweet in tweetlist:
			res.append({'date':str(tweet.date), 
				'content': tweet.content, 
				'latitude': tweet.latitude,
				'longitude': tweet.longitude,
				'topic': tweet.topic})
		final = json.dumps(res)
	except Exception as e:
		print e
	return HttpResponse(final)

def getTweetswithFilter(request):
	final = ''
	try:
		filter = request.GET.get('filter','all')
		tweetlist = None
		if filter == 'all':
			tweetlist = Tweet.objects.all()
		else:
			tweetlist = Tweet.objects.filter(content__contains = filter)
		res = []
		for tweet in tweetlist:
			res.append({'date':str(tweet.date), 
				'content': tweet.content, 
				'latitude': tweet.latitude,
				'longitude': tweet.longitude,
				'topic': tweet.topic})
		final = json.dumps(res)
	except Exception as e:
		print e
	return HttpResponse(final)

def getTweetswithTopic(request):
	topic = request.GET.get('topic','')
	tweetlist = Tweet.objects.filter(topic = topic)
	return HttpResponse(json.dumps(tweetlist))