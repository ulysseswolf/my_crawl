import os
import logging  
import logging.handlers  

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(CURRENT_PATH, os.pardir)
LOG_FILE = os.path.join(ROOT_PATH, 'a.log')
  
#handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 50*1024*1024, backupCount=1)  
handler = logging.handlers.RotatingFileHandler(LOG_FILE)
  
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s'  
formatter = logging.Formatter(fmt)  
handler.setFormatter(formatter)  
  
logger = logging.getLogger(LOG_FILE)  
logger.addHandler(handler)  
logger.setLevel(logging.DEBUG)  
  
#logger.info('info msg')  
#logger.debug('debug msg')
