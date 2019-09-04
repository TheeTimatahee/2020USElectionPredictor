from analysisTools import getAllTweets
import matplotlib
from Sentiment_Analysis import lotsOfAnalysis
import matplotlib.pyplot as plt
import numpy as np
import time
from miner import secToHMS

def labelValues(ax,rects,makeInt=False):
    """Add labels to the given plots"""
    s = '%f'
    if makeInt:
        s = '%d'
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2.,
                height+.0025,
                s % height,
                ha='center', 
                va='bottom')

def getTally(data,polarity=0):
    """Find the number of positive and negative tweets for a data set"""
    pos = 0
    neg = 0
    # For each tweet in the data set
    for e in data:
        # If the polarity isn't very high, don't bother counting it
        if abs(e.get('polarity')) < polarity:
            pass
        # Find sentiment is positive, then add a tally to pos
        elif e.get('sentiment') == 'pos':
            pos += 1
        # Otherwise sentiment is negative so add a tally to neg
        else:
            neg += 1
    return pos,neg,len(data)

def makeFollowerBrackets(data):
    """Makes a list of lists with all the tweets for which the user making them has 
    certain number of followers. First list has tweets by users with less than 10 followers, second
    has tweets by users with more than 10 followers and less than 100 followers, etc"""
    # Sort list of tweets by followers in ascending order
    l1 = sorted(data, key = lambda i: i['followers'])
    # brackets is list of lists
    brackets = []
    separator = 10
    while separator < 1000000:
        # Increment through each tweet
        k = 0
        # As long as the follower count is below the cutoff, keep incrementing
        while l1[k].get("followers") < separator:
            k += 1
        # Add list of tweets below the separator to the bracket list
        brackets.append(l1[0:k])
        # Update l1 to not include tweets just added to brackets
        l1 = l1[k:]
        # Increment separator
        separator *= 10
    # Add remaining tweets and return
    brackets.append(l1)
    return brackets

def makeVerifiedBrackets(data):
    """Makes 2 lists of tweets: one with tweets by nonverified users and one
    with tweets by verified users"""
    nonVerified = []
    verified = []
    # For each tweet in data set
    for e in data:
        # In the user making the tweet is verified add that tweet to the list of verified tweets
        if e.get('verified'):
            verified.append(e)
        # Otherwise user making the tweet is nonverified so add the tweet to the list of nonverified tweets
        else:
            nonVerified.append(e)
    return nonVerified, verified

def makeApprovalPieChart(candidate, pos, neg):
    labels = 'Approve', 'Disapprove'
    sizes = [pos, neg]
    explode = (0.1, 0)

    _, ax = plt.subplots()
    ax.pie(x = sizes, # Data
           explode = explode, 
           labels = labels, 
           colors = ['g','r'], # g=green, r=red
           autopct = '%1.1f%%', 
           shadow = True, 
           startangle = 90)
    ax.axis('equal')
    ax.set(title = candidate.capitalize() + "'s Approval Rating")

    plt.show()

def makeBarApprovalChart(candidates, data, polarity=0):
    # Make n_groups number of bars
    n_groups = len(data)

    # Get the data by finding the pos, neg values for each candidate
    dat = []
    for candidate in candidates:
        l = data.get(candidate)
        pos, neg, total = getTally(l,polarity)
        dat.append((candidate,pos/total,neg/total,(total-pos-neg)/total))
    
    # Gen display values
    approval = [approval for (candidate,approval,disapproval,unsure) in dat]
    disapproval = [disapproval for (candidate,approval,disapproval,unsure) in dat]
    unsure = [unsure for (candidate,approval,disapproval,unsure) in dat]

    fig, ax = plt.subplots()

    index = np.arange(n_groups)
    bar_width = 0.25

    opacity = 0.4   
    error_config = {'ecolor': '0.3'}

    # Make bars for approval rating
    rects1 = ax.bar(x = index, 
                    height = approval, 
                    width = bar_width,
                    alpha = opacity, 
                    color = 'g',
                    error_kw = error_config,
                    label = 'Approval')

    # Make bars for disapproval rating
    rects2 = ax.bar(x = index + bar_width, 
                    height = disapproval, 
                    width = bar_width,
                    alpha = opacity, 
                    color = 'r',
                    error_kw = error_config,
                    label = 'Disapproval')

    # Make bars for neutral rating
    if polarity > 0:
        rects3 = ax.bar(x = index + 2*bar_width, 
                        height = unsure, 
                        width = bar_width,
                        alpha = opacity, 
                        color ='#9F9F9F',
                        error_kw = error_config,
                        label = 'Neutral')

    # Label graph with important info
    ax.set_xlabel('Candidates')
    ax.set_ylabel('Ratings')
    ax.set_title('Direct Approval Ratings from Twitter')
    if polarity > 0:
        ax.set_xticks(index + bar_width)
    else:
        ax.set_xticks(index + bar_width / 2)
    
    labels = [c.capitalize() for (c,a,d,u) in dat]
    ax.set_xticklabels(labels)
    ax.legend()

    labelValues(ax,rects1)
    labelValues(ax,rects2)
    if polarity > 0:
        labelValues(ax,rects3)

    fig.tight_layout()
    plt.show()

def makeFollowerBracketsNum(candidate,brackets):
    # Find population for each follower bracket by getting length of each bracket
    data = [len(a) for a in brackets]
    n_groups = len(data)

    fig, ax = plt.subplots()

    index = np.arange(n_groups)
    bar_width = 0.35

    opacity = 0.4   
    error_config = {'ecolor': '0.3'}

    b = ax.bar(x = index,
               height = data,
               width = bar_width,
               alpha= opacity,
               color='g',
               error_kw=error_config,
               label='Approval')

    # Label graph with important info
    ax.set_xlabel('Brackets')
    ax.set_ylabel('Population')
    ax.set_title('Population of each bracket of Followers for ' + candidate.capitalize())
    ax.set_xticks(index)
    
    labels = ["[0,10)","[10,100)","[100,1000)","[1000,10000)","[10000,100000)","[100000,infinity)"]
    ax.set_xticklabels(labels)
    
    labelValues(ax,b,makeInt=True)

    fig.tight_layout()
    plt.show()

def findSentimentOfBrackets(brackets):
    data = []
    for a in brackets:
        pos, _, total = getTally(a)
        data.append((pos/total))
    return data

def makeFollowerBracketsApproval(candidate, brackets):
    data = findSentimentOfBrackets(brackets)
    n_groups = len(data)

    fig, ax = plt.subplots()

    index = np.arange(n_groups)
    bar_width = 0.35

    opacity = 0.4   
    error_config = {'ecolor': '0.3'}

    b = ax.bar(x = index,
               height = data,
               width = bar_width,
               alpha=opacity,
               color='g',
               error_kw=error_config,
               label='Approval')

    ax.set_xlabel('Brackets')
    ax.set_ylabel('Ratings')
    ax.set_title('Direct Approval Ratings from Twitter per bracket for ' + candidate.capitalize())
    ax.set_xticks(index)
    
    labels = ["[0,10)","[10,100)","[100,1000)","[1000,10000)","[10000,100000)","[100000,infinity)"]
    ax.set_xticklabels(labels)
    
    labelValues(ax,b)

    fig.tight_layout()
    plt.show()

def makeVerifiedApproval(candidate, data):
    nonVerified, verified = makeVerifiedBrackets(data)

    posN, negN, totalN = getTally(nonVerified)
    posV, negV, totalV = getTally(verified)
    data1 = [posN/totalN,posV/totalV]
    data2 = [negN/totalN,negV/totalV]

    n_groups = 2

    fig, ax = plt.subplots()

    index = np.arange(n_groups)
    bar_width = 0.35

    opacity = 0.4   
    error_config = {'ecolor': '0.3'}

    rects1 = ax.bar(x = index, 
                    height = data1, 
                    width = bar_width,
                    alpha=opacity, 
                    color='g',
                    error_kw=error_config,
                    label='Approval')

    rects2 = ax.bar(x = index + bar_width, 
                    height = data2, 
                    width = bar_width,
                    alpha=opacity, 
                    color='r',
                    error_kw=error_config,
                    label='Disapproval')

    ax.set_xlabel('Users')
    ax.set_ylabel('Ratings')
    ax.set_title('Direct Approval Ratings from Twitter for ' + candidate.capitalize())
    ax.set_xticks(index + bar_width / 2)
    
    ax.set_xticklabels(['Unverified','Verified'])
    ax.legend()
    
    labelValues(ax,rects1)
    labelValues(ax,rects2)

    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    startTime = float(time.time())
    candidates = ["bernie","biden","harris","warren","trump"]

    # Determine if sentiment analysis has been done
    s = str(input("Have you done analysis on the data?"))
    # If it has, get the data and display it
    if s == "y":
        data = {}
        # Get the data for each of the candidates
        for candidate in candidates:
            filename = str(candidate + "sent.txt")
            l = getAllTweets(filename,True)
            data[candidate] = l
    # Otherwise do sentiment analysis
    else:
        data = lotsOfAnalysis(candidates)
    print("Displaying data...")
    # For each candidate
    for candidate in candidates:
        # Get data of candidate
        l = data.get(candidate)
        # Make a bracket for followers
        bracket = makeFollowerBrackets(l)
        # Plot the distribution of the population of tweets by follower count
        makeFollowerBracketsNum(candidate,bracket)
        # Plot each brackets approval rating of candidate
        makeFollowerBracketsApproval(candidate,bracket)
        # Plot approval among nonverified and verified users
        makeVerifiedApproval(candidate,l)
    # Plot aggregate data for all candidates
    makeBarApprovalChart(candidates,data)
    makeBarApprovalChart(candidates,data,.1)
