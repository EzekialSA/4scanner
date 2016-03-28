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


def load(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def download_thread(thread, output_folder, folder, is_quiet):
    board = ''.join(thread).split('/')[3]

    directory = os.path.join(output_folder, 'downloads', board, folder + "/")
    if not os.path.exists(directory):
        os.makedirs(directory)

    while True:
        try:
            for link, img in re.findall('(\/\/i.4cdn.org/\w+\/(\d+\.(?:jpg|png|gif|webm)))', load(thread)):
                if not os.path.isfile("{0}/{1}".format(directory, img)):
                    if not is_quiet:
                        print(img)
                    urllib.request.urlretrieve('http:' + link, directory + img)
            if not is_quiet:
                print('.')
            time.sleep(20)
        except requests.exceptions.HTTPError as err:
            if not is_quiet:
                print('thread 404\'d')
            exit(0)
