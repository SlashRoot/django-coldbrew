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

    if not settings.DEBUG:
        return "%s/%s.js" % (settings.COLDBREW_CUP,
                             base_filename)

    full_path = os.path.join(coldbrew_settings.COFFEESCRIPT_LOCATION, source_file_path)
    hashed_mtime = get_hashed_mtime(full_path)
    
    # TODO: Resolve #7 and fix this.
    # TODO: For the moment, we aren't even going to compile at all if debug=False
    if not settings.DEBUG:
        output_parent = settings.STATIC_ROOT
    else:
        output_parent = settings.STATICFILES_DIRS[0]

    output_directory = os.path.join(output_parent, coldbrew_settings.COLDBREW_CUP)
    output_path = os.path.join(output_directory, "%s-%s.js" % (base_filename, hashed_mtime))

    # Now we know to which path we'll write; let's just make the URL.
    url = "%s/%s-%s.js" % (settings.COLDBREW_CUP,
                             base_filename,
                             hashed_mtime
                             )
    
    if not settings.DEBUG:
        return url

    # If the file already exists, we're not going to even bother reading the input again.
    # Instead, just return the URL.
    if os.path.exists(output_path):    
        return url


    coffeescript_string = get_string_from_path(full_path)
    quiet, compile_result = compile(coffeescript_string)
    
    if not quiet:
        raise ColdBrewCompileError(full_path, compile_result)
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    compiled_file = open(output_path, "w+")
    compiled_file.write(compile_result)
    compiled_file.close()

    return url
