import logging
import time
from logging.handlers import TimedRotatingFileHandler


def initialize(subname):
   path = f'logs/{subname}_synccompanion.log'
   logmsg = logging.getLogger("Rotating_Log")
   fmt = u'%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s'
   logmsg.setLevel(logging.INFO)
   handler = TimedRotatingFileHandler(path, when="d", interval=1, backupCount=14)
   handler.setFormatter(logging.Formatter(fmt))
   logmsg.addHandler(handler)
