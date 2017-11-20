import getpass
import glob
import inspect
import os
import re
import shutil


def cwd():
    """Returns current working directory"""
    return os.getcwd()


def chdir(path):
    """Changes current working directory"""
    os.chdir(path)


def pydir():
    """Returns script directory"""
    return os.path.dirname((inspect.getfile(inspect.currentframe())))


def user():
    """Returns current user name"""
    return getpass.getuser()


USER = "C:/Users/{0}/".format(user())
DESKTOP = "{0}/Desktop/".format(USER)
ONEDRIVE = "{0}/OneDrive/".format(USER)


def isdir(src):
    """Checks if src is a directory"""
    return os.path.isdir(src)


def isfile(src):
    """Checks if src is a file"""
    return os.path.isfile(src)


def exists(src):
    """Checks if src exists"""
    return os.path.exists(src)


def mkdirs(path):
    """Creates directories recursively"""
    os.makedirs(path)


def files(path, filter=None, recursive=True):
    """Returns all files"""
    if filter:
        files = []
        for rule in filter:
            files.extend(list(glob.iglob("{0}/**/{1}".format(path, rule), recursive=recursive)))
        return files
    return list(glob.iglob("{0}/**/*.*".format(path), recursive=recursive))


def ext(file, dot=False):
    """Returns file extension"""
    ext = os.path.splitext(file)[1]
    return ext if dot else ext[1:]


def remove_ext(file):
    """Returns file without extension"""
    return os.path.splitext(file)[0]


def filename(file, ext=True):
    """Returns file name"""
    file = os.path.basename(file)
    return file if ext else remove_ext(file)


def dirname(file):
    """Returns the directory name of a file"""
    return os.path.dirname(file)


def abspath(file):
    """Returns absolute path for a file"""
    return os.path.abspath(file)


def sort_by(files, key=lambda x: x, reverse=False):
    """Sorts a file list by criteria"""
    return sorted(files, key=lambda x: key(filename(x)), reverse=reverse)


def copy(src, dst):
    """Copies files from one place to another"""
    if not exists(src):
        raise Exception("{0} does no exist".format(src))
    if isfile(src):
        if not exists(dst):
            mkdirs(dst)
        shutil.copy(src, dst)
    else:
        shutil.copytree(src, dst)


def move(src, dst):
    """Moves files form one place to another"""
    if not exists(src):
        raise Exception("{0} does not exist".format(src))
    if not exists(dst):
        mkdirs(dst)
    shutil.move(src, dst)
    return 0


def remove(src):
    """Removes file or files from a directory"""
    if not exists(src):
        raise Exception("{0} does not exist".format(src))
    if isfile(src):
        try:
            os.remove(src)
        except:
            return os.system("DEL {0} >nul".format(src))
    else:
        try:
            shutil.rmtree(src)
        except:
            return os.system("RD {0} /S /Q >nul".format(src))
    return 0


def remove_empty_folders(path):
    """Removes empty folders recursively"""
    if not isdir(path):
        return

    folders = os.listdir(path)
    if folders:
        for folder in folders:
            full_path = os.path.join(path, folder)
            if isdir(full_path):
                remove_empty_folders(full_path)

    folders = os.listdir(path)
    if len(folders) == 0:
        remove(path)


def filter(files, regex, ext=True):
    """
    Filters files with regular expressions
    .       match any character
    *       match any repetition of characters (.* any sequence)
    \       escape following character
    ^       start of string
    $       end of string
    ()      enclose expression
    [A-Z]   sequence of characters
    {m, n}  characters must appear m to n times
    (?:1|2) must be one of the options
    """
    matching = []
    other = []
    for file in files:
        if re.match(r"{0}".format(regex), filename(file, ext=ext)):
            matching.append(file)
        else:
            other.append(file)
    return matching, other


def remove_duplicates(files):
    """Removes duplicate files"""
    test = set([filename(file) for file in files])
    if len(test) == len(files):
        return files

    result = []
    for i in range(0, len(files)):
        duplicate = False
        for j in range(i + 1, len(files)):
            if filename(files[i]) == filename(files[j]):
                duplicate = True
        if not duplicate:
            result.append(files[i])
    return result


def cd_back(path):
    """Goes one folder back"""
    path = path.replace("\\\\", "/").replace("\\", "/")
    parts = path.split("/")
    result = parts[0]
    for i in range(1, len(parts) - 1):
        result += "/{0}".format(parts[i])
    return result


def symlink(src, dst):
    """Creates symbolic link"""
    parent = cd_back(dst)
    if not exists(parent):
        mkdirs(parent)
    return os.system("mklink /d \"{0}\" \"{1}\"".format(dst, src))


def zip(dst, *src, suppress=True):
    """Creates a 7z archive"""
    cmd = "7z a -t7z -m0=lzma2 -mx=9 -aoa -mfb=64 -md=32m -ms=on -mhe \"{0}\"{1}"
    if suppress:
        cmd += " >nul"
    files = ""
    for path in src:
        files += " \"{0}\"".format(path)
    return os.system(cmd.format(dst, files))
