import hashlib
import os
import os.path
import datetime
import errno
import re


def no_error_on_exist(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    return wrapper


force_make_dirs = no_error_on_exist(os.makedirs)


force_symlink = no_error_on_exist(os.symlink)


def md5_checksum(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def read_first_checksum(file_name):
    with open(file_name, 'r') as f:
        for line in f:
            checksum = line.rstrip().split('  ')[0]
            return checksum


def file_mtime(path):
    mtime = os.path.getmtime(path)
    return datetime.datetime.utcfromtimestamp(mtime)


def is_readgroup(string):
    return string.startswith('@RG')


def sm_tag_for_readgroup_string(rg_string):
    sm_match = re.search(r'SM:(\S+)', rg_string)
    return sm_match.group(1)


def id_for_readgroup_string(rg_string):
    # ID:\d+
    seqid_match = re.search(r'ID:(\d+)', rg_string)
    return seqid_match.group(1)
