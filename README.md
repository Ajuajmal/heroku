# Installing locally

* Checkout this repository
* Install Python and Node tools: `sudo apt install python3 virtualenv npm nodejs-legacy`
* Create a py3k virtualenv: `python3 -m venv ve`
* `ve/bin/python -m pip install wheel`
* Activate the virtualenv: `. ve/bin/activate`
* Install the requirements: `pip install -r requirements.txt`
* Create a `localsettings.py`: `cp localsettings.py.sample localsettings.py`
* Run migrations (creates the DB): `./manage.py migrate`
* Install JS toolchain and dependencies `npm install`
* Download and build static assets: `node_modules/.bin/gulp`
* Generate markdown page in DB: `./manage.py load_pages`
* Create the admin account: `./manage.py createsuperuser`
* Run the webserver: `./manage.py runserver`


# Installing in production
* apt install
  - libjs-jquery
  - memcached
  - nodejs-legacy
  - python3
  - python3-diff-match-patch
  - python3-django/stretch-backports
  - python3-django-crispy-forms
  - python3-django-jsonfield
  - python3-django-nose
  - python3-django-reversion
  - python3-djangorestframework
  - python3-libravatar
  - python3-markdown
  - python3-pil
  - python3-psycopg2
  - python3-requests
  - python3-tz
  - python3-venv
  - python3-wheel
  - python3-yaml
* install npm from git (put ~/git/npm/bin/npm-cli.js on PATH as npm)

# Also see

https://wiki.debconf.org/wiki/Wafer
