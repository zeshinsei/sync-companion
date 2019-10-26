import configparser
from pprint import pprint
import sys
import logging
from datetime import datetime, timedelta, date
from twitch.api import v3
import urllib.request
import json
import praw
import re
import reddit
try:
   import xi
except ImportError:
   pass
try:
   import xiv
except ImportError:
   pass


config = configparser.ConfigParser()
config.read('config.ini')
logmsg = logging.getLogger("Rotating_Log")

### Outputs debug messages ###
def debug_msg(debug_str):
   if config['DEFAULT'].getboolean('DebugMode'):
      print("   <<<- [DEBUG]")
      if debug_str:
         pprint(debug_str)
      else:
         print("[WARNING] debug_msg: No data.")
      print("   [DEBUG] ->>>")


### Send us a modmail to alert something ###
def alert_mods(to, subject, body):
   tostr = '/r/'+to
   try:
      reddit.reddit.redditor(tostr).message(subject,body)
   except Exception as e:
      logmsg.critical("[ERROR] Cannot send modmail - %s", e)


### Get Reddit widget by name ###
def get_widget_by_name(sub, wname):
   try:
      widgets = sub.widgets
      for widget in widgets.sidebar:
         if wname == widget.shortName:
            return widget
   except Exception as e:
      logmsg.critical("[ERROR] Cannot find widget - %s", e)


### Calculate the countdown timer ###
def calc_countdown(targetdate):
   try:
      datetime_today = datetime.fromordinal(date.today().toordinal())
      delta = datetime.strptime(targetdate, '%Y-%m-%d %H:%M:%S') - datetime.now()
      hours_left = int(delta.seconds/(60*60))
      if delta.days == 1:
         total_hours = 24 + hours_left
         countdown_str = "{} hours".format(total_hours)
      elif delta.days > 1:
         countdown_str = "{} days".format(delta.days+1)
      elif delta.days == 0 and hours_left > 1:
         countdown_str = "{} hours".format(hours_left)
      elif delta.days == 0 and hours_left == 1:
         countdown_str = "{} hour".format(hours_left)
      elif delta.days == 0 and hours_left == 0:
         countdown_str = "At :00"
      else:
         countdown_str = "Arrived"
      return countdown_str
   except:
      logmsg.critical("[ERROR] Unable to calculate countdown: %s", e)
      return "?"


### Get list of Twitch streams ###
def get_twitch_streams(gamename):
   return "" # temp disabled while broken
   twitch_body = ""
   twitch_data = v3.streams.all(game=gamename)
   twitch_list = twitch_data['streams']
   ct = 0
   for a in twitch_list:
      viewers = a['viewers']
      twitch_dat = a['channel']
      twitch_body = twitch_body + '\n* [' + twitch_dat['display_name'] + '](' + twitch_dat['url'] + ')'
      twitch_body = twitch_body + ' ^((' + str(viewers) + ' viewers)^)'
      ct = ct + 1
      if ct >= int(config['DEFAULT']['ItemLimit'])*3:
         break
   if config['DEFAULT'].getboolean('DebugMode'):
      debug_msg(twitch_body)
   return twitch_body


### Get member count for a Discord server ###
def get_discord_online(id):
   discord = "https://discordapp.com/api/guilds/"+id+"/widget.json"
   uagent = config['DEFAULT']['UserAgent']
   req = urllib.request.Request(
       discord,
       data=None,
       headers={
           'User-Agent': uagent
       }
   )
   f = urllib.request.urlopen(req)
   data = f.read()
   encoding = f.info().get_content_charset('utf-8')
   objects3 = json.loads(data.decode(encoding))
   discord_ct = 0
   for o in objects3['members']:
      discord_ct = discord_ct + 1
   return discord_ct


### Sync sidebar and widgets based on sidebar_sync page ###
def sync_sidebar_widget(sub):
   template = sub.wiki['sidebar'].content_md
   new_sidebar = template
   settings = sub.mod.settings()
   syncdata = sub.wiki['sidebar_sync'].content_md
   sync_split = syncdata.split('####')
   for s_item in sync_split:
      if s_item:
         dynamic_content = None
         s_data = s_item.split('\r\n',1)
         headerfull = s_data[0]
         header_parts = headerfull.split('|')
         if len(header_parts) > 1:
            header_arg = header_parts[1]
         if len(header_parts) > 2:
            header_arg2 = header_parts[2]
         header = header_parts[0]
         title = header.replace("_"," ")
         sync_body = s_data[1]
         sync_body = sync_body.rstrip()
         header_rep = "%%"+header+"%%"
         sidebar_segment = sync_body
         if header == "Twitch_Streams":
            dynamic_content = get_twitch_streams(header_arg)
         elif header == "Discord_Info":
            dynamic_content = str(get_discord_online(header_arg))
         elif header == "Countdown":
            timer_ct = 0
            if timer_ct < int(config['DEFAULT']['NumCountdownLimit']):
               dynamic_content = calc_countdown(header_arg)
               timer_ct += 1
               title = header_arg2.replace("_"," ")
         elif header == "Server_Status":
            dynamic_content = handle_server_status(sub)
         elif header == "Latest_Topics" or header == "Topics":
            dynamic_content = handle_latest_blogs(sub, 'topics')
         elif header == "Server_News":
            dynamic_content = handle_latest_blogs(sub, 'news')
         elif header == "Notices":
            dynamic_content = handle_latest_blogs(sub, 'notices')
         elif header == "Maintenance":
            dynamic_content = handle_latest_blogs(sub, 'maintenance')
         if dynamic_content:
            new_sidebar = new_sidebar.replace(sidebar_segment,dynamic_content)
         else:
            debug_msg(header_rep + ": Inserting sidebar data= " + sidebar_segment)
            new_sidebar = new_sidebar.replace(header_rep,sidebar_segment)
         if dynamic_content:
            update_widget(sub, title, dynamic_content)
         else:
            update_widget(sub, title, sidebar_segment)
   debug_msg(new_sidebar)
   return new_sidebar


### Update an existing redesign widget ###
def update_widget(sub, widgetname, newcontent):
   debug_msg(widgetname)
   widget = get_widget_by_name(sub, widgetname)
   if widget:
      statustxt = newcontent
      styledata = None
      if isinstance(widget, praw.models.CommunityList):
         clist = []
         sublist = newcontent.split('\r\n')
         for subitem in sublist:
            subname = subitem.replace("*","").lstrip()
            subname = subname.replace("r/","")
            clist.append(subname)
         try:
            if not config['DEFAULT'].getboolean('DebugMode'):
               widget.mod.update(shortName=widgetname, data=clist,description=' ')
         except Exception as e:
            logmsg.critical("[ERROR] Updating widget %s - %s", widgetname, vars(e.response))
      else:
         if widgetname == "Server Status":
            if sub == 'ffxi' and 'xi' in sys.modules:
               statustxt = get_server_status_style(sub, newcontent, 'txt')
               styledata = get_server_status_style(sub, newcontent, 'style')
         try:
            if not config['DEFAULT'].getboolean('DebugMode'):
               if styledata:
                  widget.mod.update(shortName=widgetname, text=statustxt, styles=styledata)
               else:
                  widget.mod.update(shortName=widgetname, text=statustxt)
         except Exception as e:
            logmsg.critical("[ERROR] Updating widget %s - %s", widgetname, vars(e.response))


### Checks if sidebar attempted text is near limit, and modmails a warning if so. Returns False if near char limit ###
def check_sidebar_freespace(sub, text):
   char_ct = len(text)
   pct = round((char_ct/10000)*100.0)
   if pct > 95:
      bodystr = 'Sidebar update attempt near limit, '+str(pct)+'% full ('+str(char_ct)+' characters). Please remove some text in the sidebar ASAP or the automated sidebar will begin to fail. Lower this below 95% and this warning will cease.'
      debug_msg(bodystr)
      if datetime.now().hour == 22 and datetime.now().minute == 00:
         alert_mods(sub, 'Warning: sidebar is near/beyond character limit', bodystr)
      return False
   else:
      return True


### If you run a game subreddit, this can be used to return the server status if your have a module for it  ###
def handle_server_status(sub):
   if sub == 'ffxi' and 'xi' in sys.modules:
      return xi.get_xi_worldstatus()
   elif sub == 'ffxiv' and 'xiv' in sys.modules:
      return xiv.get_worldstatus()


### Similar to above, this can be used to return dynamic content if you have a module for it ###
def handle_latest_blogs(sub, which):
   if sub == 'ffxi' and 'xi' in sys.modules:
      return xi.get_playonline(which, int(config['DEFAULT']['ItemLimit']))
   elif sub == 'ffxiv' and 'xiv' in sys.modules:
      return xiv.obtain_lodestone(which)


### More dynamic content systems ###
def get_server_status_style(sub, status, which):
   if sub == 'ffxi' and 'xi' in sys.modules:
      if which == 'txt':
         return "**["+status+"](" + config['DEFAULT']['XiStatusUrl'] + ")**"
      elif which == 'style':
         if status == "Up":
            styledata = {'headerColor': '#014980', 'backgroundColor': '#c1ed92' }
         elif status == "Down":
            styledata = {'headerColor': '#014980', 'backgroundColor': '#f7c1c1' }
         else:
            styledata = {'headerColor': '#014980', 'backgroundColor': '#ffeb9b' }
         return styledata
