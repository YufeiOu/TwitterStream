# TwitterStream
Homework 1 for Cloud Computing - Group 29

Note: due to the credential issue, we copy the code "without" leaking any password information, if you want to run this program, please change all the hardcode

"link_credential1" - "link_credential5"

to correct keys of yourself or contact YufeiOu.

Run command:

  python manage.py runserver

If it is in AWS, then:

  python manage.py runserver 0.0.0.0:8000

Introduction to this project:

This homework is based on

  1. django python framework as the backend and frontend structure 
  2. Twitter stream as input (random pick the tweets from the API) 
  3. Google map as the frontend displayer.
  
It simply print the tweets to the map (to show where this tweet from) and you can mouseon to see the tweets content. Besides that, we use the twitter filter function to filter the tweets that contain certain keywords such as food, game or movie and display the heatmap of those tweets.

For your convenience, an old version of this project could be seen from 
http://ec2-35-160-155-125.us-west-2.compute.amazonaws.com:8000/TwitterStream/ 
I will turn on this machine from 10.24 11:59 - 10.31 11:59. Take your time to view the result.
