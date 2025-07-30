"""
Author: HECE - University of Liege, Pierre Archambeau
Date: 2025

Copyright (c) 2025 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""


""" This module provides a downloader for the WOLFHECE dataset and other files freely available on the web. """

import re
import requests
import ftplib
from pathlib import Path
from enum import Enum
from typing import Union, Optional, List
from collections import namedtuple
import logging

class DownloadType(Enum):
    """ Enum to define the type of download. """
    HTTP = 'http'
    HTTPS = 'https'
    FTP = 'ftp'

class DownloadFiles(Enum):
    """ Enum to define the files to download. """
    WOLFARRAYS = ('bin', 'bin.txt')
    TIFARRAYS = ('tif',)
    TIFFARRAYS = ('tiff',)
    SHPFILES = ('shp', 'dbf', 'shx', 'prj', 'cpg', 'sbn', 'sbx')
    GPKGFILES = ('gpkg',)
    VECFILES = ('vec', 'vec.extra')
    VECZFILES = ('vecz', 'vecz.extra')
    PROJECTFILES = ('proj',)

class DonwloadDirectories(Enum):
    """ Enum to define the directories for downloads. """
    GDBFILES = ('gdb',)


GITLAB_EXAMPLE = 'https://gitlab.uliege.be/HECE/wolf_examples/-/raw/main'
DATADIR = Path(__file__).parent / 'data' / 'downloads'

def clean_url(url: str) -> str:
    """ Clean the URL by removing any query parameters or fragments.

    :param url: The URL to clean.
    :type url: str
    :return: The cleaned URL.
    :rtype: str
    """
    # Remove query parameters and fragments
    cleaned_url = re.sub(r'\?.*|#.*', '', url)
    # Remove trailing slashes
    cleaned_url = re.sub(r'/+$', '', cleaned_url)
    # Remove any leading or trailing whitespace
    cleaned_url = cleaned_url.strip()
    # Ensure slashes are consistent
    cleaned_url = re.sub(r'(?<!:)//+', '/', cleaned_url)
    # Convert Backslashes to forward slashes
    cleaned_url = cleaned_url.replace('\\', '/')
    # Ensure the URL starts with http:// or https://
    if not cleaned_url.startswith(('http://', 'https://', 'ftp://')):
        raise ValueError(f"Invalid URL: {url}. Must start with http://, https://, or ftp://")
    return cleaned_url.strip()

def download_file(url: str, destination: Union[str, Path] = None, download_type: DownloadType = DownloadType.HTTP, load_from_cache:bool = True) -> None:
    """ Download a file from the specified URL to the destination path.

    :param url: The URL of the file to download.
    :param destination: The path where the file will be saved.
    :param download_type: The type of download (HTTP, HTTPS, FTP).
    :type url: str
    :type destination: Union[str, Path]
    :type download_type: DownloadType
    :return: None
    :raises requests.HTTPError: If the HTTP request fails.
    """

    url = str(url).strip()
    # Clean the URL
    url = clean_url(url)

    if destination is None:
        try:
            destination = DATADIR / Path(url).parent.name / Path(url).name
        except:
            destination = DATADIR / Path(url).name
    # create the directory if it does not exist
    destination.parent.mkdir(parents=True, exist_ok=True)

    suffix = Path(url).suffix.lower()
    # remove point from the suffix for matching
    if suffix.startswith('.'):
        suffix = suffix[1:]

    # Find the download type based on the URL suffix
    for file_type_enum in DownloadFiles:
        if suffix in file_type_enum.value:
            file_type = file_type_enum
            break

    # Create a list of files to download based on the download type
    # by replacing suffix in the url with the appropriate file extensions
    to_download = []
    to_destination = []
    for ext in file_type.value:
        if ext.startswith('.'):
            ext = ext[1:]
        to_download.append(url.replace(suffix, f'{ext}'))
        to_destination.append(destination.with_suffix(f'.{ext}'))


    if download_type == DownloadType.HTTP or download_type == DownloadType.HTTPS:

        for url, destination in zip(to_download, to_destination):

            if load_from_cache and destination.exists():
                logging.info(f"File {destination} already exists. Skipping download.")
                continue

            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL: {url}. Must start with http:// or https://")

            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(destination, 'wb') as file:
                    file.write(response.content)
            except requests.HTTPError as e:
                logging.error(f"HTTP error occurred while downloading {url}: {e}")

    elif download_type == DownloadType.FTP:

        for url, destination in zip(to_download, to_destination):

            if load_from_cache and destination.exists():
                logging.info(f"File {destination} already exists. Skipping download.")
                continue

            if not url.startswith('ftp://'):
                raise ValueError(f"Invalid URL: {url}. Must start with ftp://")

            try:
                parsed_url = ftplib.parse_ftp_url(url)
                with ftplib.FTP(parsed_url.hostname) as ftp:
                    ftp.login()
                    with open(destination, 'wb') as file:
                        ftp.retrbinary(f'RETR {parsed_url.path}', file.write)
            except ftplib.all_errors as e:
                logging.error(f"FTP error occurred while downloading {url}: {e}")
    else:
        raise ValueError(f"Unsupported download type: {download_type}")

    return to_destination[0]

def toys_dataset(dir:str, file:str, load_from_cache:bool = True):
    """ Download toy files from the WOLFHECE dataset.

    :param dir: The directory where the file will be saved.
    :param file: The name of the file to download.
    :type dir: str
    :type file: str
    :return: The path to the downloaded file.
    """
    url = f"{GITLAB_EXAMPLE}/{dir}/{file}"
    destination = DATADIR / dir / file
    return download_file(url, destination, load_from_cache=load_from_cache)

if __name__ == "__main__":
    # Example usage
    print(download_file(r'https:\\gitlab.uliege.be\HECE\wolf_examples\-\raw\main\Extract_part_array\extraction.vec'))
    print(download_file('https://gitlab.uliege.be/HECE/wolf_examples/-/raw/main/Extract_part_array/extraction.vec'))
    print(download_file('https://gitlab.uliege.be/HECE/wolf_examples/-/raw/main/Extract_part_array/Array_vector.proj'))
    print(download_file('https://gitlab.uliege.be/HECE/wolf_examples/-/raw/main/Array_Theux_Pepinster/mnt.bin'))
    print(download_file('https://gitlab.uliege.be/HECE/wolf_examples/-/raw/main/Array_Theux_Pepinster/mnt.tif'))
    print(download_file('https://gitlab.uliege.be/HECE/wolf_examples/-/raw/main/PICC/PICC_Vesdre.shp'))
    print(toys_dataset('Extract_part_array', 'extraction.vec'))
