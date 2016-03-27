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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('thread', help='url of the thread')
    parser.add_argument('folder', nargs='?',
                        help='Change the folder name where images are downloaded')
    parser.add_argument("-q", "--quiet", action='store_true', help="quiet")
    parser.add_argument("-o", "--output", help="Specify output folder")
    args = parser.parse_args()

    print(args.thread)

    quiet = False
    if args.quiet:
        quiet = True

    if args.folder is not None:
        folder = ''.join(args.folder)
    else:
        folder = ''.join(args.thread).split('/')[5].split('#')[0]

    if args.output is not None:
        output = args.output
        if not os.path.exists(output):
            print("{0} Does not exist.".format(output))
            exit(1)
    else:
        output = os.path.dirname(os.path.realpath(__file__))

    download_thread(args.thread, output, folder, quiet)


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

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
