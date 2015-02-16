import os
import sys
import site

site.addsitedir('/var/www/html/jester5/jester_backend/venv/lib/python2.7/site-packages')
sys.path.append('/var/www/html/jester5/jester_backend')
sys.path.append('/var/www/html/jester5/jester_backend/jester')
os.environ['DJANGO_SETTINGS_MODULE'] = 'jester_backend.settings'

activate_env=("/var/www/html/jester5/jester_backend/venv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
