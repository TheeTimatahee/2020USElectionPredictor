import twitter
from datetime import date, time, datetime
import time
import json
import tweepy
import sys

def secToHMS(n):
    """Method for calculating the amount of time taken to output"""
    #Get the hours portion
    hours = int(n/3600)
    n -= hours*3600

    #If less then 10 add a 0; for purely aesthetic purposes
    if hours < 10:
        hours = "0" + str(hours)
    
    #Get Seconds portion
    Seconds = int(n/60)
    n -= Seconds*60

    #If less then 10 add a 0; for purely aesthetic purposes
    if Seconds < 10:
        Seconds = "0" + str(Seconds)
    
    #return str(hours) + ":" + str(Seconds) + ":" + str(n)
    return (str(hours),str(Seconds),str(n))

class StreamListener(tweepy.StreamListener):
    
    def __init__(self, candidate, api=None,  filename="tweets.txt"):
        super().__init__(api=api)
        # Number of tweets mined by this stream
        self.tweets = 0
        # Name of file tweets are being written to
        self.filename = filename
        # The time when this stream began
        self.startTime = float(time.time())
        # The name of the candidate being mined
        self.candidate = candidate

    def on_status(self, status):
        if(status.lang == "en"):
            #Creates a dictionary to store relevant information about the tweet
            diction = {}
            diction['user'] = status.user.screen_name
            diction['followers'] = status.user.followers_count
            diction['created_at'] = str(status.created_at)
            diction['coords'] = status.coordinates
            diction['retweet_count'] = status.retweet_count
            diction['verified'] = ((status._json)['user'])['verified']
            # Try to get the extended text if the tweet goes beyond 140 characters
            try: 
                diction['text'] = ((status._json)['extended_tweet'])['full_text']
            # Except if it doesn't go beyond the 140 character limit and raises an error
            except:
                # Check if the status retweeted another status
                if 'retweeted_status' in status._json:
                    # If it does, attempt to get the extended text if the tweet goes beyond 140 characters
                    try:
                        diction['text'] = str(status.id)  + " " + (((status._json)['retweeted_status'])['extended_tweet'])['full_text']
                    # Except if it doesn't go beyond the 140 character limit and raises an error, get the text
                    except:
                        diction['text'] = str(status.id) + " " + ((status._json)['retweeted_status'])['text']
                # If it doesn't retweet anything and doesn't go beyond 140 characters, just get the normal text
                else:
                    diction['text'] = status.text

            # Writes the dictionary to the file, which will eventually be converted back into a dictionary using json
            f = open(self.filename,"a")
            try:
                f.write(str(diction) + "\n")
            # In the case where something goes wrong, throw out the tweet and continue mining
            except: 
                print("Error: Couldn't write tweet to " + self.filename + ". Continuing...")
                f.close()
                return

            # Close the file and increment the number of tweets mined by the stream
            f.close()
            self.tweets += 1
            print("Tweets mined: " + str(self.tweets))
            
            # Calculates the amount of time since the stream started
            deltaT = float(time.time()) - self.startTime
            (h,m,s) = secToHMS(deltaT)
            print("Stream uptime: " + h + ":" + m + ":" + s)
            rate = tweetsPerSecond(self.tweets,deltaT)
            print("Tweets per second: " + str(rate))

            coord = {}
            coord['time'] = time.time()
            coord['rate'] = rate

            f = open("timeVsRate" + self.candidate + ".txt","a")
            f.write(str(coord) + "\n")
            f.close()


    def on_error(self, status_code):
        if status_code == 420:
            return False

def tweetsPerSecond(tweets,seconds):
    if seconds < 1:
        return "Not enough data"
    return tweets / (int(round(seconds)))

if __name__ == "__main__":
    # CONSUMER_KEY = YOUR CONSUMER_KEY HERE
    # CONSUMER_SECRET = YOUR CONSUMER_SECRET HERE
    # OAUTH_TOKEN = YOUR OAUTH_TOKEN HERE
    # OAUTH_TOKEN_SECRET = YOUR OAUTH_TOKEN_SECRET HERE

    bidenTerms = ["biden","joebiden"]
    bernieTerms = ["bernie","sanders","berniesanders"]
    harrisTerms = ["@KamalaHarris","harris","kamala"]
    warrenTerms = ["@ewarren","warren","elizabeth warren"]
    trumpTerms = ["@realDonaldTrump","trump","donaldtrump"]
    i = str(input("What candidate do you want to mine?"))
    track = None
    if i == "biden":
        track = bidenTerms
    if i == "bernie":
        track = bernieTerms
    if i == "harris":
        track = harrisTerms
    if i == "warren":
        track = warrenTerms
    if i == "trump":
        track = trumpTerms

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    twitter_api = tweepy.API(auth)

    stream_listener = StreamListener(candidate=i,filename= i + ".txt")
    stream = tweepy.Stream(auth=twitter_api.auth, listener=stream_listener, tweet_mode='extended')

    stream.filter(track=track)