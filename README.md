# Bing Image Downloader

Download images in bulk from Bing image search

This project is intended to be run on Google Colaboratory.
See the [Colab Notebook](./BingImageDownloaderSample.ipynb) to learn about basic usage.

## Usage

Clone this repository

```shell
git clone https://github.com/maeda6uiui/BingImageDownloader
cd BingImageDownloader
```

Install **icrawler**

```
pip install icrawler
```

Create a text file enumerating your keywords and save it as *keywords.txt*

```
Bee-eater
Sharad Purnima
Commondale
Polkovnik
Crunchyroll Anime Awards
```

Run

```shell
python3 run.py
```

Images are downloaded and then archived under the *Archive* directory. Each subdirectory is named according to the MD5 hash value of the keyword and *info.txt* contains the original keyword.

## Requirements

- Python 3.5, 3.6, 3.7
- **icrawler** library

Tested with Python 3.6

## Options

| Option                     | Description                                                  | Default value  |
| -------------------------- | ------------------------------------------------------------ | -------------- |
| --keywords_filepath        | Filepath of the keyword list                                 | ./keywords.txt |
| --max_num_images           | Max number of images to download                             | 200            |
| --save_root_dir            | Root directory to save downloaded images. This directory will be removed after being archived. | ./Image        |
| --archive_save_dir         | Directory to save archive files                              | ./Archive      |
| --overwrite                | Overwrite existing directories                               |                |
| --archive_format           | Format of archive files. *zip*, *tar*, *gztar*, *bztar*, and *xztar* are supported. | gztar          |
| --num_keywords_per_archive | Number of keywords per archive                               | 100            |
| --progress_log_filepath    | Filepath of the log file to record progress                  | ./progress.txt |
| --index_lower_bound        | Start index of keywords. Keywords between [index_lower_bound, index_upper_bound) are used by this downloader. | 0              |
| --index_upper_bound        | End index of keywords. Keywords between [index_lower_bound, index_upper_bound) are used by this downloader. When a negative value is set to this option, the upper bound of the index is the total number of keywords. | -1             |
| --feeder_threads           | Number of feeder threads                                     | 4              |
| --parser_threads           | Number of parser threads                                     | 4              |
| --downloader_threads       | Number of downloader threads                                 | 8              |
| --num_formatter_processes  | Number of formatter processes                                | 4              |
| --image_width              | Width of images                                              | 256            |
| --image_height             | Height of images                                             | 256            |
| --no_format_images         | Images are not formatted if set                              |                |
| --no_archive_images        | Images are not archived if set                               |                |

