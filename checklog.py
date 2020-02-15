from datetime import datetime, timedelta
import reddit
from common import debug_msg, alert_mods
import configparser
import logging
logmsg = logging.getLogger("Rotating_Log")


### Once a day, checks if modlog contains admin activity from Anti-Evil Operations; modmails a warning if so.
### Returns False if none found
def check_for_admins(sub):
   found = False
   config = configparser.ConfigParser()
   config.read('config.ini')
   configname = 'SysLastRun' + sub.display_name
   lastrunstr = config['DEFAULT'][configname]
   lastrun = datetime.strptime(lastrunstr, config['DEFAULT']['lastrunformat'])
   lastday = lastrun.day
   currentrun = datetime.utcnow().strftime(config['DEFAULT']['lastrunformat'])
   currentday = datetime.utcnow().day
   if lastday == currentday:
      debug_msg("Not a new day, won't check log.")
      return False

   bodystr = ""
   for log in sub.mod.log(limit=None,mod='a'):
       datestr = datetime.fromtimestamp(log.created_utc).strftime("%Y-%m-%d %H:%M:%S")
       if (datetime.utcnow() - datetime.fromtimestamp(log.created_utc)) < timedelta(1):
          bodystr = bodystr + "* " + str(log.mod) + " action at " + datestr + " UTC against /u/" + log.target_author + ": action [" + log.action + "]("+log.target_permalink+")\n"
          found = True

   if found:
      headerstr = "Admin activity was detected in the [modlog](https://www.reddit.com/r/" + sub.display_name + "/about/log/?mod=a). Review below to determine which Reddit content policy was violated, or if a false positive contact the admins.\n\n" + bodystr
      alert_mods(sub.display_name, 'Alert: admin activity in the modlog', headerstr)

   return found


### Once a day: Health check of the bot. If bot run has not completed in last 24 hours, returns False to indicate poor health ###
def health_check(sub):
   ### Revamp this, as condition where bot fails but still reaches end of main() can still occur.
   config = configparser.ConfigParser()
   config.read('config.ini')
   configname = 'SysLastRun' + sub.display_name
   lastrunstr = config['DEFAULT'][configname]

   with open(logmsg.handlers[0].baseFilename) as f:
      if 'Bot is in bad health state' in f.read():
         debug_msg("Bot previously in a bad health state, not sending modmail alert again today.")
         return True

   if (datetime.utcnow() - datetime.strptime(lastrunstr, config['DEFAULT']['lastrunformat'])) > timedelta(1):
      logmsg.critical("[ALERT] Bot is in bad health state, sent modmail alert.")
      alert_mods(sub.display_name, 'Alert: bot failed to run', 'Warning: This bot has failed to run at last attempt. If this repeats over multiple days, review the bot log files for more details.')
      return False
   return True
