from coldbrew.exceptions import ColdBrewCompileError
from coldbrew.cache import get_cache_key, get_hexdigest, get_hashed_mtime
from . import settings as coldbrew_settings
from django.conf import settings as django_settings
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
    
    
def compile_from_path(source_file_path):
    coffee_string = get_string_from_path(source_file_path)
    if coffee_string:
        quiet, compile_result = compile(coffee_string)
        return quiet, compile_result
    else:
        return False, "Coffee String was blank.  Weak Coffee don't brew."

def save_compiled_string(compiled_string, filename):
    if filename.endswith(".coffee"):
        base_filename = filename[:-7]
    else:
        base_filename = filename
    output_directory = os.path.join(django_settings.STATIC_ROOT, 
                                coldbrew_settings.COLDBREW_CUP)
    
    output_path = os.path.join(output_directory, 
                               "%s.js" % base_filename)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    compiled_file = open(output_path, "w+")
    compiled_file.write(compiled_string)
    compiled_file.close()
    