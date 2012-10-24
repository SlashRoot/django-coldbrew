from ..cache import get_cache_key, get_hexdigest, get_hashed_mtime
from .. import compile, get_string_from_path
from ..exceptions import ColdBrewCompileError
from django.conf import settings
from .. import settings as coldbrew_settings
from django.core.cache import cache
from django.template.base import Library, Node

import os

register = Library()


class InlineCoffeescriptNode(Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def compile(self, source):
        quiet, compile_result = compile(source)
    
        if not quiet:
            raise ColdBrewCompileError("Inline", compile_result)
        else:
            return compile_result
    
    def render(self, context):
        output = self.nodelist.render(context)

        if coldbrew_settings.COFFEESCRIPT_USE_CACHE:
            cache_key = get_cache_key(get_hexdigest(output))
            cached = cache.get(cache_key, None)
            if cached is not None:
                return cached
            output = self.compile(output)
            cache.set(cache_key, output, coldbrew_settings.COFFEESCRIPT_CACHE_TIMEOUT)
            return output
        else:
            return self.compile(output)


@register.tag(name="inlinecoffeescript")
def do_inlinecoffeescript(parser, token):
    nodelist = parser.parse(("endinlinecoffeescript",))
    parser.delete_first_token()
    return InlineCoffeescriptNode(nodelist)


@register.simple_tag
def coffeescript(source_file_path):
    
    filename = os.path.split(source_file_path)[-1]
    if filename.endswith(".coffee"):
        base_filename = filename[:-7]
    else:
        base_filename = filename

    output_directory = os.path.join(coldbrew_settings.COFFEESCRIPT_LOCATION, 
                                        coldbrew_settings.COFFEESCRIPT_OUTPUT_DIR, 
                                        os.path.dirname(source_file_path))
    full_path = os.path.join(coldbrew_settings.COFFEESCRIPT_LOCATION, source_file_path)
    hashed_mtime = get_hashed_mtime(full_path)
    output_path = os.path.join(output_directory, "%s-%s.js" % (base_filename, hashed_mtime))

    # If the file already exists, we're not going to even bother reading the input again.
    if os.path.exists(output_path):    
        return output_path[len(settings.STATIC_ROOT):].replace(os.sep, '/').lstrip("/")


    coffeescript_string = get_string_from_path(full_path)
    
    
    quiet, compile_result = compile(coffeescript_string)
    
    if not quiet:
        raise ColdBrewCompileError(full_path, compile_result)
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    compiled_file = open(output_path, "w+")
    compiled_file.write(compile_result)
    compiled_file.close()

    # Remove old files
    compiled_filename = os.path.split(output_path)[-1]
    for filename in os.listdir(output_directory):
        if filename.startswith(base_filename) and filename != compiled_filename:
            os.remove(os.path.join(output_directory, filename))

    # If DEBUG is on, we want to see if a staticfiles directory is at the beginning
    # of our output_path.  If it is, we know to use that path instead of STATIC_ROOT.
    if settings.DEBUG:
        for static_dir in settings.STATICFILES_DIRS:
            if output_path.startswith(static_dir):
                return output_path[len(static_dir):].replace(os.sep, '/').lstrip("/")
        
    relative_output_path = output_path[len(settings.STATIC_ROOT):].replace(os.sep, '/').lstrip("/")
    return relative_output_path
