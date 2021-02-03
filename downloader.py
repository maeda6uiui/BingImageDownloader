import hashlib
import imghdr
import logging
import os
import posixpath
import re
import urllib.parse
import urllib.request

default_logger=logging.getLogger(__name__)
default_logger.setLevel(level=logging.INFO)

class BingImageDownloader:
    def __init__(
        self,
        keyword:str,
        limit:int,
        save_root_dir:str,
        safe_search:bool,
        timeout:int,
        filters:str,
        logger:logging.Logger=default_logger):
        self.download_count=0
        self.keyword=keyword
        self.limit=limit
        self.adult="on" if safe_search else "off"
        self.timeout=timeout
        self.filters=filters
        self.logger=logger

        self.headers={}
        self.page_counter=0

        #Save directory is represented by the MD5 hash of the keyword
        keyword_hash=hashlib.md5(keyword.encode()).hexdigest()
        self.save_dir=os.path.join(os.getcwd(),save_root_dir,keyword_hash)

        os.makedirs(self.save_dir,exist_ok=True)
        logger.info("[{}] ({})".format(keyword,keyword_hash))

        #Create a text file keeping the keyword
        info_filepath=os.path.join(self.save_dir,"info.txt")
        with open(info_filepath,"w",encoding="utf_8") as w:
            w.write("{}\n".format(keyword))

    def save_image(self,link:str,save_filepath:str):
        request=urllib.request.Request(link,None,self.headers)
        image=urllib.request.urlopen(request,timeout=self.timeout).read()

        if not imghdr.what(None,image):
            raise RuntimeError("Invalid image")
        else:
            with open(save_filepath,"wb") as f:
                f.write(image)
    
    def download_image(self,link:str):
        self.download_count+=1

        try:
            #Get the image link
            path=urllib.parse.urlsplit(link).path
            filename=posixpath.basename(path).split("?")[0]
            filetype=filename.split(".")[-1]
            if filetype.lower() not in ["jpe","jpeg","jfif","exif","tiff","gif","bmp","png","webp","jpg"]:
                filetype="jpg"

            #Download the image
            self.logger.info("Downloading image #{} from {}".format(self.download_count,link))

            save_filename=str(self.download_count).zfill(6)+"."+filetype
            save_filepath=os.path.join(self.save_dir,save_filename)

            self.save_image(link,save_filepath)
        
        except Exception as e:
            self.download_count-=1
            self.logger.error("Failed to download {}\t{}".format(link,e))

    def run(self):
        while self.download_count<self.limit:
            self.logger.info("Indexing page: {}".format(self.page_counter+1))

            request_url="https://www.bing.com/images/async?q=" \
                +urllib.parse.quote_plus(self.keyword) \
                +"&first="+str(self.page_counter)+"&count="+str(self.limit) \
                +"&adlt="+self.adult+"&qft="+self.filters
            request=urllib.request.Request(request_url,None,headers=self.headers)
            response=urllib.request.urlopen(request)
            html=response.read().decode("utf_8")
            links=re.findall("murl&quot;:&quot;(.*?)&quot;",html)

            self.logger.info("Indexed {} images on page {}".format(len(links),self.page_counter+1))
            self.logger.info("==============================")

            for link in links:
                if self.download_count<self.limit:
                    self.download_image(link)
                else:
                    self.logger.info("Downloaded {} images".format(self.download_count))
                    self.logger.info("==============================")
                    break

            self.page_counter+=1
