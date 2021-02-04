#!python3.6
import argparse
import glob
import hashlib
import logging
import multiprocessing
import os
import shutil
import sys
from icrawler.builtin import BingImageCrawler
from typing import Any,List

sys.path.append(".")
from postprocessing import format_images

logging_fmt = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(format=logging_fmt)

def get_md5_hash(keyword:str)->str:
    return hashlib.md5(keyword.encode()).hexdigest()

def split_list(l:List[Any],n:int):
    for i in range(n):
        yield l[i*len(l)//n:(i+1)*len(l)//n]

def crawl_images(
    keyword:str,
    max_num_images:int,
    save_dir:str,
    feeder_threads:int,
    parser_threads:int,
    downloader_threads:int):
    crawler=BingImageCrawler(
        feeder_threads=feeder_threads,
        parser_threads=parser_threads,
        downloader_threads=downloader_threads,
        log_level=logging.ERROR,
        storage={"root_dir":save_dir},
    )
    crawler.crawl(keyword=keyword,max_num=max_num_images)

def formatter_worker(**kwargs):
    target_dirs:List[str]=kwargs["target_dirs"]
    image_width:int=kwargs["image_width"]
    image_height:int=kwargs["image_height"]

    for target_dir in target_dirs:
        format_images(target_dir,image_width,image_height)

def archive_images(
    archive_filepath:str,
    archive_format:str,
    save_root_dir:str):
    shutil.make_archive(archive_filepath,archive_format,base_dir=save_root_dir)
    shutil.rmtree(save_root_dir)

def main(args):
    keywords_filepath:str=args.keywords_filepath
    max_num_images:int=args.max_num_images
    image_width:int=args.image_width
    image_height:int=args.image_height
    save_root_dir:str=args.save_root_dir
    archive_save_dir:str=args.archive_save_dir
    archive_format:str=args.archive_format
    overwrite:bool=args.overwrite
    progress_log_filepath:str=args.progress_log_filepath
    index_lower_bound:int=args.index_lower_bound
    index_upper_bound:int=args.index_upper_bound
    feeder_threads:int=args.feeder_threads
    parser_threads:int=args.parser_threads
    downloader_threads:int=args.downloader_threads
    num_formatter_processes:int=args.num_formatter_processes
    num_keywords_per_archive:int=args.num_keywords_per_archive
    no_format_images:bool=args.no_format_images
    no_archive_images:bool=args.no_archive_images

    os.makedirs(save_root_dir,exist_ok=overwrite)
    os.makedirs(archive_save_dir,exist_ok=overwrite)

    progress_logger=logging.getLogger("progress_loggger")
    progress_logger.setLevel(level=logging.INFO)
    handler=logging.FileHandler(progress_log_filepath,"a",encoding="utf_8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(logging_fmt))
    progress_logger.addHandler(handler)

    progress_logger.info(args)

    with open(keywords_filepath,"r",encoding="utf_8") as r:
        keywords=r.read().splitlines()

    if index_upper_bound<0:
        index_upper_bound=len(keywords)

    for idx in range(index_lower_bound,index_upper_bound,num_keywords_per_archive):
        progress_logger.info("Batch start index: {}".format(idx))

        #Download
        batch_keywords=keywords[idx:idx+num_keywords_per_archive]
        for i,keyword in enumerate(batch_keywords):
            progress_logger.info("{}\t{}".format(idx+i,keyword))

            title_hash=get_md5_hash(keyword)
            save_dir=os.path.join(save_root_dir,title_hash)
            os.makedirs(save_dir,exist_ok=True)

            info_filepath=os.path.join(save_dir,"info.txt")
            with open(info_filepath,"w",encoding="utf_8") as w:
                w.write("{}\n".format(keyword))

            crawl_images(keyword,max_num_images,save_dir,feeder_threads,parser_threads,downloader_threads)

        #Format
        if not no_format_images:
            subdirs=glob.glob(os.path.join(save_root_dir,"*"))
            subbatch_subdirs=list(split_list(subdirs,num_formatter_processes))

            formatter_processes:List[multiprocessing.Process]=[]
            for i in range(num_formatter_processes):
                kwargs={
                    "target_dirs":subbatch_subdirs[i],
                    "image_width":image_width,
                    "image_height":image_height
                }
                formatter_process=multiprocessing.Process(target=formatter_worker,kwargs=kwargs)
                formatter_processes.append(formatter_process)

            for formatter_process in formatter_processes:
                formatter_process.start()
            for formatter_process in formatter_processes:
                formatter_process.join()

        #Archive
        if not no_archive_images:
            batch_start_index=idx
            batch_end_index=min(idx+num_keywords_per_archive,index_upper_bound)
            archive_filepath=os.path.join(archive_save_dir,"images_{}_{}".format(batch_start_index,batch_end_index))

            shutil.make_archive(archive_filepath,archive_format,base_dir=save_root_dir)
            shutil.rmtree(save_root_dir)

            progress_logger.info("Created an archive file {}".format(archive_filepath))

        progress_logger.info("====================")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--keywords_filepath",type=str,default="./keywords.txt")
    parser.add_argument("--max_num_images",type=int,default=200)
    parser.add_argument("--image_width",type=int,default=256)
    parser.add_argument("--image_height",type=int,default=256)
    parser.add_argument("--save_root_dir",type=str,default="./Image")
    parser.add_argument("--archive_save_dir",type=str,default="./Archive")
    parser.add_argument("--archive_format",type=str,default="gztar")
    parser.add_argument("--overwrite",action="store_true")
    parser.add_argument("--progress_log_filepath",type=str,default="./progress.txt")
    parser.add_argument("--index_lower_bound",type=int,default=0)
    parser.add_argument("--index_upper_bound",type=int,default=-1)
    parser.add_argument("--feeder_threads",type=int,default=4)
    parser.add_argument("--parser_threads",type=int,default=4)
    parser.add_argument("--downloader_threads",type=int,default=8)
    parser.add_argument("--num_formatter_processes",type=int,default=4)
    parser.add_argument("--num_keywords_per_archive",type=int,default=100)
    parser.add_argument("--no_format_images",action="store_true")
    parser.add_argument("--no_archive_images",action="store_true")
    args=parser.parse_args()

    main(args)
