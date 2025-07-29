import logging
import os
import sys
#import psutil NÕUAB gcc kompileerimist lähtesüsteemi

def reconf_logging(solution_name, level=logging.DEBUG):
    """
    Once you can redefine logging globally -- before first use!
    Let's add timestamp in begginning (if no time is displayed by default (you cannot tell the bees))
    And let's print out everything, incl debug-level
    FIXME: make these adaptions controlled by some env.var (not by Conf class, which may itself already use logging)
    
    https://docs.python.org/3/library/logging.html#logrecord-attributes
    %(message)s
    %(asctime)s
    %(lineno)d
    %(module)s
    %(name)s
    %(levelname)s
    """
    frm = "%(asctime)s:%(levelname)8s:%(lineno)5d:%(module)-15s:%(name)-6s:%(message)s"
    
    if '%(module)' not in frm:
        frm = ' %(module)-12s:' + frm
    if '%(lineno)' not in frm:
        frm = '%(lineno)4d:' + frm
    if '%(asctime)' not in frm:
        frm = '%(asctime)s:' + frm
    logging.basicConfig(format=frm, level=level, force=True)

def get_custom_logger(solution_name):
    reconf_logging(solution_name, logging.INFO)
    return logging.getLogger(solution_name)

### PURE FUNCTIONS ###
    
def halt(code: int, message: str):
    """
    Shortcut (for serious error situations) for logging message and do quick exit 
    Be aware: for Airflow any return code (incl 0) means that task is failed (dont use halt on normal flow!)
    For other running systems (bash script etc) You can control flow using exit code (regular end is code 0 automatically)
    Exit code must by between 0 and 255. Any other cases we will map to 255 
    """
    code = code if code >= 0 and code <= 255 else 255
    logging.error(f"{code} {message}")
    sys.exit(code)


# def mem_free_now() -> float: 
#     """
#     Returns free memory in megabytes as float
#     """
#     return psutil.virtual_memory().available / (1024 * 1024)

