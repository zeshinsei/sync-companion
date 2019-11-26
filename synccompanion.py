import logging
import sys
import argparse
import common
import configparser
import logger
import reddit
import re
import checklog
from datetime import datetime

### Script arguments ###
parser = argparse.ArgumentParser()
parser.add_argument("subname", help="Name of subreddit")
args = parser.parse_args()

### Config ini vars ###
config = configparser.ConfigParser()
config.read('config.ini')
debug_mode = config['DEFAULT'].getboolean('DebugMode')
logger.initialize(args.subname)
logmsg = logging.getLogger("Rotating_Log")

### Handles main segment ###
def main():
   if not re.match(r'^[A-Za-z0-9_]+$', args.subname):
      sys.exit("Invalid subreddit name, aborting.")
   s = reddit.reddit.subreddit(args.subname)
   common.debug_msg('Mod Permission: ' + str(s.user_is_moderator))
   if not s.user_is_moderator:
      logmsg.critical("[ERROR] Bot check as mod failed, aborting.")
      sys.exit("Shutting down due to bot permission issue.")
   checklog.check_for_admins(s)
   if not common.bool_sidebar_queued(s):
      sys.exit("Shutting down due to no need to run bot, no new sidebar content found.")
   new_sidebar = common.sync_sidebar_widget(s)
   sidebar_state = common.check_sidebar_freespace(s.display_name,new_sidebar)
   if not debug_mode:
      try:
         s.mod.update(description=new_sidebar)
      except Exception as e:
         logmsg.critical("[ERROR] Updating sidebar - %s", e)
   common.debug_msg("Bot run has completed. API usage: " + str(reddit.reddit.auth.limits))
   configname = 'SysLastRun' + s.display_name
   currentrun = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
   config['DEFAULT'][configname] = currentrun
   with open('config.ini', 'w') as configfile:
      config.write(configfile)

### Start the script ###
if __name__ == '__main__':
    main()

