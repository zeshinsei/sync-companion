import praw
import logging
import sys
import re #remove
import argparse
import common
import configparser
import logger
import reddit
#### If you have an addon for a specific feature or game integration, import it here ###
#try:
   #import xi
#except ImportError:
   #pass
try:
   import xiv
except ImportError:
   pass

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
   s = reddit.reddit.subreddit(args.subname)
   common.debug_msg('Mod Permission: ' + str(s.user_is_moderator))
   if not s.user_is_moderator:
      logmsg.critical("[ERROR] Bot check as mod failed, aborting.")
      sys.exit("Shutting down due to bot permission issue.")
   if args.subname == "ffxiv": #sanitize
      update_sidebar('test',s)
   else:
      new_sidebar = common.sync_sidebar_widget(s)
      sidebar_state = common.check_sidebar_freespace(s.display_name,new_sidebar)
      if not debug_mode:
         try:
            s.mod.update(description=new_sidebar)
         except Exception as e:
            logmsg.critical("[ERROR] Updating sidebar - %s", e)
   common.debug_msg("Script has finished.")
   logmsg.info("Bot run has completed. API usage: %s", reddit.reddit.auth.limits)


### Updates subreddit sidebar, legacy code. ###
#sanitize/remove
def update_sidebar(body, subr):
   template = subr.wiki['sidebar'].content_md
   new_sidebar = template
   settings = subr.mod.settings()
   ### Update news etc
   news = xiv.obtain_lodestone('topics')
   new_sidebar = template.replace("%%EVENTS%%",news)
   maints = xiv.obtain_lodestone('maintenance')
   new_sidebar = new_sidebar.replace("%%MAINT%%",maints)
   notices = xiv.obtain_lodestone('notices')
   new_sidebar = new_sidebar.replace("%%NOTICES%%",notices)
   #updates = xiv.obtain_lodestone('updates')
   #new_sidebar = new_sidebar.replace("%%UPDATES%%",updates)
   #statuses = xiv.obtain_lodestone('status')
   #new_sidebar = new_sidebar.replace("%%STATUSES%%",statuses)
   devblog = xiv.obtain_lodestone('developers')
   new_sidebar = new_sidebar.replace("%%DEVBLOG%%",devblog)
   #devoforums = xiv.obtain_lodestone('devposts')
   #new_sidebar = new_sidebar.replace("%%DEVOFORUMS%%",devoforums)
   ### Update world status
   worldstatus = xiv.get_worldstatus()
   statusstr = worldstatus + "**](http://arrstatus.com/#" + worldstatus + ")"
   new_sidebar = new_sidebar.replace("%%SERVERS%%",statusstr)
   ### Update countdown timer
   timer_ct = 0
   while timer_ct < 9:
      countdown_string = re.search('%%CD_(\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2})_CD%%', new_sidebar)
      if countdown_string is None:
         break
      countdown_target = countdown_string.group(1)
      updated_countdown = common.calc_countdown(countdown_target)
      new_sidebar = re.sub(r'%%CD_(\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2})_CD%%', updated_countdown, new_sidebar, 1)
      timer_ct += 1
   sidebar_state = common.check_sidebar_freespace(subr.display_name,new_sidebar)
   if not debug_mode:
      subr.mod.update(description=new_sidebar)
   common.debug_msg(reddit.reddit.auth.limits)


### Start the script ###
if __name__ == '__main__':
    main()

