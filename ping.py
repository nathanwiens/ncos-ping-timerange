"""
This application will ping an address and log the results
"""

import cs
import sys
from time import sleep
from datetime import datetime, time, timezone, timedelta
import logging
import logging.handlers

"""SET THE IP ADDRESSES OR HOSTNAMES TO PING"""
hosts = ['208.67.220.220', '208.67.222.222', '8.8.8.8']

handlers = [logging.StreamHandler()]

if sys.platform == 'linux2':
    # on router also use the syslog
    handlers.append(logging.handlers.SysLogHandler(address='/dev/log'))

logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(name)s: %(message)s',
        datefmt='%b %d %H:%M:%S',
        handlers=handlers)

log = logging.getLogger('ping-sdk')

cstore = cs.CSClient()


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now(timezone(timedelta(hours=-6))).time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

'''
CHANGE TIME RANGE HERE. ADD/REMOVE "or" STATEMENTS FOR MULTIPLE RANGES
'''
while 1:
    if is_time_between(time(10, 30), time(12, 00)) or is_time_between(time(13, 30), time(15, 00)):
        for host in hosts:
            cstore.put('control/ping/start/host', host)
            cstore.put('control/ping/start/size', 64)
            result = {}
            try_count = 0

            sleep(5)
            while try_count < 5:
                result = cstore.get('control/ping')
                if result.get('data') and result.get('data').get('status') in ["error", "done"]:
                    break
                sleep(3)
                try_count += 1

            error_str = ""
            if try_count == 5 or not result.get('data') or result.get('data').get('status') != "done":
                error_str = "An error occurred"

            resultstring = result['data']['result'].splitlines()
            if error_str == "":
                for line in resultstring:
                    if "icmp_seq" in line:
                        line = line.split("(")[1]
                        line = line.replace(")", "")
                        log.info(line)
            else:
                log.info(error_str)
            sleep(5)
    else:
        """
        log.info("Time range not met, skipping ping test: {}".format(datetime.now(timezone(timedelta(hours=-6))).time()))
        """
    sleep(900)
