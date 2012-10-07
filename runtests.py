import os
os.environ["DJANGO_SETTINGS_MODULE"] = "coldbrew.tests.test_settings"

from unittest import main
from coldbrew.tests.tests import CoffeeScriptTestCase


if __name__ == '__main__':
    main()

