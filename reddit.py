### This file creates the instance of Reddit and authenticates ###

import praw
import sys

sub = sys.argv[1]

reddit = praw.Reddit(sub, user_agent='SyncCompanion bot')
