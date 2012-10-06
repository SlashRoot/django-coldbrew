from ..cache import get_cache_key, get_hexdigest, get_hashed_mtime
from ..settings import COFFEESCRIPT_EXECUTABLE, COFFEESCRIPT_USE_CACHE, \
    COFFEESCRIPT_CACHE_TIMEOUT, COFFEESCRIPT_OUTPUT_DIR, POSIX_COMPATIBLE, \
    COFFEESCRIPT_LOCATION
from ..exceptions import ColdBrewCompileError
from django.conf import settings
from django.core.cache import cache
from django.template.base import Library, Node
import logging
import os
import shlex
import subprocess


logger = logging.getLogger("coffeescript")
register = Library()


class InlineCoffeescriptNode(Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def compile(self, source):
        args = shlex.split("%s -c -s -p" % COFFEESCRIPT_EXECUTABLE, posix=POSIX_COMPATIBLE)

        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, errors = p.communicate(source.encode("utf-8"))
        if out:
            return out.decode("utf-8")
        elif errors:
            return errors.decode("utf-8")

        return u""

    def render(self, context):
        output = self.nodelist.render(context)

        if COFFEESCRIPT_USE_CACHE:
            cache_key = get_cache_key(get_hexdigest(output))
            cached = cache.get(cache_key, None)
            if cached is not None:
                return cached
            output = self.compile(output)
            cache.set(cache_key, output, COFFEESCRIPT_CACHE_TIMEOUT)
            return output
        else:
            return self.compile(output)


@register.tag(name="inlinecoffeescript")
def do_inlinecoffeescript(parser, token):
    nodelist = parser.parse(("endinlinecoffeescript",))
    parser.delete_first_token()
    return InlineCoffeescriptNode(nodelist)


@register.simple_tag
def coffeescript(path):

    full_path = os.path.join(COFFEESCRIPT_LOCATION, path)
    filename = os.path.split(path)[-1]

    output_directory = os.path.join(COFFEESCRIPT_LOCATION, COFFEESCRIPT_OUTPUT_DIR, os.path.dirname(path))

    hashed_mtime = get_hashed_mtime(full_path)

    if filename.endswith(".coffee"):
        base_filename = filename[:-7]
    else:
        base_filename = filename

    output_path = os.path.join(output_directory, "%s-%s.js" % (base_filename, hashed_mtime))

    if not os.path.exists(output_path):
        source_file = open(full_path)
        source = source_file.read()
        source_file.close()

        args = shlex.split("%s -c -s -p" % COFFEESCRIPT_EXECUTABLE, posix=POSIX_COMPATIBLE)
        try:
            p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            raise RuntimeError('CoffeeScript Executable not found.  Is it installed in your OS?')
        out, errors = p.communicate(source)
        if out:
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            compiled_file = open(output_path, "w+")
            compiled_file.write(out)
            compiled_file.close()

            # Remove old files
            compiled_filename = os.path.split(output_path)[-1]
            for filename in os.listdir(output_directory):
                if filename.startswith(base_filename) and filename != compiled_filename:
                    os.remove(os.path.join(output_directory, filename))
        elif errors:
            logger.error(errors)
            
            if settings.COLDBREW_FAIL_LOUD:
                raise ColdBrewCompileError('Compiling %s \n\n %s' % (full_path, errors))
            
            return path

    # If DEBUG is on, we want to see if a staticfiles directory is at the beginning
    # of our output_path.  If it is, we know to use that path instead of STATIC_ROOT.
    if settings.DEBUG:
        for static_dir in settings.STATICFILES_DIRS:
            if output_path.startswith(static_dir):
                return output_path[len(static_dir):].replace(os.sep, '/').lstrip("/")
        
    
    return output_path[len(settings.STATIC_ROOT):].replace(os.sep, '/').lstrip("/")
