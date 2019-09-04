#!/usr/bin/python3
import twitter
import sys
import time
import pickle
from urllib.error import URLError
from http.client import BadStatusLine
import networkx as nx
from threading import Thread

try:
    from blessings import Terminal
    term = Terminal()
except ImportError:
    term = None

# TODO: implement Stoppable Thread

class Tweeter:
    ''' A class for storing useful information about Twitter users '''
    def __init__(self, name, uid, fr_count, fo_count):
        self.name = name
        self.uid = uid
        self.fr_count = fr_count
        self.fo_count = fo_count

    # Below functions for compatibility with NetworkX
    def __hash__(self):
        return self.uid

    def __eq__(self, other):
        return self.uid == other

    def __repr__(self):
        return "Tweeter(name=%r, uid=%r, fr_count=%r, fo_count=%r)" %\
                (self.name, self.uid, self.fr_count, self.fo_count)

    def __str__(self):
        return "@" + self.name

error_sep = '*'*50
def make_twitter_request(func, max_errors=10, *args, **kwargs):
    ''' 
    A wrapper for handling Twitter requests, errors and rate limits 
    Credit to TwitterCookbook
    '''
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
        if wait_period > 3600: # seconds
            print('Too many retries. Quitting', file=sys.stderr)
            raise e
        if e.e.code == 401:
            print(error_sep)
            print('* Encountered 401 Error (Not Authorized)', file=sys.stderr)
            print(error_sep)
            return None
        elif e.e.code == 404:
            print(error_sep)
            print('* Encountered 404 Error (Not Found)', file=sys.stderr)
            print(error_sep)
            return None
        elif e.e.code == 429:
            if sleep_when_rate_limited:
                if term: start_countdown()
                print(error_sep)
                print('* Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
                print('* Current time: {}'.format(time.strftime('%T')))
                print('* Retrying in 15 minutes...ZzZ...', file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print('* ...ZzZ...Awake now and retrying.', file=sys.stderr)
                print(error_sep)
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
                print(error_sep)
        elif e.e.code in (500, 502, 502, 504):
            print(error_sep)
            print('* Encountered {0} Error. Retrying in {1} seconds'.format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e
    # End of http error handler

    wait_period = 2
    error_count = 0

    while True:
        try:
            return func(*args, **kwargs)
        except twitter.api.TwitterHTTPError as e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print('URLError encountered. Continuing.', file=sys.stderr)
            if error_count > max_errors:
                print('Too many consecutive errors...bailing out.', file=sys.stderr)
                raise
        except BadStatusLine as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print('BadStatusLine encountered. Continuing.', file=sys.stderr)
            if error_count > max_errors:
                print('Too many consecutive errors...bailing out.', file=sys.stderr)
                raise

# Graph import/export functions
def graph2bin(nodes):
    '''Store a graph into a file'''
    with open('nodes.bin', 'wb') as f:
        pickle.dump(nodes, f)

def bin2graph(filename):
    '''Get a graph from a file'''
    with open(filename, 'rb') as f:
        nodes = pickle.loads(f.read())
    return nx.DiGraph(nodes)

def bin2dict(filename):
    '''Get a dict representing the graph store in a file'''
    return nx.to_dict_of_lists(bin2graph(filename))

# Terminal functions
def init_term():
    '''Enables nice printing using blessings if installed'''
    if term: print(term.clear)
    return term

sep = '#'*75
def print_header(start=0):
    '''Print uptime, header, and countdown for rate limit timeout if applicable'''
    global node_count, queue_count, iteration, countdown
    node_count = queue_count = iteration = 1
    countdown = None
    print(term.clear)
    print(term.move_y(3))
    def timer_func(term, start):
        global node_count, queue_count, iteration, countdown
        # Print every second using the top 3 lines
        while True:
            with term.location():
                print(term.move_y(0) + term.clear_eol, end='')
                print('Stream uptime:', time.strftime('%H:%M:%S', time.gmtime(time.time() - start)), end='')
                if countdown:
                    print('  |  Rate Timeout:', time.strftime("%M:%S", time.gmtime(countdown)))
                    countdown -= 1
                    if countdown == -1: countdown = None
                else: 
                    print()
                print(term.clear_eol, end='')
                print('Total nodes = {} | Next queue = {} | Iteration #{}'.format(node_count, queue_count, iteration))
                print(sep)
            time.sleep(1)
    # Start timer thread
    uptimer = Thread(target=timer_func, args=(term, start), daemon=True)
    uptimer.start()

def start_countdown(duration=60*15):
    '''Start a countdown for `duration` seconds (default is 15 minutes'''
    global countdown
    countdown = duration

def update_header(nc=None, qc=None, it=None):
    '''Update header information (node count, queue count, and iteration number)'''
    global node_count, queue_count, iteration
    if nc: node_count = nc
    if qc: queue_count = qc
    if it: iteration = it





