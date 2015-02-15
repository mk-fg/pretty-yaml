pretty-yaml: Pretty YAML serialization
--------------------

YAML is generally nice an easy format to read *if* it was written by humans.

**IMPORTANT NOTE:** I just discovered allow_unicode=True option for Emitter
(shameful, I know). It fixes *a lot* of issues with non-ascii stuff, maybe
consider trying just that one first.

Unfortunately, by default, available serializers seem to not care about that
aspect, producing correct but less-readable (and format allows for json-style
crap) and poorly-formatted dumps, hence this simple module.

Observe...

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

`pyaml.pprint(data)` (or just `pyaml.p`) should work just as well as
`pyaml.dump(src, sys.stdout)` (and there's `pyaml.dumps()` to get bytes).

- - -

Multi-line X.509 data?

yaml.dump(cert, sys.stdout):

    {cert: !!python/unicode '-----BEGIN CERTIFICATE-----

        MIIDUjCCAjoCCQD0/aLLkLY/QDANBgkqhkiG9w0BAQUFADBqMRAwDgYDVQQKFAdm

        Z19jb3JlMRYwFAYDVQQHEw1ZZWthdGVyaW5idXJnMR0wGwYDVQQIExRTdmVyZGxv

        ...

Beautiful, is it not? (it is not)

pyaml.p(cert):

    cert: |-
      -----BEGIN CERTIFICATE-----
      MIIDUjCCAjoCCQD0/aLLkLY/QDANBgkqhkiG9w0BAQUFADBqMRAwDgYDVQQKFAdm
      Z19jb3JlMRYwFAYDVQQHEw1ZZWthdGVyaW5idXJnMR0wGwYDVQQIExRTdmVyZGxv
      dnNrYXlhIG9ibGFzdDELMAkGA1UEBhMCUlUxEjAQBgNVBAMTCWxvY2FsaG9zdDAg
      Fw0xMzA0MjQwODUxMTRaGA8yMDUzMDQxNDA4NTExNFowajEQMA4GA1UEChQHZmdf
      Y29yZTEWMBQGA1UEBxMNWWVrYXRlcmluYnVyZzEdMBsGA1UECBMUU3ZlcmRsb3Zz
      a2F5YSBvYmxhc3QxCzAJBgNVBAYTAlJVMRIwEAYDVQQDEwlsb2NhbGhvc3QwggEi
      MA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCnZr3jbhfb5bUhORhmXOXOml8N
      fAli/ak6Yv+LRBtmOjke2gFybPZFuXYr0lYGQ4KgarN904vEg7WUbSlwwJuszJxQ
      Lz3xSDqQDqF74m1XeBYywZQIywKIbA/rfop3qiMeDWo3WavYp2kaxW28Xd/ZcsTd
      bN/eRo+Ft1bor1VPiQbkQKaOOi6K8M9a/2TK1ei2MceNbw6YrlCZe09l61RajCiz
      y5eZc96/1j436wynmqJn46hzc1gC3APjrkuYrvUNKORp8y//ye+6TX1mVbYW+M5n
      CZsIjjm9URUXf4wsacNlCHln1nwBxUe6D4e2Hxh2Oc0cocrAipxuNAa8Afn5AgMB
      AAEwDQYJKoZIhvcNAQEFBQADggEBADUHf1UXsiKCOYam9u3c0GRjg4V0TKkIeZWc
      uN59JWnpa/6RBJbykiZh8AMwdTonu02g95+13g44kjlUnK3WG5vGeUTrGv+6cnAf
      4B4XwnWTHADQxbdRLja/YXqTkZrXkd7W3Ipxdi0bDCOSi/BXSmiblyWdbNU4cHF/
      Ex4dTWeGFiTWY2upX8sa+1PuZjk/Ry+RPMLzuamvzP20mVXmKtEIfQTzz4b8+Pom
      T1gqPkNEbe2j1DciRNUOH1iuY+cL/b7JqZvvdQK34w3t9Cz7GtMWKo+g+ZRdh3+q
      2sn5m3EkrUb1hSKQbMWTbnaG4C/F3i4KVkH+8AZmR9OvOmZ+7Lo=
      -----END CERTIFICATE-----

Seem to be somewhat nicer.

Use e.g. `pyaml.dump(stuff, string_val_style='|')` to force all string values
(but not keys) to some particular style (see tricks section below for examples).

- - -

Another example.

Let's say you have a parsed URL like this:

    # -*- coding: utf-8 -*-
    url = dict(
      path='/some/path',
      query_dump=OrderedDict([
        ('key1', 'тест1'),
        ('key2', 'тест2'),
        ('key3', 'тест3'),
        ('последний', None) ]) )

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

pyaml.pprint(url):

    path: /some/path
    query_dump:
      key1: тест1
      key2: тест2
      key3: тест3
      последний:

Much easier to read than... anything else! Diff-friendly too.

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
and internally there are some nasty hacks (that I'm not proud of) are used to do
it, which may not work with more complex serialization cases, possibly even
producing non-deserializable (but fixable) output.

Again, prime goal is **not** to serialize, say, gigabytes of complex
document-storage db contents, but rather individual simple human-parseable
documents, please keep that in mind (and of course, patches for hacks are
welcome!).


Other Tricks
--------------------

Pretty-print any yaml or json (yaml subset) file from the shell:

    python -m pyaml /path/to/some/file.yaml
    curl -s https://status.github.com/api.json | python -m pyaml

Easier "debug printf" for more complex data (all funcs below are aliases to same thing):

    pyaml.p(stuff)
    pyaml.pprint(my_data)
    pyaml.pprint('----- HOW DOES THAT BREAKS!?!?', input_data, some_var, more_stuff)
    pyaml.print(data, file=sys.stderr) # needs "from __future__ import print_function"

Force all string values to a certain style (see info on these in
[PyYAML docs](http://pyyaml.org/wiki/PyYAMLDocumentation#Scalars)):

    pyaml.dump(many_weird_strings, string_val_style='|')
    pyaml.dump(multiline_words, string_val_style='>')
    pyaml.dump(no_want_quotes, string_val_style='plain')

Using `pyaml.add_representer()` (note *p*yaml) as suggested
in [this SO thread](http://stackoverflow.com/a/7445560)
(or [#7](https://github.com/mk-fg/pretty-yaml/issues/7))
should also work.



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
