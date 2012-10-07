from django.test import TestCase

from django.test.utils import override_settings

from django.template.base import Template
from django.template.context import RequestContext
from django.conf import settings

import os
import re
import time
import shutil

import sys

class CoffeeScriptTestCase(TestCase):

    def setUp(self):
        output_dir = os.path.join(settings.MEDIA_ROOT,
                                  settings.COFFEESCRIPT_OUTPUT_DIR)

        # Remove the output directory if it exists to start from scratch
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def test_inline_coffeescript(self):
        template = Template("""
        {% load coldbrew %}
        {% inlinecoffeescript %}console.log "Hello, World"
        {% endinlinecoffeescript %}
        """)
        hopeful_result = u"""(function() {\n
  console.log("Hello, World");\n
}).call(this);"""
        actual_result = template.render(RequestContext({})).strip()
        self.assertEqual(actual_result, hopeful_result)

    def test_external_coffeescript(self):

        template = Template("""
        {% load coldbrew %}
        {% coffeescript "scripts/test.coffee" %}
        """)
        compiled_filename_re = re.compile(r"COFFEESCRIPT_CACHE/scripts/test-[a-f0-9]{12}.js")
        compiled_filename = template.render(RequestContext({})).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename)))

        compiled_path = os.path.join(settings.MEDIA_ROOT, compiled_filename)
        compiled_content = open(compiled_path).read()
        compiled = """(function() {\n
  console.log("Hello, World!");\n
}).call(this);
"""
        self.assertEquals(compiled_content, compiled)

        # Change the modification time
        source_path = os.path.join(settings.MEDIA_ROOT, "scripts/test.coffee")
        os.utime(source_path, None)

        # The modification time is cached so the compiled file is not updated
        compiled_filename_2 = template.render(RequestContext({})).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename_2)))
        self.assertEquals(compiled_filename, compiled_filename_2)

        # Wait to invalidate the cached modification time
        time.sleep(settings.COFFEESCRIPT_MTIME_DELAY)

        # Now the file is re-compiled
        compiled_filename_3 = template.render(RequestContext({})).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename_3)))
        self.assertNotEquals(compiled_filename, compiled_filename_3)

        # Check that we have only one compiled file, old files should be removed

        compiled_file_dir = os.path.dirname(os.path.join(settings.MEDIA_ROOT,
                                                         compiled_filename_3))
        self.assertEquals(len(os.listdir(compiled_file_dir)), 1)
        
    @override_settings(COFFEESCRIPT_OUTPUT_DIR="%s/compiled/" % settings.STATIC_ROOT)
    def test_compiled_file_already_exists_file_is_not_written_again(self):
        template = Template("""
        {% load coldbrew %}
        {% coffeescript "scripts/test-already-exists.coffee" %}
        """)
        # Render it once.
        compiled_filename = template.render(RequestContext({})).strip()
        first_access = os.path.getatime("%s/%s" % (settings.STATIC_ROOT, compiled_filename))
        # ...and delete it.
        os.remove("%s/%s" % (settings.STATIC_ROOT, compiled_filename))
        
        # Now render it agian.
        compiled_filename_again = template.render(RequestContext({})).strip()
        second_access = os.path.getatime("%s/%s" % (settings.STATIC_ROOT, compiled_filename_again))
        
        # The file will have been accessed again.
        self.assertGreater(second_access, first_access)
        
        # Render it a third time - this time the file will already exist.
        compiled_filename_yet_again = template.render(RequestContext({})).strip()
        third_access = os.path.getatime("%s/%s" % (settings.STATIC_ROOT, compiled_filename_yet_again))
        
        # Since the file already existed, we won't have written again
        self.assertEqual(third_access, second_access)