# -*- coding: utf-8 -*-


import os
import logging

from os import path
from setuptools.command.build_py import build_py
from shutil import copyfile
from urllib.parse import urlparse
from zipfile import ZipFile


logger = logging.getLogger(__name__)


class WebResourceCommand(build_py):

    def run(self):
        with open('web_resource_requirements.txt', 'rb') as file_handle:
            web_resource_urls =\
                [web_resource_url.strip() for web_resource_url in file_handle.read().decode('utf-8').split('\n')]

        for web_resource_url in web_resource_urls:
            if len(web_resource_urls) > 0:
                satisfy_resource_requirement(web_resource_url)


def ensure_directory(dir_path):
    if not path.exists(dir_path):
        os.makedirs(dir_path)

    return dir_path


def ensure_web_resource_directory_cache():
    web_resource_cache_dir = '.web_resource_cache'
    return ensure_directory(web_resource_cache_dir)


def ensure_web_resource_directory():
    web_resource_directory_path = 'sciit/web/static'
    return ensure_directory(web_resource_directory_path)


def retrieve_resource_to_local_cache(resource_url):

    web_resource_cache_dir = ensure_web_resource_directory_cache()

    parsed_resource_url = urlparse(resource_url)
    cached_web_resource_file_path = web_resource_cache_dir + path.sep + os.path.basename(parsed_resource_url.path)

    if not path.exists(cached_web_resource_file_path):
        import requests
        response = requests.get(resource_url)
        with open(cached_web_resource_file_path, 'wb') as cached_web_resource_file_handle:
            cached_web_resource_file_handle.write(response.content)
            logger.info("Cached [%s]", cached_web_resource_file_path)

    return cached_web_resource_file_path


def satisfy_resource_requirement(resource_url):
    cached_web_resource_file_path = retrieve_resource_to_local_cache(resource_url)
    resource_dir_path = ensure_web_resource_directory()

    target_resource_filename = path.basename(cached_web_resource_file_path)
    resource_name, extension = path.splitext(target_resource_filename)

    if extension == '.zip':
        web_resource_zipfile = ZipFile(cached_web_resource_file_path)
        web_resource_zipfile.extractall(resource_dir_path)

    elif extension in {'.js', '.css'}:

        install_single_file(
            extension[1:],
            cached_web_resource_file_path,
            resource_dir_path, resource_name,
            target_resource_filename)


def install_single_file(
        extension, cached_web_resource_file_path, resource_dir_path, resource_name, target_resource_filename):

    target_resource_dir_path = resource_dir_path + path.sep + resource_name + path.sep + extension
    target_resource_file_path = target_resource_dir_path + path.sep + target_resource_filename

    if not path.exists(target_resource_dir_path):
        os.makedirs(target_resource_dir_path)

    copyfile(cached_web_resource_file_path, target_resource_file_path)
