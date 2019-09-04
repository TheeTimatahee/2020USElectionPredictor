import json

def getNewTweet(filename,lineNum=0):
    """Reads line number 'lineNum' from 'filename',
    then converts that string into a dictionary.
    
    Will return the first line in 'filename' if line
    number is not specified

    Returns an empty dictionary if the specificed
    line number doesn't exist"""
    s = None

    # Opens file for reading
    f = open(filename,"r")
    # Loops through each line in f
    for i, line in enumerate(f):
        # Checks if the current line is the line we want
        if(i == lineNum):
            # If it is, set s to the line, which is a string
            s = line
            break
    f.close()

    # Parse the string representation of the dictionary and return that
    # Returns an empty dictionary in case the specified line doesn't exist
    return strToDict(s)

def getAllTweets(filename,isSent=False):
    """Returns all of the tweets in 'filename' as an
    array of dictionaries"""
    arrayOfTweets = []

    # Opens file for reading
    f = open(filename, "r", encoding="utf8")#, errors='ignore')
    # Loops through each line in f
    print("Parsing...")
    for i, line in enumerate(f):
        # Parses the string representation of the dictionary to an actual dictionary
        dictionary = strToDict(line,isSent)
        # Add the dictionary to the list
        arrayOfTweets.append(dictionary)
    f.close()
    # except:
    #     print(filename)

    # Find length of the list before removing None values
    total = len(arrayOfTweets)
    # Remove any None values from the list (None where a tweet could not be parsed)
    arrayOfTweets = [tweet for tweet in arrayOfTweets if tweet is not None]
    # Find number of invalid tweets
    tweetsRemoved = total - len(arrayOfTweets)
    # Find percentage of invalid tweets
    tweetsRemovedPercent = 100*(round((tweetsRemoved/total), 4))

    print("Parsing Complete")
    print("Total Tweets: " + str(len(arrayOfTweets)))
    print("Tweets unable to be parsed: " + str(tweetsRemoved) + ", " + str(tweetsRemovedPercent) + "%")
    return arrayOfTweets

def strToDict(s,isSent=False):
    """Parses a string representation of a dictionary to an actual dictionary"""
    # In case that s is None, return empty dictionary
    if(s is None):
        return dict({})

    i = -1
    try:
        # Checks if the coords key is empty
        i = s.index("None")
    except: # If it isn't, continue
        pass
    # If i != -1, than coords must be empty
    if i != -1:
        # Remove this element from the dictionary, as it is not needed
        s = s.replace("'coords': None, ", "")
    # Finds the index of the text portion of the tweet
    i = s.index("'text': ") + 9
    # Find the index of the end of the dictionary
    if isSent:
        ie = s.index("'polarity'") - 3
    else:
        ie = s.index("}") - 1
    # Get the text portion of the tweet as a string
    text = s[(i):(ie)]
    # Remove the text from the dictionary temporarily
    s1 = s.replace(text,'')
    # Replace all single quotes with double quotes, so json can parse the string to a dictionary
    # This is why we removed the text, as some text has single quotes that shouldn't be replaced with double quotes
    json_acceptable_string = s1.replace("'", "\"")
    
    # Add the text back into the string representation of the dictionary
    snew = json_acceptable_string[:i] + text + json_acceptable_string[i:]

    snew = snew.replace("False","false")
    snew = snew.replace("True","true")

    try:
        # Tries to parse the string representation of the dictionary
        # Returns it if it can
        return json.loads(snew)
    except:
        # In case it can't, throw away tweet and return None
        return None

if __name__ == "__main__":
    d = getAllTweets("tweets.txt")
    print(d)

# I'm keeping this function here for completeness sake, and if I ever figure out how to make it work
# For now, it's not functional and should not be used

# def fixQuotedText(text):
#     """Function that is supposed to fix tweets with quoted text; NOT FUNCTIONAL"""
#     start = 0
#     ee = []

#     try:
#         i = text.index("\"")
#         stillQuotes = True
#     except ValueError:
#         return text
#     while(stillQuotes):
#         i = text.index("\"")
#         print(str(i))
#         t1 = text[start:(i)]
#         ee.append(t1)
#         ee.append("\"")
#         start = 0
#         print(str(t1))
#         text = text[(i+1):] #t1 + "\"" + text[(i+1):]
#         print(text)
#         try:
#             i = text.index("\"")
#         except ValueError:
#             stillQuotes = False

#     return ''.join(ee)