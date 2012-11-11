from coldbrew import get_string_from_path, compile_from_path, \
    settings as coldbrew_settings, save_compiled_string
from coldbrew.exceptions import ColdBrewCompileError
from django.conf import settings
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
 
    def handle(self, *args, **options):
        for static_dir in settings.STATICFILES_DIRS:
            for root, dirs, files in os.walk(static_dir):
                for f in files:
                    fullpath = os.path.join(root, f)

                    try:
                        filename = os.path.split(fullpath)[-1]
                        quiet, compile_result = compile_from_path(fullpath)
                        if not quiet:
                            if filename.endswith(".coffee"):
                                raise ColdBrewCompileError(fullpath, compile_result)
                            else:
                                print "Not compiling %s; doesn't look like coffeescript, didn't end in .coffee" % fullpath
                                continue
                        else:
                            save_compiled_string(compile_result, filename)
                            print "Compiled %s" % fullpath
                    except UnicodeDecodeError:
                        print "Not compiling %s; file is not Unicode" % fullpath
                        continue
                    

                    