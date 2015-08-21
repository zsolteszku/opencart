import os
import sys
import urllib2
import shutil


class PackageInfo:
    package_name = None
    package_download_url = None

    def __init__(self, package_name, package_download_url):
        self.package_name = package_name
        self.package_download_url = package_download_url


python_modules_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".python_modules")
temp_dir = os.path.join(python_modules_path, ".temp")


def download(package_info):
    print "Downloading {} package(url = \"{}\")".format(package_info.package_name, package_info.package_download_url)

    url = package_info.package_download_url

    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    file_path = os.path.join(temp_dir, file_name)
    f = open(file_path, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,

    f.close()
    return file_path


def get_tar_dir(tar_file):
    import tarfile

    tar = tarfile.open(tar_file, "r:gz")
    for tarinfo in tar:
        if tarinfo.isdir():
            print "a directory."
            tar.close()
            return tarinfo.name
    tar.close()


def unzip_tar_gz(tar_gz_file, path_to_unzip):
    import tarfile

    print "Unzip \"{}\" to \"{}\"".format(tar_gz_file, path_to_unzip)
    extracted_dir_name = get_tar_dir(tar_gz_file)
    tar = tarfile.open(tar_gz_file)
    if not os.path.exists(path_to_unzip):
        os.makedirs(path_to_unzip)
    tar.extractall(path=path_to_unzip)
    tar.close()
    return extracted_dir_name


def install(downloaded_file, package_info):
    print "\rInstalling {}...".format(package_info.package_name)
    dir_name = unzip_tar_gz(downloaded_file, python_modules_path)
    path_to_package = os.path.join(python_modules_path, package_info.package_name)
    os.rename(os.path.join(python_modules_path, dir_name), path_to_package)
    setup_py_file = os.path.join(path_to_package, "setup.py")
    if os.path.exists(setup_py_file):
        print "Found setup.py. So Setup package: {}".format(package_info.package_name)
        import subprocess

        subprocess.call(['python', setup_py_file, 'install'])


def download_and_install(package_info):
    downloaded_file = download(package_info)
    install(downloaded_file, package_info)
    os.remove(downloaded_file)
    shutil.rmtree(temp_dir)


def install_if_necessary(package_info):
    path_to_package = os.path.join(python_modules_path, package_info.package_name)
    if not os.path.exists(path_to_package):
        print "Not found {}, so downloading and installing it!".format(package_info.package_name)
        download_and_install(package_info)
    sys.path.append(path_to_package)