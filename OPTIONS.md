# Search options

## keywords (required)

the keywords that 4scanner will look for when searching the threads. When a keyword is found in the first post of a thread, it will be downloaded.

Examples:
- `"keywords": "cat" `
- `"keywords": ["cat", "caturday", "dog"] `

## board (required)

The board where 4scanner will search for threads to download.

Example:
- `"board": "v"`

## folder_name (required)

The name of the folder where the picture will be downloaded.

Example:
- `"folder_name": "cat_pictures" `


## imageboard (optional)

Specify the imageboard to search.
- Default: 4chan

Example:
- `"imageboard": "4chan" `


## filename (optional)

Download only images containing the the string specified. You can specify more than one filename.

Example:

- `"filename": "my_filename" `
- `"filename": ["filename_1", "filename_2"] `

## extension (optional)

Download only images with one (or more) extension.

Example:

- `"extension": ".png" `
- `"extension": [".jpg", ".png"] `

## width (optional)

specify minimum, maximum or exact width of the images to download, in pixel.

Format is `>`, `<` or `=` followed by the number.

Example:

- `"width": "<600" `
- `"width": ">1024" `
- `"width": "=1920" `


## height (optional)

Specify minimum, maximum or exact height of the images to download, in pixel.

Format is `>`, `<` or `=` followed by the number of pixel.

Example:

- `"height": "<600" `
- `"height": ">1024" `
- `"height": "=1080" `

## check_duplicate (optional)

Can be true or false. If true, 4scanner will check if the picture already exist in the download directory and won't download it. If false no attempt will be made to not download duplicate pictures.

Default: true

Example:
- `"check_duplicate": true `
- `"check_duplicate": false `
