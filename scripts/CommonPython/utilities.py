import glob, os

def parse_ignore_files(ignore_file, path_prefixes = [""]):
    result = []
    for line in ignore_file.read().splitlines():
        for prefix in path_prefixes:
            result.append(os.path.join(prefix,line.strip()))
    return result

def is_enabled_file(file, skip_files):
    for skip_file in skip_files:
        if glob.fnmatch.fnmatch(file, skip_file):
            return False
    return True