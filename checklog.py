from datetime import datetime, timedelta
import reddit
from common import debug_msg, alert_mods
import configparser

### Checks if modlog contains admin activity from Anti-Evil Operations, and modmails a warning if so. Returns False if none found ###
def check_for_admins(sub):
   found = False
   config = configparser.ConfigParser()
   config.read('config.ini')
   configname = 'SysLastRun' + sub.display_name
   lastrunstr = config['DEFAULT'][configname]
   lastrun = datetime.strptime(lastrunstr, '%Y-%m-%d %H:%M:%S')
   currentrun = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
   # TODO: this will always be false, as it's the last time the bot ran not the last admin check
   if (datetime.utcnow() - lastrun) < timedelta(1):
      debug_msg("Is within 24 hours, won't check.")
      return False

   bodystr = ""
   for log in sub.mod.log(limit=None,mod='a'):
       datestr = datetime.fromtimestamp(log.created_utc).strftime("%Y-%m-%d %H:%M:%S")
       # TODO: only alert on logs in last 24 hours
       bodystr = bodystr + "* " + str(log.mod) + " action at " + datestr + " UTC against /u/" + log.target_author + ": action [" + log.action + "]("+log.target_permalink+")\n"
       found = True

   if found:
      headerstr = "Admin activity was detected in the [modlog](https://www.reddit.com/r/" + sub.display_name + "/about/log/?mod=a). Review below to determine which Reddit content policy was violated, or if a false positive contact the admins.\n\n" + bodystr
      alert_mods(sub.display_name, 'Alert: admin activity in the modlog', headerstr)

   return found


#TODO: add a function here that checks if bot ran in last 24 hours
