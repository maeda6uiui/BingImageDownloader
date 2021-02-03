import glob
import logging
import os
from PIL import Image

default_logger=logging.getLogger(__name__)
default_logger.setLevel(level=logging.INFO)

def format_images(
    target_dir:str,
    image_width:int,
    image_height:int,
    logger:logging.Logger=default_logger):
    """
    format_images resizes images and converts them to JPEG.
    Invalid images are removed.
    """
    pathname=os.path.join(target_dir,"**","*[!txt]")
    files=glob.glob(pathname)

    for file in files:
        try:
            image=Image.open(file)
            image=image.resize((image_width,image_height))
            if image.mode in ("RGBA","P"):
                image=image.convert("RGB")

            filepath_wo_extension=os.path.splitext(file)[0]
            save_filepath=filepath_wo_extension+".jpg"

            image.save(save_filepath)

        except Exception as e:
            logger.error("Failed to format {}\t{}".format(file,e))
            os.remove(file) #Remove this invalid file

            continue
