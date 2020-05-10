import configparser
import sys
import reddit

### Return the current subreddit name ###
def get_subreddit():
   return sys.argv[1]

### Read from the config ###
def get_config():
   config = configparser.ConfigParser()
   s = reddit.reddit.subreddit(get_subreddit())
   configdata = s.wiki['sync_config'].content_md
   config.read_string(configdata)
   return config

