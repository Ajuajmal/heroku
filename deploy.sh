#!/bin/sh
set -euf
if ! cmp -s package.json .deployed.package.json; then
	npm prune
	npm install
	cp package.json .deployed.package.json
fi
nodejs node_modules/.bin/gulp
rebuilt_ve=0
if ! cmp -s requirements.txt .deployed.requirements.txt; then
	rm -rf ve
	python3 -m venv --system-site-packages ve
	ve/bin/python -m pip install -r requirements.txt
	cp requirements.txt .deployed.requirements.txt
	rebuilt_ve=1
fi
ve/bin/python manage.py collectstatic --noinput
ve/bin/python manage.py migrate --noinput
ve/bin/python manage.py load_pages
ve/bin/python manage.py load_sponsors

# Periodic tasks that we just do on deploy out of lazyness:
ve/bin/python manage.py clearsessions
ve/bin/python manage.py cleanupregistration

touch wsgi.py
