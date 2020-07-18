import logging
import sys
import argparse
import common
import configparser
import logger
import reddit
import re
import checklog
import core
import time
from datetime import datetime

### Script arguments ###
parser = argparse.ArgumentParser()
parser.add_argument("subname", help="Name of subreddit")
args = parser.parse_args()

### Setup the logging ###
logger.initialize(args.subname)
logmsg = logging.getLogger("Rotating_Log")

### Handles main segment ###
def main():
   if not re.match(r'^[A-Za-z0-9_]+$', args.subname):
      sys.exit("Invalid subreddit name, aborting.")
   s = reddit.reddit.subreddit(args.subname)
   config = core.get_config()
   debug_mode = config['DEFAULT'].getboolean('DebugMode')
   common.debug_msg('Mod Permission: ' + str(s.user_is_moderator))
   if not s.user_is_moderator:
      logmsg.critical("[ERROR] Bot check as mod failed, aborting.")
      sys.exit("Shutting down due to bot permission issue.")
   checklog.check_for_admins(s)
   checklog.health_check(s)
   common.cleanup_modmail(s)
   if not common.bool_sidebar_queued(s):
      sys.exit("No sync needed, no new sidebar content found.")
   new_sidebar = common.sync_sidebar_widget(s)
   sidebar_state = common.check_sidebar_freespace(s.display_name,new_sidebar)
   if not debug_mode:
      try:
         s.mod.update(description=new_sidebar)
      except Exception as e:
         logmsg.critical("[ERROR] Updating sidebar - %s", e)
   common.debug_msg("Bot run has completed. API usage: " + str(reddit.reddit.auth.limits))
   if not debug_mode:
      configf = configparser.ConfigParser()
      configf.read('config.ini')
      configname = 'SysLastRun' + s.display_name
      currentrun = datetime.utcnow().strftime(configf['DEFAULT']['lastrunformat'])
      configf['DEFAULT'][configname] = currentrun
      usern = "u_" + reddit.reddit.user.me().name
      statusmsg = "Bot last online " + currentrun + " UTC. "
      if checklog.check_log_errors(s):
         statusmsg = statusmsg + "❌Errors seen today."
      else:
         statusmsg = statusmsg + "✔️No errors today."
      reddit.reddit.subreddit(usern).mod.update(public_description=statusmsg)
      with open('config.ini', 'w') as configfile:
         configf.write(configfile)

def bot_loop():
   """Run the bot indefinitely."""
   if not re.match(r'^[A-Za-z0-9_]+$', args.subname):
      sys.exit("Invalid subreddit name, aborting.")
   s = reddit.reddit.subreddit(args.subname)
   config = core.get_config()
   debug_mode = config['DEFAULT'].getboolean('DebugMode')
   common.debug_msg('Mod Permission: ' + str(s.user_is_moderator))
   if not s.user_is_moderator:
      logmsg.critical("[ERROR] Bot check as mod failed, aborting.")
      sys.exit("Shutting down due to bot permission issue.")
   running = True
   common.debug_msg("Starting bot...")
   s = reddit.reddit.subreddit(args.subname)
   while running:
      try:
         #TODO main loop
         for submission in s.stream.submissions(skip_existing=False):
            common.debug_msg('Found submission ' + submission.title)
      except KeyboardInterrupt:
         print('Keyboard Interrupt. Ending bot.')
         running = False
      except Exception as e:
         print('Exception raised per below. Attempting to continue bot in 10 seconds.')
         logmsg.critical('Exception raised per below. Attempting to continue bot in 10 seconds.')
         print(e)
         logmsg.critical(e)
         time.sleep(10)
   return 0


### Start the script ###
if __name__ == '__main__':
    main()

