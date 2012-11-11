from coldbrew.exceptions import ColdBrewCompileError
from coldbrew.cache import get_cache_key, get_hexdigest, get_hashed_mtime
from . import settings
import logging
import os
import shlex
import subprocess

logger = logging.getLogger("coffeescript")

def get_string_from_path(source_file_path):
    source_file = open(source_file_path)
    coffeescript_string = source_file.read()
    source_file.close()
    return coffeescript_string

def compile(coffeescript_string):
    args = shlex.split("%s -c -s -p" % settings.COFFEESCRIPT_EXECUTABLE, posix=settings.POSIX_COMPATIBLE)
    try:
        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        raise RuntimeError('CoffeeScript Executable not found.  Is it installed in your OS?')
    
    out, errors = p.communicate(coffeescript_string.encode("utf-8"))
    
    if not (out or errors):
        raise ColdBrewCompileError(coffeescript_string, 'Process resulted in no output and no errors.  WTF?')
    
    if errors:
        logger.error(errors)
        
        if settings.COLDBREW_FAIL_LOUD:
            return False, errors
        else:
            return True, errors

    if out:
        return True, out.decode("utf-8")