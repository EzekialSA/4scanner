#!/usr/bin/env python3

import json
import logging
import os
from scanner import thread_scanner, dupecheck, imageboard_info, downloader

print("Testing scanner.py")

t_scanner = thread_scanner.thread_scanner("test/test_config.json", "/tmp/", 200, 1, logging.getLogger())
print("--------------------------------------------------------")
print("Testing: t_scanner.get_catalog_json                    -")
print("--------------------------------------------------------")
catalog_json = t_scanner.get_catalog_json("a", "4chan")
print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("Testing: t_scanner.scan_thread                         -")
print("--------------------------------------------------------")

list_of_threads = t_scanner.scan_thread("anime", catalog_json)
for i in list_of_threads:
     print(i)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("!!! t_scanner.download_thread not tested yet !!!       -")
print("--------------------------------------------------------")

print("--------------------------------------------------------")
print("Testing: t_scanner.dir_size_mb                         -")
print("--------------------------------------------------------")

#Creating a 15mb file in a subfolder of a folder
os.system("mkdir folder_size_test")
os.system("mkdir folder_size_test/subfolder")
os.system("dd if=/dev/zero of=folder_size_test/subfolder/15mbfile bs=15000000 count=1")

# Getting folder size
size = t_scanner.dir_size_mb("folder_size_test")
if int(size) != 15:
    print(size)
    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("!!! scanner.check_quota not tested yet !!!             -")
print("--------------------------------------------------------")

print("--------------------------------------------------------")
print("Testing:                                               -")
print("scanner.get_check_duplicate                            -")
print("scanner.get_condition                                  -")
print("scanner.get_imageboard                                 -")
print("scanner.get_keyword                                    -")
print("--------------------------------------------------------")

json_file = json.load(open("test/test_config.json"))

# Get a list of every search entry in the json file
search_list = []
for search in json_file["searches"]:
    search_list.append(search)

# Test on the first search with all optionals parameters
duplicate1  = t_scanner.get_check_duplicate(search_list[0])
condition1  = t_scanner.get_condition(search_list[0])
imageboard1 = t_scanner.get_imageboard(search_list[0])
keyword1    = t_scanner.get_keyword(search_list[0])

if not duplicate1:
    print("duplicate1 should be True but is False")
    exit(1)

if condition1["filename"] != ['IMG_']:
    print("filename error in condition1")
    exit(1)

if condition1["width"] != '>100':
    print("width error in condition1")
    exit(1)

if condition1["height"] != '>200':
    print("height error in condition1")
    exit(1)

if condition1["ext"] != ['.jpg', '.png']:
    print("ext error in condition1")
    exit(1)

if imageboard1 != '4chan':
    print("imageboard1 should be 4chan")
    exit(1)

if keyword1 != ['keyword1', 'keyword2', 'keyword3']:
    print("keyword1 should be equal to ['keyword1', 'keyword2', 'keyword3']")
    exit(1)

duplicate2  = t_scanner.get_check_duplicate(search_list[1])
condition2  = t_scanner.get_condition(search_list[1])
imageboard2 = t_scanner.get_imageboard(search_list[1])
keyword2    = t_scanner.get_keyword(search_list[1])

if not duplicate2:
    print("duplicate2 should be True but is False")
    exit(1)

if condition2["filename"]:
    print("filename should be false")
    exit(1)

if condition2["width"]:
    print("width should be false")
    exit(1)

if condition2["height"]:
    print("height should be false")
    exit(1)

if condition2["ext"]:
    print("ext should be false")
    exit(1)

if imageboard2 != '4chan':
    print("imageboard2 should be 4chan")
    exit(1)

if keyword2 != ['keyword']:
    print("keyword2 should be equal to ['keyword']")
    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("!!! scanner.scan not tested yet !!!                    -")
print("--------------------------------------------------------")

print('\x1b[6;30;42m' + 'All test OK for scanner.py' + '\x1b[0m')

print("Testing dupecheck.py")

print("--------------------------------------------------------")
print("Testing: dupecheck.hash_image                          -")
print("--------------------------------------------------------")

hash = dupecheck.hash_image("test/test_img.png")
if hash != "b3ce9cb3aefc5e240b4295b406ce8b9a":
    print("hash should be b3ce9cb3aefc5e240b4295b406ce8b9a")
    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("!!! dupecheck.add_to_db not tested yet !!!             -")
print("--------------------------------------------------------")

print("--------------------------------------------------------")
print("!!! dupecheck.is_duplicate not tested yet !!!          -")
print("--------------------------------------------------------")

print('\x1b[6;30;42m' + 'All test OK for dupecheck.py' + '\x1b[0m')

print("Testing imageboard_info.py")

print("--------------------------------------------------------")
print("Testing: imageboard_info.get_imageboard_info           -")
print("--------------------------------------------------------")

info_4chan = imageboard_info.imageboard_info("4chan")
if info_4chan.base_url != "http://a.4cdn.org/":
    print("chan_base_url wrong for 4chan")
    exit(1)

if info_4chan.thread_subfolder != "/thread/":
    print("chan_thread_subfolder wrong for 4chan")
    exit(1)

if info_4chan.image_subfolder != "/":
    print("chan_image_subfolder wrong for 4chan")
    exit(1)

if info_4chan.image_base_url != "http://i.4cdn.org/":
    print("chan_image_base_url wrong for 4chan")
    exit(1)

info_lainchan = imageboard_info.imageboard_info("lainchan")
if info_lainchan.base_url != "https://lainchan.org/":
    print("chan_base_url wrong for lainchan")
    exit(1)

if info_lainchan.thread_subfolder != "/res/":
    print("chan_thread_subfolder wrong for lainchan")
    exit(1)

if info_lainchan.image_subfolder != "/src/":
    print("chan_image_subfolder wrong for lainchan")
    exit(1)

if info_lainchan.image_base_url != "https://lainchan.org/":
    print("chan_image_base_url wrong for lainchan")
    exit(1)


info_uboachan = imageboard_info.imageboard_info("uboachan")
if info_uboachan.base_url != "https://uboachan.net/":
    print("chan_base_url wrong for uboachan")
    exit(1)

if info_uboachan.thread_subfolder != "/res/":
    print("chan_thread_subfolder wrong for uboachan")
    exit(1)

if info_uboachan.image_subfolder != "/src/":
    print("chan_image_subfolder wrong for uboachan")
    exit(1)

if info_uboachan.image_base_url != "https://uboachan.net/":
    print("chan_image_base_url wrong for uboachan")
    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print('\x1b[6;30;42m' + 'All test OK for imageboard_info.py' + '\x1b[0m')

print("Testing download.py")

# Creating download object
condition = {"ext": False, "filename": False, "width": False, "height": False, }
download = downloader.downloader(list_of_threads[0], 'a',"4chan", ".", "testci", True, condition, True, ["travistag1", "ci:travistag2"], logging.getLogger())

print("--------------------------------------------------------")
print("!!! download.load not tested yet !!!                   -")
print("--------------------------------------------------------")

print("--------------------------------------------------------")
print("Testing: download.create_dir                           -")
print("--------------------------------------------------------")

# Creating directory
download.create_dir("test_create_dir")
if not os.path.exists("test_create_dir"):
    print("'test_create_dir' was not created")
    exit(1)

# Testing again because the function should not crash if folder already exist
download.create_dir("test_create_dir")

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("Testing: download.add_to_downloaded_log                -")
print("Testing: download.was_downloaded                       -")
print("--------------------------------------------------------")

os.system("echo "" > test_download_log.txt")
download.add_to_downloaded_log("my_filename")
if 'my_filename' not in open(download.downloaded_log).read():
    print("'my_filename' is not in {0}".format(download.downloaded_log))
    exit(1)

downloaded = download.was_downloaded("my_filename")
if not downloaded:
    print("'returned' should be True")
    exit(1)

downloaded = download.was_downloaded("other_filename")
if downloaded:
    print("'returned' should be False")
    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("Testing: download.extension_condition                  -")
print("--------------------------------------------------------")

if not download.extension_condition([".jpg"], ".jpg"):
    print("same extension should return True")
    exit(1)

if download.extension_condition([".jpg"], ".png"):
    print("different extension should return False")
    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("Testing: download.filename_condition                   -")
print("--------------------------------------------------------")

if not download.filename_condition(["IMG_"], "IMG_2345.jpg"):
    print("IMG_ is in IMG_2345, should return True")
    exit(1)

if download.filename_condition(["PIC"], "IMG_2345.jpg"):
    print("PIC is not in IMG_2345, should return False")
    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("Testing: download.width_condition                      -")
print("--------------------------------------------------------")

if not download.width_condition("=100", 100):
    print("100 is equal to 100, should be True")
    exit(1)

if download.width_condition("=100", 101):
    print("100 is not equal to 101, should be False")
    exit(1)

if not download.width_condition(">100", 101):
    print("101 is greater than 100, should be True")
    exit(1)

if download.width_condition(">100", 99):
    print("99 is not greater than 100, should be False")
    exit(1)

if not download.width_condition("<100", 99):
    print("99 is lower than 100, should be True")
    exit(1)

if download.width_condition("<100", 101):
    print("101 is not lower than 100, should be False")
    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')


print("--------------------------------------------------------")
print("Testing: download.all_condition_check                  -")
print("--------------------------------------------------------")

all_true = [True, True, True, True]
one_false = [True, False, True, True]
all_false = [False, False, False, False]

if not download.all_condition_check(all_true):
    print("all conditions are True, should return True")
    exit(1)

if download.all_condition_check(one_false):
    print("one condition is False, should return False")
    exit(1)

if download.all_condition_check(all_false):
    print("all conditions are False, should return False")
    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("!!! download.meet_dl_condition not tested yet !!!      -")
print("--------------------------------------------------------")

print("--------------------------------------------------------")
print("!!! download.remove_if_duplicate not tested yet !!!    -")
print("--------------------------------------------------------")

print("--------------------------------------------------------")
print("!!! download.download_image not tested yet !!!         -")
print("--------------------------------------------------------")

#img_url= "https://github.com/Lacsap-/4scanner/raw/master/logo/"
#post_dic = {'tim': '4scanner128', 'ext': '.png'}

#file_path = download.download_image(img_url, post_dic, ".")
#if not os.path.isfile(file_path):
#    print("4scanner128.png should have been downloaded.")
#    exit(1)

print('\x1b[6;30;42m' + 'OK' + '\x1b[0m')

print("--------------------------------------------------------")
print("!!! download.download_thread not tested yet !!!        -")
print("--------------------------------------------------------")

print('\x1b[6;30;42m' + 'All test OK for download.py' + '\x1b[0m')
print('\x1b[6;30;42m' + 'SUCCESS' + '\x1b[0m')
