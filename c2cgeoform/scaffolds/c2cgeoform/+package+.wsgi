import sys
sys.path.append('[DIR]/.build/venv/lib/python3.6/site-packages')

from pyramid.paster import get_app
application = get_app(
  '[DIR]/production.ini', 'main')
