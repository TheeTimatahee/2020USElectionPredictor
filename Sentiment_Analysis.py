#CIS400 - Data Mining Term Project
#Group: Jay, Tim, Aiden, Alan
#Project: Predicting 2020 presidential election
from analysisTools import getAllTweets
import time
from miner import secToHMS
#List of unclean tweets as strings
datasetD = []             
datasetR = []  

testDataSet = ["Deep Dreaming Bob Ross Cat: The Library of my new Dutch management movement: Human desires. Cost!",
               "It's only a gambling addiction if you keep losing, otherwise it's a high paying career.",
               "Mark Zukerberg used to be a hero of the digital age, but now he has lived long enough to see himself become the villain",
               "I'm happy for you",
               "I loath you with every fiber of my being"
              ]

testDataSet2 = ["Thanks for coming",
                "#FollowFriday @France_Inte @PKuchly57 @Milipol_Paris for being top engaged members in my community this week :)"
               ]

#Data Preprocessing Section ~ Utilities

#Remove duplicates from the list
def remove_duplicates_list(dataset): 
    #keys of dictionary must be unique -- duplicates are removed
    #Convert elements of list into dictionary keys
    #then convert back to a list
    dataset = list(dict.fromkeys(dataset))
    return dataset

#remove duplicate words in each string
#doesn't work entirely correctly until
#string has been properly tokenized (punctuation/spec chars 
#removed, while contractions are preserved)
def remove_duplicates_str(str):
    new_list = []
    #convert string into list of strings(words of string)
    split_list = str.split()
    #append string if not in new_list, otherwise ignore
    [new_list.append(x) for x in split_list if x not in new_list]
    #convert back to string and return string without duplicates
    return new_list

#tokenization -- convert text into tokens
#duplicate words handled here with above helper function

#from nltk.tokenize import word_tokenize
from nltk.tokenize import TweetTokenizer
def tokenize_str(str): 
    tokenizer = TweetTokenizer()
    tokenized_strList = tokenizer.tokenize(str)
    #remove duplicates of tweet
    tokenized_strList = " ".join(tokenized_strList)
    tokenized_strList = remove_duplicates_str(tokenized_strList)
    return tokenized_strList

#remove Stopwords -- words not relevant to context of data

from nltk.corpus import stopwords
def remove_sw(lst):
    tokenized_list = []
    #all stop words in the english language
    stop_words = stopwords.words('english')
    #append elements of old list to new list if 
    #they're not stop words
    [tokenized_list.append(x) for x in lst if x not in stop_words]
    return tokenized_list

#Normalization of data

#i.e. fifty    = 50
#     Rebelled = rebel
#     High     = high

from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

#Helper function to look up part-of-speech tag given
#i.e. to determine whether the word is an adj, noun, etc.
#reference: https://stackoverflow.com/questions/15586721/
#           wordnet-lemmatization-and-pos-tagging-in-python

def pos_tag_finder(corpus_tag): 
    if corpus_tag.startswith('J'):
        return wordnet.ADJ
    elif corpus_tag.startswith('V'):
        return wordnet.VERB
    elif corpus_tag.startswith('N'):
        return wordnet.NOUN
    elif corpus_tag.startswith('R'):
        return wordnet.ADV
    elif corpus_tag.startswith('S'):
        return wordnet.ADJ
    else:
        return ''

#To be run after tokenization/cleaning of data
#to be used for each string, i.e. list of words
import string
def normalize_data(lst):
    #Normalize casing of words
    lst = [x.lower() for x in lst]   
    #remove stand-alone punctuations/special characters
    #given they don't contribute to sentiment i.e. '!', 'II', ','
    #account for contractions
    new_list1 = []
    lst = " ".join(lst)
    lst = [x.strip(string.punctuation) for x in lst.split()]
    for x in lst:
        if (x != ''):
            new_list1.append(x)
    lst = new_list1
            
    #Lemmatize data -- normalization via context
    #1. find base/dict. form of a word (the lemma)
    #   -- dictionary importance
    #   -- morphological analysis (structure, grammar relation of word)
    #need to distinguish pos type for each word
    #in order for successful lemmatization i.e. verb, noun, adj, etc..
    lemmatizer = WordNetLemmatizer()    #inst. Lemmatizer obj. u
    lst_pos = pos_tag(lst)              #create list of tuples (word, nltk pos)
    new_list = []                       
    for x in lst_pos:
                                        #lemmatize word using wordnet (correct) pos 
                                        #converted from nltk pos with helper function
        pos_t = pos_tag_finder(x[1])
        if (pos_t == ''):
            continue
        w = lemmatizer.lemmatize(x[0], pos_tag_finder(x[1]))   
        if (w != ''):
            new_list.append(w)
    lst = new_list
    return lst
    #Example output: 
    #['fantasized', 'going', 'rocks', 'become'] -> ['fantasize', 'go', 'rock', 'become']


    #Sentiment Analysis of Data 
    #input: Raw tweet as string 
    #Will be cleaned/normalized using above functions
    #output: List[(Polarity, Subjectivity)...,...]
    #Note: Textblob doesn't handle contractions, which is why it's handled above

from textblob import TextBlob
from nltk.corpus import twitter_samples
from textblob.classifiers import NaiveBayesClassifier
from nltk import classify
#>>>import nltk
#>>>nltk.download('twitter_samples')
#Taking ideas from course lecture

def train_data():
    #Using the twitter_samples corpus to train TextBlob's NaiveBayesClassifier
    #i.e. Training Data Sets to be more accurate
    #The greater the train_set, the greater the accuracy
    #Save Classifier using nltk and pickle module?

    #some issues with classifying i.e. clearly pos tweet is marked neg
    positive_tweets = twitter_samples.strings('positive_tweets.json')
    negative_tweets = twitter_samples.strings('negative_tweets.json')
    positive_tweets_set = []
    for x in positive_tweets:
        positive_tweets_set.append((x, 'pos'))
    negative_tweets_set = []
    for x in negative_tweets:
        negative_tweets_set.append((x, 'neg'))
    test_set   = positive_tweets_set[:100] + negative_tweets_set[:100]
    train_set  = positive_tweets_set[100:300] + negative_tweets_set[100:300]
    classifier = NaiveBayesClassifier(train_set)
    print("\nAccuracy of classifer: "+str(classifier.accuracy(test_set)))
    print("Sample tweet: "+(positive_tweets_set[0])[0])
    return classifier

def Sent_Analysis(dic, shouldSaveData, candidate, classifier=train_data()):
    #Perform Sentiment Analysis
    for e in dic:
        x = e.get('text')
        twt_lst = tokenize_str(x)                   #tokenize tweet (account for contractions)
        twt_lst = remove_sw(twt_lst)                #remove stop words from tweet
        twt_lst = normalize_data(twt_lst)           #normalize/lemmatize 
        twt_lst = " ".join(twt_lst)
        cleaned_str = TextBlob(twt_lst,classifier=classifier) 
        sent = cleaned_str.sentiment
        # Add the polarity and sentiment to the tweet
        e['polarity'] = sent[0]
        e['sentiment'] = cleaned_str.classify()
        # Check user wants to save data
        if shouldSaveData:
            # Open file of data with polarity and sentiment added
            f = open(candidate + "sent.txt","a",encoding="utf8")
            f.write(str(e) + "\n")
            f.close()
    # Return the classified data set
    return dic

def lotsOfAnalysis(candidates):
    startTime = float(time.time())
    data = {}
    saveData = False
    s = str(input("Do you want to save the sentiment analysis data to a file for faster displaying later?"))
    if s == 'y':
        saveData = True
    # Get the data for each of the candidates
    for candidate in candidates:
        filename = str(candidate + ".txt")
        l = getAllTweets(filename)
        data[candidate] = l
    print("Data retreived. Beginning sentiment analysis...This is gonna take awhile...")
    # For each candidate
    for candidate in candidates:
        # Do sentiment analysis on data
        l = Sent_Analysis(dic=data.get(candidate),shouldSaveData=saveData,candidate=candidate)
        # Update the data with the sentiment of each tweet added
        data[candidate] =  l
        print("Analysis for " + candidate.capitalize() + " done")
    print("Analysis complete.")
    deltaT = float(time.time()) - startTime
    (h,m,s) = secToHMS(deltaT)
    print("Time to output: " + h + ":" + m + ":" + s)
    return data

if __name__ == "__main__":
    candidates = ["bernie","biden","harris","warren","trump"]
    lotsOfAnalysis(candidates)