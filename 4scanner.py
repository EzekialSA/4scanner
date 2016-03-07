#!/usr/bin/env python3

import argparse
import time
import json
import os
import subprocess
import urllib.request


# Arguments parsing and validation
parser = argparse.ArgumentParser()
parser.add_argument("keywords_file",
                    help="file with the keywords to search for")
args = parser.parse_args()

# Checking keywords file
if not os.path.isfile(args.keywords_file):
        print("Keywords file does not exist...")
        exit(1)


def get_catalog_json(board):
    catalog = urllib.request.urlopen(
              "http://a.4cdn.org/{0}/catalog.json".format(board))
    return json.loads(catalog.read().decode("utf8"))


def scan_thread(keyword, catalog_json):
    # Check each thread, threads who contains the keyword are returned
    matched_threads = []
    for i in range(len(catalog_json)):
        for thread in catalog_json[i]["threads"]:
            if 'com' in thread:
                if keyword.lower() in str(thread["com"]).lower():
                    matched_threads.insert(0, thread["no"])

    return matched_threads


def download_thread(id, board, folder):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    command = "{0}/download.py -q "\
              "http://boards.4chan.org/{1}/thread/{2} {3} &"\
              .format(script_dir,
                      board,
                      id,
                      folder)
    os.system(command)


def add_to_downloaded(id):
    download_log = open("downloaded.txt", "a")
    download_log.write("{0}\n".format(id))


def main():
    current_time = time.strftime('%d, %b %Y')
    print("{0} Searching threads...".format(current_time))

    dl_log = open("downloaded.txt", "a")
    dl_log.write(time.strftime('Execution date %d, %b %Y\n'))
    dl_log.close()

    json_file = json.load(open(args.keywords_file))

    for search in json_file["searches"]:

        folder_name = search["folder_name"]
        board = search["board"]
        keywords = search["keywords"]

        catalog_json = get_catalog_json(board)

        for keyword in keywords:
            threads_id = scan_thread(keyword, catalog_json)

            dl_log = open('downloaded.txt').read()
            for thread_id in list(set(threads_id)):
                if str(thread_id) not in dl_log:
                    download_thread(thread_id, board, folder_name)
                    add_to_downloaded(thread_id)

                    # waiting because starting downloads too fast sometime
                    # crashes download.py
                    time.sleep(5)

    print("Thread search completed, you can see running downloads with:")
    print("ps aux | grep download.py\nSearching again in 10 minutes!")
    time.sleep(600)

if __name__ == '__main__':
    try:
        while True:
            main()
    except KeyboardInterrupt:
        pass
