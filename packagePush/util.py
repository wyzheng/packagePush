#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import os
import struct

import requests
import json
import time
import logging
logging.basicConfig(level=logging.INFO,
                    filename='error.log',
                    filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )

class MMToolsError(RuntimeError):
    pass


def mmtools_post(url, data=None, retry_count=3, **kwargs):
    print(data)
    frames = inspect.stack()
    call = ""
    if len(frames) > 2:
        current_filename = frames[0][1]
        for frame in frames[1:]:
            if frame[1] != current_filename and os.path.basename(frame[1]) != "monitor.py" and "mmtoolscli" not in \
                    frame[1]:
                call = "called by %s in line %d, " % (frame[3], frame[2])
                break

    logging.debug("%s%s", call, data[:1024])
    res = None
    for i in range(retry_count):
        # logger.info("try %d, max try %d", i, retry_count)
        try:
            res = requests.post(url, data=data, **kwargs)
        except requests.exceptions.Timeout:
            logging.exception("requests timeout")
            continue
        logging.info("status:%s, res:%s", res.status_code, res.text[:1024])
        if res.status_code == requests.codes.ok:
            json_res = res.json()
            if json_res['rtn'] != 0:
                raise MMToolsError(res.text)
            return res
        else:
            logging.error("server error")
        time.sleep((i + 1) * 2)
    if res:
        res.raise_for_status()


def mmtools_get(url, params=None, retry_count=3, **kwargs):
    logging.debug(url)
    res = None
    for i in range(retry_count):
        logging.info("try %d, max try %d", i, retry_count)
        try:
            res = requests.get(url, params=params, **kwargs)
        except requests.exceptions.Timeout:
            logging.exception("requests timeout")
            continue
        logging.info(res.status_code)
        if res.status_code == requests.codes.ok:
            return res
        else:
            logging.error("server error")
            time.sleep((i + 1) * 2)
    if res:
        res.raise_for_status()


def MMGBK2UTF8(content):
    if isinstance(content, str):
        return content.encode("utf-8")

    try:
        content = content.decode('utf-8').encode('utf-8')
    except:
        content = content.decode('gbk', "ignore").encode('utf-8')
    return content


def file_2_int_buffer(path):
    int_buffer = []
    with open(path, 'rb') as f:
        while True:
            byte_s = f.read(1)
            if not byte_s:
                break
            int_buffer.append(struct.unpack('B', byte_s)[0])
    return int_buffer


def is_test_uin(uin):
    return str(uin).startswith("319")
