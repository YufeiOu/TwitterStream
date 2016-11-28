from django.shortcuts import render
import datetime
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from TwitterStream.models import Tweet
from django.shortcuts import render_to_response  
from threading import Thread
import boto.sqs
from boto.sqs.message import Message
import boto.sns
import requests
from multiprocessing import Pool
import os
import tweepy
from tweepy.api import API
import json
import sys
import urllib2
import urllib
import traceback
# from nltk.tokenize import RegexpTokenizer
# from stop_words import get_stop_words
# from nltk.stem.porter import PorterStemmer
# from gensim import corpora, models
# import gensim


consumer_token = 'link_credential1'
consumer_secret = 'link_credential2'

requesttoken = None
myStream = None
conn = None
messagequeue = None
resultqueue = None
poolthread = None
snsurl = None
snsclient = None

class MyStreamListener(tweepy.StreamListener):
	def __init__(self, queue=None, api=None):
		self.messagequeue = queue
		self.api = api or API()

	def on_status(self, status):
		try:
			if not status.coordinates == None:
				newtweet = Tweet(content = status.text, longitude = status.coordinates['coordinates'][0], 
					latitude = status.coordinates['coordinates'][1], 
					topic = '', 
					date = status.created_at)
				newtweet.save()
				print 'save'
				if self.messagequeue:
					s = Message()
					s.set_body(status.text)
					self.messagequeue.write(s)
					print 'write'
			#print '\n %s  %s  %s\n' % (status.text, status.created_at, status.coordinates)
		except Exception, e:
			# Catch any unicode errors while printing to console
			# and just ignore them to avoid breaking application.
			print e

# Create your views here.

def process():
	#to do
	global conn
	global messagequeue
	global poolthread
	global resultqueue
	global snsclient
	while True:
		try:
			if messagequeue:
				messages = messagequeue.get_messages(num_messages=1)
				if len(messages) > 0:
					message = messages[0]
					url = 'http://gateway-a.watsonplatform.net/calls/text/TextGetTextSentiment'
					parameters = {'apikey' : 'link_credential8', 'text':message.get_body(), 'outputMode':'json'}
					response = requests.get(url, params=parameters)
					result = json.loads(response.text)
					if not result['status'] == 'OK':
						continue
					mes = {
						'type':result['docSentiment']['type'],
						'text':message.get_body()
					}
					snsclient.publish(topic = 'arn:aws:sns:us-west-2:803394064234:Twitter', message = json.dumps(mes))
					messagequeue.delete_message(message)
					print "publish"
					# if resultqueue:
					# 	s = Message()
					# 	s.set_body(json.dumps(mes))
					# 	resultqueue.write(s)
		except Exception, e:
				# Catch any unicode errors while printing to console
				# and just ignore them to avoid breaking application.
				exc_type, exc_value, exc_traceback = sys.exc_info()
				traceback.print_exception(exc_type, exc_value, exc_traceback)

def workerPool():
	global conn
	global messagequeue
	global poolthread
	global resultqueue
	pool = Pool(processes = 5)
	while True:
		if messagequeue:
			mes = messagequeue.get_messages(num_messages=10)
			result = pool.map(process, mes)

def createSQS():
	global conn
	global messagequeue
	global poolthread
	global resultqueue
	global snsclient
	if not conn:
		conn = boto.sqs.connect_to_region("us-west-2",
			aws_access_key_id='link_credential6',
			aws_secret_access_key='link_credential7')
		snsclient = boto.sns.connect_to_region("us-west-2",
			aws_access_key_id='link_credential6',
			aws_secret_access_key='link_credential7')
		messagequeue = conn.create_queue('tweets')
		resultqueue = conn.create_queue('sentiments')

def createWorkerPool():
	global conn
	global messagequeue
	global poolthread
	global resultqueue
	if not poolthread:
		poolthread = Thread(target = process)
		poolthread.start()

def processSNSUrl(request):
	global snsurl
	return HttpResponse(json.dumps(snsurl))

def getSentiments(request):
	global conn
	global messagequeue
	global poolthread
	global resultqueue
	res = []
	if resultqueue:
		result = resultqueue.get_messages(num_messages=10)
		for mes in result:
			body = json.loads(mes.get_body())
			res.append(body['Message'])
			resultqueue.delete_message(mes)
	final = json.dumps(res)
	return HttpResponse(final)

def index(request):
	global myStream
	createSQS()
	createWorkerPool()
	if myStream:
		print myStream.running
	if myStream and myStream.running:
		return HttpResponseRedirect('/TwitterStream/test/')
	auth = tweepy.OAuthHandler(consumer_token, consumer_secret, "http://127.0.0.1:8000/TwitterStream/redirect")
	# for aws server, now is "http://ec2-35-164-174-113.us-west-2.compute.amazonaws.com:8000/TwitterStream/redirect"
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
	global messagequeue
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
		myStreamListener = MyStreamListener(queue=messagequeue)
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

def getTweetswithTopic(request):
	topic = request.GET.get('topic','')
	tweetlist = Tweet.objects.filter(topic = topic)
	return HttpResponse(json.dumps(tweetlist))