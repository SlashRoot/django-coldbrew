ColdBrew
========

django-coldbrew started as a fork of Django Coffeescript.

ColdBrew provides template tags to compile CoffeeScript into JavaScript from templates.
It works with both inline code and external files.

Installation
************

1. Add ``"coldbrew"`` to ``INSTALLED_APPS`` setting.
2. Make sure that you have ``coffee`` executable installed. See
   `CoffeeScript official site <http://jashkenas.github.com/coffee-script/>`_ for details.
3. Optionally, you can specify the full path to ``coffee`` executable with ``COFFEESCRIPT_EXECUTABLE`` setting.
   By default it's set to ``coffee``.

Example Usage
*************

External file
-------------

::
    {% load coffeescript %}

    <script type="text/javascript"
            src="{{ STATIC_URL}}{% coffeescript "path/to/script.coffee" %}">
    </script>

renders to

::

    <script type="text/javascript"
            src="/media/COFFEESCRIPT_CACHE/path/to/script-91ce1f66f583.js">
    </script>


Inline
------

::

    {% load coldbrew %}

    <script type="text/javascript">
      {% inlinecoffeescript %}
        console.log "Hello, World!"
      {% endinlinecoffeescript %}
    </script>

renders to

::

      <script type="text/javascript">
        (function() {
      console.log("Hello, World!");
    }).call(this);

      </script>


Note that by default compiled files are saved into ``COFFEESCRIPT_CACHE`` folder under your ``STATIC_ROOT`` (or ``MEDIA_ROOT`` if you have no ``STATIC_ROOT`` in your settings).
You can change this folder name with ``COFFEESCRIPT_OUTPUT_DIR`` setting.


Settings
********

``COFFEESCRIPT_EXECUTABLE``
    Path to CoffeeScript compiler executable. Default: ``"coffee"``.

``COFFEESCRIPT_OUTPUT_DIR``
    Output directory for compiled external scripts. It's relative to ``STATIC_ROOT``. Default: ``"COFFEESCRIPT_CACHE"``.

``COFFEESCRIPT_USE_CACHE``
    Whether to use cache for inline scripts. Default: ``True``.

``COFFEESCRIPT_CACHE_TIMEOUT``
    Cache timeout for inline scripts (in seconds). Default: 30 days.

``COFFEESCRIPT_MTIME_DELAY``
    Cache timeout for reading the modification time of external scripts (in seconds). Default: 10 seconds.
    
``COLDBREW_FAIL_LOUD``
    If True, raise ColdBrewCompileError upon encountering compiling error.
    Otherwise, records to error log.
    Defaults to same as DEBUG.