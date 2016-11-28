# TwitterStream
Homework 2 for Cloud Computing - Group 29

Note: due to the credential issue, we copy the code "without" leaking any password information, if you want to run this program, please change all the hardcode

"link_credential1" - "link_credential8"

to correct keys of yourself or contact YufeiOu.

Run command:

  python manage.py runserver

If it is in AWS, then:

  python manage.py runserver 0.0.0.0:8000

Introduction to this project:

This homework is based on 

  1. assignment1 (django python framework as the backend and frontend structure. Twitter stream as input (random pick the tweets from the API). Google map as the frontend displayer.)
  2. SQS (tweets queue/ sentiments queue)
  3. SNS send notification
  4. Alchemy API to label sentiments


For your convenience, this project could be seen from
http://ec2-35-164-174-113.us-west-2.compute.amazonaws.com:8000/TwitterStream/
But I will not turn on this machine until the demo due to the limitation of API access. If you want to see the result, contact YufeiOu for details.
