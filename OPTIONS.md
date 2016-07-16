# Search options

## keywords (required)

the keywords that 4scanner will look for when searching the threads. When a keyword is found in the first post of a thread, it will be downloaded.

Example:<br/>
``` "keywords": "cat" ```
or<br/>
``` "keywords": ["cat", "caturday", "dog"] ```

## board (required)

The board where 4scanner will search for threads to download.

Example:<br/>
```"board": "v"```

## folder_name (required)

The name of the folder where the picture will be downloaded.

Example:<br/>
``` "folder_name": "cat_pictures" ```


## imageboard (optional)

Specify the imageboard to search.
- Default: 4chan

Example:<br/>
``` "imageboard":"4chan" ```


## filename (optional)

Download only images containing the the string specified. You can specify more than one filename.

Example:

``` "filename": "my_filename" ```
or<br/>
``` "filename": ["filename_1", "filename_2"] ```

## extension (optional)

Download only images with one (or more) extension.

Example:

``` "extension": ".png" ```
or<br/>
``` "extension": [".jpg", ".png"] ```

## width (optional)

specify minimum, maximum or exact width of the images to download, in pixel.

Format is ```>```, ```<``` or ```=``` followed by the number.

Example:

``` "width":"=1920" ```
or<br/>
``` "width":">1024" ```
or<br/>
``` "width":"<600" ```

## height (optional)

Specify minimum, maximum or exact height of the images to download, in pixel.

Format is ```>```, ```<``` or ```=``` followed by the number of pixel.

Example:

``` "height":"=1080" ```
or<br/>
``` "height":">1024" ```
or<br/>
``` "height":"<600" ```

## check_duplicate (optional)

Can be true or false. If true, 4scanner will check if the picture already exist in the download directory and won't download it. If false no attempt will be made to not download duplicate pictures.

Default: true

Example:<br/>
``` "check_duplicate": true ```
or <br/>
``` "check_duplicate": false ```
