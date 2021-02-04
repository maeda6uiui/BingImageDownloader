# Bing Image Downloader

Download images in bulk from Bing image search

## Usage

Clone this repository

```shell
git clone https://github.com/maeda6uiui/BingImageDownloader
cd BingImageDownloader
```

Create a text file enumerating your keywords and save it as *keywords.txt*

```
Bee-eater
The Shepherd's Crown
Sharad Purnima
Commondale
Polkovnik
Crunchyroll Anime Awards
Fukuzawa Yukichi
```

Run

```shell
python3 run.py
```

Images are downloaded and then archived under the *Archive* directory. Each subdirectory is named according to the MD5 hash value of the keyword and *info.txt* contains the original keyword.

## Options

| Option                     | Description                                                  | Default value  |
| -------------------------- | ------------------------------------------------------------ | -------------- |
| --keywords_filepath        | Filepath of the keyword list                                 | ./keywords.txt |
| --limit                    | Max number of images to download                             | 200            |
| --disable_safe_search      | Disable safe search                                          |                |
| --timeout                  | Timeout                                                      | 60             |
| --filters                  | Filters                                                      |                |
| --save_root_dir            | Root directory to save downloaded images. This directory will be removed after being archived. | ./Image        |
| --workers_log_dir          | Directory to create log files of workers                     | ./WorkersLog   |
| --archive_save_dir         | Directory to save archive files                              | ./Archive      |
| --overwrite                | Overwrite existing directories                               |                |
| --archive_format           | Format of archive files. *zip*, *tar*, *gztar*, *bztar*, and *xztar* are supported. | gztar          |
| --num_keywords_per_archive | Number of keywords per archive                               | 100            |
| --progress_log_filepath    | Filepath of the log file to record progress                  | ./progress.txt |
| --index_lower_bound        | Start index of keywords. Keywords between [index_lower_bound, index_upper_bound) are used by this downloader. | 0              |
| --index_upper_bound        | End index of keywords. Keywords between [index_lower_bound, index_upper_bound) are used by this downloader. When a negative value is set to this option, the upper bound of the index is the total number of keywords. | -1             |
| --num_downloader_processes | Number of downloader processes (*run.py* only)               | 5              |
| --num_formatter_processes  | Number of formatter processes                                | 5              |
| --feeder_threads           | Number of feeder threads (*run_icrawler.py* only)            | 4              |
| --parser_threads           | Number of parser threads (*run_icrawler.py* only)            | 4              |
| --downloader_threads       | Number of downloader threads (*run_icrawler.py* only)        | 8              |
| --image_width              | Width of images                                              | 256            |
| --image_height             | Height of images                                             | 256            |
| --no_format_images         | Images are not formatted if set                              |                |
| --no_archive_images        | Images are not archived if set                               |                |

## Comments

Large part of [downloader.py](./downloader.py) is derived from [gurugaurav/bing_image_downloader](https://github.com/gurugaurav/bing_image_downloader). Please check out [the license for the original project](https://github.com/gurugaurav/bing_image_downloader/blob/master/LICENSE).

The specs of search engines are subject to change, and this project may not work after such change.

