import os
import stat
import shutil


def onerror(func, path, excp_info):
    os.chmod(path, stat.S_IWUSR)
    func(path)


def remove_existing_repo(path):
    if os.path.exists(path):
        shutil.rmtree(path, onerror=onerror)


def safe_create_repo_dir(path):
    remove_existing_repo(path)

    os.makedirs(path)
    os.makedirs(path + "/objects")
