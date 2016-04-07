#!/usr/bin/env python3


import time
import json
import os
import re
from scanner import download
import subprocess
import urllib.request
import threading


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


def download_thread(id, board, folder, output):
    url = "http://boards.4chan.org/{0}/thread/{1}".format(board, id)
    t = threading.Thread(target=download.download_thread, args=(str(url),
                                                                output,
                                                                folder,
                                                                True))
    t.daemon = True
    t.start()


def add_to_downloaded(id, log_file, output):
    download_log = open("{0}/{1}".format(output, log_file), "a")
    download_log.write("{0}\n".format(id))


def scan(keywords_file, output, log_file):
    while True:
        curr_time = time.strftime('%d/%b/%Y-%H:%M')
        print("{0} Searching threads...".format(curr_time))

        dl_log = open("{0}/{1}".format(output, log_file), "a")
        dl_log.write(time.strftime('Execution date {0}\n'.format(curr_time)))
        dl_log.close()

        json_file = json.load(open(keywords_file))

        for search in json_file["searches"]:

            folder_name = search["folder_name"]
            board = search["board"]
            keywords = search["keywords"]
            try:
                catalog_json = get_catalog_json(board)

                for keyword in keywords:
                    threads_id = scan_thread(keyword, catalog_json)

                    dl_log = open("{0}/{1}".format(output, log_file)).read()
                    for thread_id in list(set(threads_id)):
                        if str(thread_id) not in dl_log:
                            download_thread(thread_id, board, folder_name,
                                            output)
                            add_to_downloaded(thread_id, log_file, output)
            except requests.exceptions.HTTPError as err:
                print("Error while opening {0} catalog page. "
                      "Retrying during next scan.")
                pass

        active_downloads = threading.active_count()-1
        print("{0} Threads download are active!".format(active_downloads))
        print("Searching again in 10 minutes!")
        time.sleep(600)
