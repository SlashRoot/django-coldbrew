import os
from unittest import main
from coldbrew.tests.tests import CoffeeScriptTestCase

os.environ["DJANGO_SETTINGS_MODULE"] = "coldbrew.tests.django_settings"
if __name__ == '__main__':
    main()

