import logging
import threading
import time
import traceback
from time import sleep

import requests

data = {'user': 'kf001@xykd'}
logger = logging.getLogger("traceback_test")
logger.setLevel(logging.DEBUG)


def send(x, y):
    global ind, succ, error
    try:
        start = int(time.time())
        res = requests.put('http://192.168.66.111:11005/fs/api/init',
                           data=data)
        end = int(time.time())
        diff = end - start
        print('Thread {0} - {1} times:{2}, {3}  {4}'.format(
            x, y, start, end, diff))
        succ += 1
    except Exception:
        logger.error(traceback.format_exc(limit=None))
        error += 1
    finally:
        ind += 1


def send_threading(x):
    for y in range(y_len):
        threading.Thread(target=send, args=(x, y)).start()


x_len = 10
y_len = 100
ind = 0
succ = 0
error = 0
if __name__ == '__main__':
    for x in range(x_len):
        threading.Thread(target=send_threading, args=(x, )).start()
    while ind < x_len * y_len:
        sleep(1)

    print('Thread is End')
    print('Succ:{0}'.format(succ))
    print('Error:{0}'.format(error))

    # start = time.time()
    # data = {'user': 'kf001@xykd'}
    # req_list = [
    #     grequests.put('http://117.158.194.72:11011/fs/api/init', data=data)
    #     for i in range(1000)
    # ]
    # res_list = grequests.map(req_list)
    # print(time.time() - start)
    # print(res_list)
