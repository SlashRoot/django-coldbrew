from coldbrew.cache import get_cache_key, get_hexdigest, get_hashed_mtime
import subprocess
import shlex
from django.conf import settings
import os

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
    
    if errors:
        logger.error(errors)
        
        if settings.COLDBREW_FAIL_LOUD:
            raise ColdBrewCompileError('Compiling %s \n\n %s' % (full_path, errors))
        else:
            return errors

    if out:
        return out.decode("utf-8")