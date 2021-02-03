import argparse
import glob
import logging
import multiprocessing
import os
import shutil
import sys
from typing import Any, List

sys.path.append(".")
from downloader import BingImageDownloader
from postprocessing import format_images

logging_fmt="%(asctime)s %(levelname)s: %(message)s"

def downloader_worker(**kwargs):
    keywords:List[str]=kwargs["keywords"]
    limit:int=kwargs["limit"]
    safe_search:bool=kwargs["safe_search"]
    timeout:int=kwargs["timeout"]
    filters:str=kwargs["filters"]
    save_root_dir:str=kwargs["save_root_dir"]
    workers_log_dir:str=kwargs["workers_log_dir"]
    worker_index:int=kwargs["worker_index"]

    downloader_log_filepath=os.path.join(workers_log_dir,"downloader_log_{}.txt".format(worker_index))
    downloader_logger=logging.getLogger("downloader_logger_{}".format(worker_index))
    downloader_logger.setLevel(level=logging.INFO)
    handler=logging.FileHandler(downloader_log_filepath,"a",encoding="utf_8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(logging_fmt))
    downloader_logger.addHandler(handler)

    progress_log_filepath=os.path.join(workers_log_dir,"progress_log_{}.txt".format(worker_index))
    progress_logger=logging.getLogger("progress_logger_{}".format(worker_index))
    progress_logger.setLevel(level=logging.INFO)
    handler=logging.FileHandler(progress_log_filepath,"a",encoding="utf_8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(logging_fmt))
    progress_logger.addHandler(handler)

    for idx,keyword in enumerate(keywords):
        progress_logger.info("{}\t{}".format(idx,keyword))

        downloader=BingImageDownloader(
            keyword,
            limit,
            save_root_dir,
            safe_search,
            timeout,
            filters,
            logger=downloader_logger
        )
        downloader.run()

    progress_logger.info("====================")

def formatter_worker(**kwargs):
    target_dirs:List[str]=kwargs["target_dirs"]
    workers_log_dir:str=kwargs["workers_log_dir"]
    worker_index:int=kwargs["worker_index"]
    image_width:int=kwargs["image_width"]
    image_height:int=kwargs["image_height"]

    formatter_log_filepath=os.path.join(workers_log_dir,"formatter_log_{}.txt".format(worker_index))
    formatter_logger=logging.getLogger("formatter_logger_{}".format(worker_index))
    formatter_logger.setLevel(level=logging.INFO)
    handler=logging.FileHandler(formatter_log_filepath,"a",encoding="utf_8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(logging_fmt))
    formatter_logger.addHandler(handler)

    for target_dir in target_dirs:
        format_images(target_dir,image_width,image_height,logger=formatter_logger)

def split_list(l:List[Any],n:int):
    for i in range(n):
        yield l[i*len(l)//n:(i+1)*len(l)//n]

def main(args):
    keywords_filepath:str=args.keywords_filepath
    limit:int=args.limit
    disable_safe_search:bool=args.disable_safe_search
    timeout:int=args.timeout
    filters:str=args.filters
    save_root_dir:str=args.save_root_dir
    workers_log_dir:str=args.workers_log_dir
    archive_save_dir:str=args.archive_save_dir
    archive_format:str=args.archive_format
    overwrite:bool=args.overwrite
    num_keywords_per_archive:int=args.num_keywords_per_archive
    progress_log_filepath:str=args.progress_log_filepath
    index_lower_bound:int=args.index_lower_bound
    index_upper_bound:int=args.index_upper_bound
    num_downloader_processes:int=args.num_downloader_processes
    num_formatter_processes:int=args.num_formatter_processes
    image_width:int=args.image_width
    image_height:int=args.image_height
    no_format_images:bool=args.no_format_images
    no_archive_images:bool=args.no_archive_images

    os.makedirs(save_root_dir,exist_ok=overwrite)
    os.makedirs(workers_log_dir,exist_ok=overwrite)
    if not no_archive_images:
        os.makedirs(archive_save_dir,exist_ok=overwrite)

    progress_logger=logging.getLogger(__name__)
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
        batch_keywords=keywords[index_lower_bound:index_lower_bound+num_keywords_per_archive]
        subbatch_keywords=list(split_list(batch_keywords,num_downloader_processes))

        downloader_processes:List[multiprocessing.Process]=[]
        for i in range(num_downloader_processes):
            kwargs={
                "keywords":subbatch_keywords[i],
                "limit":limit,
                "safe_search":not disable_safe_search,
                "timeout":timeout,
                "filters":filters,
                "save_root_dir":save_root_dir,
                "workers_log_dir":workers_log_dir,
                "worker_index":i
            }
            downloader_process=multiprocessing.Process(target=downloader_worker,kwargs=kwargs)
            downloader_processes.append(downloader_process)

            progress_logger.info("Sub batch #{}\t{}".format(i,subbatch_keywords[i]))

        for downloader_process in downloader_processes:
            downloader_process.start()
        for downloader_process in downloader_processes:
            downloader_process.join()

        #Format
        if not no_format_images:
            subdirs=glob.glob(os.path.join(save_root_dir,"*"))
            subbatch_subdirs=list(split_list(subdirs,num_formatter_processes))

            formatter_processes:List[multiprocessing.Process]=[]
            for i in range(num_formatter_processes):
                kwargs={
                    "target_dirs":subbatch_subdirs[i],
                    "workers_log_dir":workers_log_dir,
                    "worker_index":i,
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
    parser.add_argument("--limit",type=int,default=200)
    parser.add_argument("--disable_safe_search",action="store_true")
    parser.add_argument("--timeout",type=int,default=60)
    parser.add_argument("--filters",type=str,default="")
    parser.add_argument("--save_root_dir",type=str,default="./Image")
    parser.add_argument("--workers_log_dir",type=str,default="./WorkersLog")
    parser.add_argument("--archive_save_dir",type=str,default="./Archive")
    parser.add_argument("--archive_format",type=str,default="gztar")
    parser.add_argument("--overwrite",action="store_true")
    parser.add_argument("--num_keywords_per_archive",type=int,default=100)
    parser.add_argument("--progress_log_filepath",type=str,default="./progress.txt")
    parser.add_argument("--index_lower_bound",type=int,default=0)
    parser.add_argument("--index_upper_bound",type=int,default=-1)
    parser.add_argument("--num_downloader_processes",type=int,default=5)
    parser.add_argument("--num_formatter_processes",type=int,default=5)
    parser.add_argument("--image_width",type=int,default=256)
    parser.add_argument("--image_height",type=int,default=256)
    parser.add_argument("--no_format_images",action="store_true")
    parser.add_argument("--no_archive_images",action="store_true")
    args=parser.parse_args()

    main(args)
