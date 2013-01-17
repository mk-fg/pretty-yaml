pretty-yaml: Pretty YAML serialization
--------------------

YAML is generally nice an easy format to read *if* it was written by humans.

Unfortunately, by default, available serializers seem to not care about that
aspect, producing correct but less-readable (and format allows for json-style
crap) and poorly-formatted dumps, hence this simple module.

Observe.

- - -

Let's try default PyYAML methods first.

yaml.dump(src, sys.stdout):

    destination:
      encoding:
        xz: {enabled: true, min_size: 5120, options: null, path_filter: null}
      result: {append_to_file: null, append_to_lafs_dir: null, print_to_stdout: true}
      url: http://localhost:3456/uri
    filter: ["\u0414\u043B\u0438\u043D\u043D\u044B\u0439 \u0441\u0442\u0440\u0438\u043D\
        \u0433 \u043D\u0430 \u0440\u0443\u0441\u0441\u043A\u043E\u043C", "\u0415\u0449\
        \u0435 \u043E\u0434\u043D\u0430 \u0434\u043B\u0438\u043D\u043D\u0430\u044F \u0441\
        \u0442\u0440\u043E\u043A\u0430"]

Quite similar to JSON (a subset of YAML, actually).

yaml.dump(src, sys.stdout, default_flow_style=False):

    destination:
      encoding:
        xz:
          enabled: true
          min_size: 5120
          options: null
          path_filter: null
      result:
        append_to_file: null
        append_to_lafs_dir: null
        print_to_stdout: true
      url: http://localhost:3456/uri
    filter:
    - "\u0414\u043B\u0438\u043D\u043D\u044B\u0439 \u0441\u0442\u0440\u0438\u043D\u0433\
      \ \u043D\u0430 \u0440\u0443\u0441\u0441\u043A\u043E\u043C"
    - "\u0415\u0449\u0435 \u043E\u0434\u043D\u0430 \u0434\u043B\u0438\u043D\u043D\u0430\
      \u044F \u0441\u0442\u0440\u043E\u043A\u0430"

Better, but why all the "null" stuff if yaml allows to have just empty values?
Why make all non-ascii strings completely unreadable like that if pretty much
every parser reads utf-8 or whatever unicode-string object by default?

pyaml.dump(src, sys.stdout):

    destination:
      encoding:
        xz:
          enabled: true
          min_size: 5120
          options:
          path_filter:
      result:
        append_to_file:
        append_to_lafs_dir:
        print_to_stdout: true
      url: http://localhost:3456/uri
    filter:
      - 'Длинный стринг на русском'
      - 'Еще одна длинная строка'

Note, yaml.load will read that to the same thing as the above dumps, but now you
can read that as well.

- - -

Another example.

Let's say you have a parsed URL like this:

    url = dict(
      path='/some/path',
      query_dump=OrderedDict([
        ('key1', 'value1'),
        ('key2', 'value2'),
        ('key3', 'value3') ]) )

Order of keys in query matters because there might be a hundred of them and
you'd like the output to be diff-friendly.

yaml.dump(url, sys.stdout):

    path: !!python/unicode '/some/path'
    query_dump: !!python/object/apply:collections.OrderedDict
    - - [!!python/unicode 'key1', "\u0442\u0435\u0441\u04421"]
      - [!!python/unicode 'key2', "\u0442\u0435\u0441\u04422"]
      - [!!python/unicode 'key3', "\u0442\u0435\u0441\u04423"]
      - ["\u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0439", null]

Ugh...

yaml.safe_dump(url, sys.stdout):

    yaml.representer.RepresenterError: cannot represent an object: OrderedDict(...

Right... let's try something *designed* to be pretty here:

    >>> from pprint import pprint
    >>> pprint(url)
    {'path': u'/some/path',
     'query_dump': OrderedDict([(u'key1', u'\u0442\u0435\u0441\u04421'), (u'key2', u'\u0442\u0435\u0441\u04422'), (u'key3', u'\u0442\u0435\u0441\u04423'), (u'\u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439', None)])}

YUCK!

pyaml.dump(url, sys.stdout):

    path: /some/path
    query_dump:
      key1: тест1
      key2: тест2
      key3: тест3
      последний:

Much easier to read than... anything else! Diff-friendly.

- - -

Have a long config which will produce a wall-of-text even with indentation? No problem!

pyaml.dump(src, sys.stdout, vspacing=[2, 1]):

    destination:

      encoding:
        xz:
          enabled: true
          min_size: 5120
          options:
          path_filter:
            - \.(gz|bz2|t[gb]z2?|xz|lzma|7z|zip|rar)$
            - \.(rpm|deb|iso)$
            - \.(jpe?g|gif|png|mov|avi|ogg|mkv|webm|mp[34g]|flv|flac|ape|pdf|djvu)$
            - \.(sqlite3?|fossil|fsl)$
            - \.git/objects/[0-9a-f]+/[0-9a-f]+$

      result:
        append_to_file:
        append_to_lafs_dir:
        print_to_stdout: true

      url: http://localhost:3456/uri


    filter:
      - /(CVS|RCS|SCCS|_darcs|\{arch\})/$
      - /\.(git|hg|bzr|svn|cvs)(/|ignore|attributes|tags)?$
      - /=(RELEASE-ID|meta-update|update)$


    http:

      ca_certs_files: /etc/ssl/certs/ca-certificates.crt

      debug_requests: false

      request_pool_options:
        cachedConnectionTimeout: 600
        maxPersistentPerHost: 10
        retryAutomatically: true


    logging:

      formatters:
        basic:
          datefmt: '%Y-%m-%d %H:%M:%S'
          format: '%(asctime)s :: %(name)s :: %(levelname)s: %(message)s'

      handlers:
        console:
          class: logging.StreamHandler
          formatter: basic
          level: custom
          stream: ext://sys.stderr

      loggers:
        twisted:
          handlers:
            - console
          level: 0

      root:
        handlers:
          - console
        level: custom

- - -

Hopefully, the *why* should be obvious now.

Among other features - proper readable (and working) object deduplication links
by the grace of [unidecode](http://pypi.python.org/pypi/Unidecode) module
transliteration and an option ("force_embed" keyword) to disable deduplication
(imagine reading through dump riddled with such "jump there" links - none of
that!).


### Obligatory warning

Note that prime concern for this module is to chew *simple* stuff gracefully,
and internally, there are some nasty hacks (I'm quite ashamed of) are used to do
that, which may not work with more complex serialization cases, possibly even
producing non-deserializable output.

Again, prime goal is not to serialize, say, gigabytes of complex
document-storage db, but rather individual simple human-parseable documents,
please keep that in mind (and of course, patches for hacks are welcome!).



Installation
--------------------

It's a regular package for Python 2.7 (not 3.X).

Using [pip](http://pip-installer.org/) is the best way:

	% pip install pyaml

If you don't have it, use:

	% easy_install pip
	% pip install pyaml

Alternatively ([see
also](http://www.pip-installer.org/en/latest/installing.html)):

	% curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
	% pip install pyaml

Or, if you absolutely must:

	% easy_install pyaml

But, you really shouldn't do that.

Current-git version can be installed like this:

	% pip install 'git+https://github.com/mk-fg/pretty-yaml.git#egg=pyaml'

Module uses [PyYAML](http://pyyaml.org/) for processing of the actual YAML files
and should pull it in as a dependency.

Dependency on [unidecode](http://pypi.python.org/pypi/Unidecode) module is
optional and should only be necessary if same-id objects or recursion is used
within serialized data.
