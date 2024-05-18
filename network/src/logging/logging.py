import os
import yaml
import logging

logger = logging.getLogger("BioNet")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
         "%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s"
         )

# console handler
ch = logging.StreamHandler()
ch.setLevel(logging.WARN) # ERROR
ch.setFormatter(formatter)
logger.addHandler(ch)

# file handler
file_name = os.path.join('src', 'last_experiment.log')
try:
    os.mknod(file_name)
    print("Empty last_experiment.log created!")
except:
    os.remove(file_name)
    print("last_experiment.log removed!")
fh = logging.FileHandler(file_name)
fh.setLevel(logging.DEBUG) # DEBUG
fh.setFormatter(formatter)
logger.addHandler(fh)
