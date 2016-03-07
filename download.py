#!/usr/bin/python
import urllib2
import argparse
import logging
import os
import sys
import re
import time
import httplib


def load(url):
    return urllib2.urlopen(url).read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('thread', nargs=1, help='url of the thread')
    parser.add_argument('folder', nargs='?', help='change output folder')
    parser.add_argument("-q", "--quiet", action='store_true', help="quiet")
    args = parser.parse_args()

    if args.quiet:
        null = open(os.devnull, 'w')
        sys.stdout = null

    workpath = os.path.dirname(os.path.realpath(__file__))
    board = ''.join(args.thread).split('/')[3]

    if args.folder is not None:
        thread = ''.join(args.folder)
    else:
        thread = ''.join(args.thread).split('/')[5].split('#')[0]

    directory = os.path.join(workpath, 'downloads', board, thread)
    if not os.path.exists(directory):
        os.makedirs(directory)

    os.chdir(directory)

    while len(args.thread):
        for t in args.thread:
            try:
                for link, img in re.findall('(\/\/i.4cdn.org/\w+\/(\d+\.(?:jpg|png|gif|webm)))', load(t)):
                    if not os.path.exists(img):
                        print(img)
                        data = load('https:' + link)
                        with open(img, 'w') as f:
                            f.write(data)
            except urllib2.HTTPError, err:
                print('%s 404\'d')
                args.thread.remove(t)
                continue
            except (urllib2.URLError, httplib.BadStatusLine, httplib.IncompleteRead):
                print('something went wrong')
        print('.')
        time.sleep(20)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
