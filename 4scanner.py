#!/usr/bin/env python3

import argparse
import download
import time
import json
import os
import re
import subprocess
import urllib.request
import download
import threading


# Arguments parsing and validation
parser = argparse.ArgumentParser()
parser.add_argument("keywords_file",
                    help="file with the keywords to search for")
args = parser.parse_args()

# Checking keywords file
if not os.path.isfile(args.keywords_file):
        print("Keywords file does not exist...")
        exit(1)

workpath = os.path.dirname(os.path.realpath(__file__))


def get_catalog_json(board):
    catalog = urllib.request.urlopen(
              "http://a.4cdn.org/{0}/catalog.json".format(board))
    return json.loads(catalog.read().decode("utf8"))


def scan_thread(keyword, catalog_json):
    # Check each thread, threads who contains the keyword are returned
    matched_threads = []
    for i in range(len(catalog_json)):
        for thread in catalog_json[i]["threads"]:
            regex = r'\b{0}\b'.format(keyword)
            # Search thread title
            if 'sub' in thread:
                if re.search(regex, str(thread["sub"]), re.IGNORECASE):
                    matched_threads.append(thread["no"])

            # Search OPs post body
            if 'com' in thread:
                if re.search(regex, str(thread["com"]), re.IGNORECASE):
                    matched_threads.append(thread["no"])

    return matched_threads


def download_thread(id, board, folder):
    url = "http://boards.4chan.org/{0}/thread/{1}".format(board, id)
    t = threading.Thread(target=download.download_thread, args=(str(url),
                                                                folder,
                                                                True))
    t.daemon = True
    t.start()


def add_to_downloaded(id):
    download_log = open("{0}/downloaded.txt".format(workpath), "a")
    download_log.write("{0}\n".format(id))


def main():
    current_time = time.strftime('%d/%b/%Y-%H:%M')
    print("{0} Searching threads...".format(current_time))

    dl_log = open("{0}/downloaded.txt".format(workpath), "a")
    dl_log.write(time.strftime('Execution date {0}\n'.format(current_time)))
    dl_log.close()

    json_file = json.load(open(args.keywords_file))

    for search in json_file["searches"]:

        folder_name = search["folder_name"]
        board = search["board"]
        keywords = search["keywords"]

        catalog_json = get_catalog_json(board)

        for keyword in keywords:
            threads_id = scan_thread(keyword, catalog_json)

            dl_log = open("{0}/downloaded.txt".format(workpath)).read()
            for thread_id in list(set(threads_id)):
                if str(thread_id) not in dl_log:
                    download_thread(thread_id, board, folder_name)
                    add_to_downloaded(thread_id)

                    # waiting because starting downloads too fast sometime
                    # crashes download.py
                    time.sleep(5)
    active_downloads = threading.active_count()-1
    print("{0} Threads download are active!".format(active_downloads))
    print("Searching again in 10 minutes!")
    time.sleep(600)

if __name__ == '__main__':
    try:
        while True:
            main()
    except KeyboardInterrupt:
        pass
