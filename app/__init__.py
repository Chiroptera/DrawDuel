from flask import Flask
import logging

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                     LOGGING SETUP
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                     APP SETUP
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.logger.addHandler(ch)
app.logger.addHandler(fh)

from app import game