# Mozilla Badges

Mozilla Badges powers [badges.mozilla.org][bmo], a badge service based on [django-badgekit][] and [playdoh][].

[bmo]: https://badges.mozilla.org/
[playdoh]: https://github.com/mozilla/playdoh
[django-badgekit]: https://github.com/mozilla/django-badgekit

## Bugs and Ideas

Feel free to file them [as issues on the mozilla-badges project][issues]!

[issues]: https://github.com/mozilla/mozilla-badges/issues

Development
-----------

Here's how I get it running on my MacBook:

    git clone --recursive git@github.com:mozilla/mozilla-badges.git
    [mkvirtualenv][virtualenvwrapper] mozilla-badges
    workon mozilla-badges
    pip install -r requirements/compiled.txt
    pip install -r requirements/dev.txt
    cd mozilla-badges
    cp badgus/settings/local.py-dist badgus/settings/local.py
    # Set up mysql database
    # Edit badgus/settings/local.py
    pip install python-memcached
    pip install python-six
    ./manage.py syncdb
    ./manage.py migrate
    ./manage.py runserver 127.0.0.1:8000

[virtualenvwrapper]: http://virtualenvwrapper.readthedocs.org/

License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/
