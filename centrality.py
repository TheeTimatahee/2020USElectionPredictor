#!/usr/bin/python3
import twitter
import time
from functools import partial
import networkx as nx
import matplotlib.pyplot as plt
from utility import *

term = init_term()

'''
Creates a network of Twitter users using a directed graph and 
    uses Katz centrality (with beta = scaled follow count) to
    determine the most influential accounts.
The network graph is stored as a dict of lists {k:v} where
    k = <Tweeter> node
    v = <List of Tweeter> out-edges of k
'''

SEED = 'berniesanders' # Twitter user to start network at
NODE_LIMIT = 50 # Max size of network graph
MIN_FOLLOW_COUNT = 1000000 # Min num of followers for nodes in graph
FETCH_LIMIT = 75000 # Max num of friends to query for each node
MAX_DEPTH = 3 # Max number of levels to traverse, 0 for unlimited
MODE = 'crawl'

# For nice printing
sep = '#'*75
second_sep = '-'*50

#c_key = None
#c_sec = None
#a_tok = None
#a_sec = None
c_key = your key here
c_sec = your key here
a_tok = your key here
a_sec = your key here

blacklist = ['Twitter','biz','mashable','OhMyCorgi','BuzzFeed','TMZ','verified','NFL','THR','SportsCenter','Eagles','ESPNNFL','SamsungMobileUS']

def oath_login():
    ''' Returns a Twitter obj with authentication '''
    auth = twitter.oauth.OAuth(a_tok, a_sec, c_key, c_sec)
    api = twitter.Twitter(auth=auth)
    return api

api = oath_login()

# Filter functions for get_node_list()
def min_follow_filter(user_dict):
    ''' Returns True if follow_count >= MIN_FOLLOW_COUNT ''' 
    return user_dict['followers_count'] >= MIN_FOLLOW_COUNT

def blacklist_filter(user_dict):
    ''' Returns True if min_follow_filter() and if user not in blacklist '''
    return min_follow_filter(user_dict) and user_dict['screen_name'] not in blacklist

def cleanup_filter(user_dict):
    ''' Returns True if user exists in network already '''
    return user_dict['screen_name'] in nodes

# Twitter functions
def get_node_list(twtr, get_func, filt=blacklist_filter):
    '''
    Returns a list of users `twtr` follows who pass `filt` function
        Default `filt` is blacklist_filter()
        Uses either partial func of api.friends.list or api.followers.list
    '''
    fetched_count = 0
    users = []
    cursor = -1
    while cursor != 0:
        r = get_func(cursor=cursor, user_id=twtr.uid)
        if not r: 
            print(error_sep, '\nSomething  happened: Response was None\n', error_sep)
            break
        # Keep users that pass filter as Tweeter obj
        checked_users = [Tweeter(u['screen_name'], u['id'], u['friends_count'], u['followers_count'])
                for u in r['users'] if filt(u)]
        users += checked_users
        fetched_count += len(r['users'])
        print('\n{:,} total friends fetched\n\t\t{:,} total pass criteria'
                .format(fetched_count, len(users)))
        # Stop if fetch limit exceeded
        if fetched_count >= FETCH_LIMIT: break
        cursor = r['next_cursor']
    # Return the found users
    return users

def friendships_show(u1, u2):
    ''' 
    Returns True if user 1 follows user 2 
        <https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show>
    '''
    print(second_sep, '\nfriendships.show')
    rel = make_twitter_request(api.friendships.show, source_id=u1, target_id=u2)
    return rel['relationship']['source']['following']

def clean_up(nodes, remaining):
    '''
    Check if `user` follows anyone one already in network (don't get new nodes)
        Use api.friendships.show for most connections because `len(nodes)` is usually less than `user.fr_count`
        Use api.friends.list if `user.fr_count` is less than 1500 ((200 result limit per req) * (10 req out of 15 req limit per 15 min))
    '''
    print(sep)
    print('Max nodes reached, cleaning up now')
    len_r = len(remaining)
    if term: update_header(nc=len(temp_nodes))
    # Check all remaining for connections to those already in network
    #   i.e., don't add new nodes
    friends = {}
    for i,u in enumerate(remaining):
        if term: update_header(qc=len_r)
        print('Cleaning up {}: ({:,} followers, {:,} friends)'.format(u, u.fo_count, u.fr_count))
        if u.fr_count <= 1500: # If friend count small enough, check friend in nodes for all friends
            friends.update({u:friends_list(u, filt=cleanup_filter)})
            #friends = friends_list(u, filt=cleanup_filter)
        else: # Else, just check if check if the user is friends with anyone already in the network
            friends.update({u:[u2 for u2 in nodes if friendships_show(u.uid, u2.uid)]})
            #friends = [ u2 for u2 in nodes if friendships_show(u.uid, u2.uid) ]
        len_r -= 1
    # Return entries to add/update in main nodes dict
    return {user: friends}

# Network functions
def get_network(get_func, seed=SEED):
    '''
    Returns a network built from a directed graph 
    '''
    global  nodes
    # Initialize with seed user
    u = api.users.show(screen_name=seed)
    tweeter = Tweeter(u['screen_name'], u['id'], u['friends_count'], u['followers_count'])
    # Set up for the main loop
    next_q = [tweeter]
    nodes = {tweeter:[]}
    node_count = iteration = 1
    start = time.time()
    if term: print_header(start)
    # Main loop
    while node_count < NODE_LIMIT and iteration < MAX_DEPTH:
        # q = current queue, next_q = q for next loop
        (q, next_q) = (next_q, [])
        for twtr in q:
            # Get filtered friends/followers and add to edge list)
            print('Getting nodes for {} ({:,} followers, {:,} friends):'
                    .format(twtr, twtr.fo_count, twtr.fr_count))
            filtered = get_node_list(twtr, get_func)
            nodes.update({twtr: filtered})
            # Add newly found nodes (not already in nodes or next_q) to nodes
            next_q += [ t for t in filtered if t not in nodes and t not in next_q ]
            node_count += len(next_q)
            if term: update_header(nc=node_count)
            if NODE_LIMIT < node_count:
                # Nodes to cleanup are those after twtr in q and all of next_q
                remaining = q[q.index(twtr)+1] + next_q
                if len(remaining) == 0: break
                # ntwk_nodes is all the users in the network (nodes + next_q)
                ntwk_nodes = list(nodes.keys()) + next_q
                nodes.update(clean_up(ntwk_nodes, remaining))
                break
        # If no new users found, exit
        if len(next_q) == 0: break
        iteration += 1
    print('\nFinished gathering network nodes')
    print('Total time elapsed is', time.strftime("%H:%M:%S",
        time.gmtime(time.time() - start)))
    return nodes

def create_network(seed):
    '''
    Fetches friends using api.friends.list: 15req/15min, returns up to 200 friends of `twtr` at a time
    <https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friends-list>
    '''
    friends_func = partial(make_twitter_request, api.friends.list, count=200, skip_status='true', include_user_entities='false')
    nodes = get_network(friends_func, seed=seed)
    # Store nodes in 'nodes.bin' file
    graph2bin(nodes)
    ntwk = nx.DiGraph(nodes)
    analyze_network(ntwk)
    graph_network(ntwk)

def crawl_network(seed):
    '''
    Fetches followers using api.followers.list: 15req/15min, returns up to 200 followers of `twtr` at a time
    <https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-followers-list>
    '''
    follow_func = partial(make_twitter_request, api.followers.list, count=200, skip_status='true', include_user_entities='false')
    nodes = get_network(follow_func, seed=seed)
    # Store nodes in 'nodes.bin' file
    graph2bin(nodes)
    ntwk = nx.DiGraph(nodes)

    u = api.users.show(screen_name=seed)
    tweeter = Tweeter(u['screen_name'], u['id'], u['friends_count'], u['followers_count'])
    score = get_centrality_score(tweeter, g)
    return score

def analyze_network(g):
    ''' Prints out useful information about a (assumed directed) graph '''
    print(sep, '\nAnalysis of network\n', sep)
    # Calculate Katz centrality
    #   beta will be a scaled follower count
    beta = { t: round(t.fo_count/10000000, 2)+1
            for t in nodes.keys() }
    print('beta dict')
    print(beta)
    katz_centrality = nx.katz_centrality(g, alpha=0.85, beta=beta)
    print('Nodes by Katz Centrality:')
    for k,v in sorted(katz_centrality.items(), key=lambda k:k[1], reverse=True):
        # Prints as '(katz_centrality)  (follower_count)  (screen_name)'
        print(v, '\t{:>15,d}'.format(k.fo_count), '\t', k)

def get_centrality_score(user, g):
    beta = { t: round(t.fo_count/10000000, 2)+1
            for t in nodes.keys() }
    katz_centrality = nx.katz_centrality(g, alpha=0.85, beta=beta)
    return katz_centrality[user]


def graph_network(g):
    ''' Draw a graph using matplotlib and save picture as "network.png" '''
    nx.draw(g, with_labels=True)
    plt.savefig('network.png')
    plt.show()

# Main
def main(seed=SEED, mode=MODE):
    '''
    Create/crawl a network and perform analysis on it
    seed = user name to start network at
    mode = 'create' or 'crawl' a network, see create_ and crawl_network for details
    '''
    if mode not in ['crawl', 'create']:
        print('mode argument invalid, exiting')
        return
    global term
    if mode == 'crawl': crawl_network(seed=seed)
    else: create_network(seed=seed)
    graph_network(ntwk)

if __name__ == '__main__': main()

