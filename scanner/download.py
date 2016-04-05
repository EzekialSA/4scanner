#!/usr/bin/env python3
import urllib
import argparse
import logging
import os
import sys
import re
import time
import http.client
import requests
import threading


def load(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def add_to_downloaded_log(img_filename, tmp_log):
    f = open(tmp_log, "a")
    f.write("{0}\n".format(img_filename))
    f.close()


def was_downloaded(img_filename, tmp_log):
    if os.path.isfile(tmp_log):
        f = open(tmp_log, "r")
        if img_filename in f.read():
            f.close()
            return True
        else:
            return False
    else:
        return False


def download_thread(thread, output_folder, folder, is_quiet):
    board = ''.join(thread).split('/')[3]

    tmp_log = ("/tmp/4scanner_tmp_{0}_{1}"
               .format(os.getpid(), threading.current_thread().name))

    directory = os.path.join(output_folder, 'downloads', board, folder + "/")
    if not os.path.exists(directory):
        os.makedirs(directory)

    while True:
        try:
            for link, img in re.findall('(\/\/i.4cdn.org/\w+\/(\d+\.(?:jpg|png|gif|webm)))', load(thread)):
                if not os.path.isfile("{0}/{1}".format(directory, img)):
                    if not is_quiet:
                        print(img)
                    if not was_downloaded(img, tmp_log):
                        urllib.request.urlretrieve('http:' + link, directory + img)
                        add_to_downloaded_log(img, tmp_log)
            if not is_quiet:
                print('.')
            time.sleep(20)
        except requests.exceptions.HTTPError as err:
            if not is_quiet:
                print('thread 404\'d')
            os.unlink(tmp_file)
            exit(0)
