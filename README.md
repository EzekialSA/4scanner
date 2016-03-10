# 4scanner

4scanner search 4chan's thread for matching keywords then download all images
to disk

## Requirements
- requests

To install all requirements: ``` pip install -r requirement.txt ```

## How to

the first things you need to do is create a simple json file with the output
folder you want, the board(s) you want to search and the keywords.
(set the json file section for more details)

After your json file is done you can start 4scanner with:

``` 4scanner.py file.json ```

it will search all threads for the keywords defined in your json file and
download all images/webms from threads where a keyword is found.

## Creating your JSON file

Creating the JSON file is easy, you can use the example.json file as a base.

Your "Searches" are what 4scanner use to know which board check for what keywords and where to download the images, you can have as many "Searches" as you want.

Here is an example of what the JSON file should look like:
```
{"searches":[
    {
      "folder_name":"YOUR_FOLDER_NAME",
      "board": "BOARD_LETTER",
      "keywords": ["KEYWORD1", "KEYWORD2"]
    },

    {
      "folder_name":"vidya",
      "board": "v",
      "keywords": ["tf2", "splatoon", "world of tank"]
    }
]}
```

## Notes

- /f/ - Flash is not supported (yet?)
- the keywords search is case insentitive

## download.py

download.py is the script used to download the threads found with the keywords.
You can use this this script alone to download a single thread by doing:

``` download.py http://boards.4chan.org/b/thread/373687492 ```

It will download all images until the thread die.

## Tips

Since 4chan is a cesspool of repost, you will probably download duplicates pictures
very fast. To prevent this you can download fdupes and run it as a cron job to remove duplicates like so:

```fdupes -rdN downloads/```
