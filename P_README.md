# browserexport

[![PyPi version](https://img.shields.io/pypi/v/browserexport.svg)](https://pypi.python.org/pypi/browserexport) [![Python 3.6|3.7|3.8|3.9](https://img.shields.io/pypi/pyversions/browserexport.svg)](https://pypi.python.org/pypi/browserexport) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

This:
  - locates and backs up browser history by copying the underlying database files to some directory you specify
  - can identify and parse the resulting sqlite files into some common schema

This doesn't aim to offer a way to 'restore' your history, it just denormalizes and merges your history from backed up databases so its all available under some common format:

```
Visit:
  url: the url
  dt: datetime (when you went to this page)
  metadata:
    title: the stored <title> for this page
    description: description <meta description> tag, if stored
    preview_image: 'main image' for this page, often opengraph/favicon
    duration: how long you were on this page
```

`metadata` is dependent on the data available in the browser (e.g. firefox has preview images, chrome has duration, but not vice versa)

This currently supports:

- Firefox (and Waterfox)
- Chrome (and Chromium, Brave)
- Safari
- Palemoon

This might be able to extract visits from other Firefox/Chrome-based databases, but it doesn't know how to locate them to `save` them

## Install

`pip3 install browserexport`

Requires `python3.6+`

## Usage

The `inspect` and `merge` commands also accept a `--json` flag, which dumps the result to STDOUT as JSON. Dates are serialized to epoch time

Logs are hidden by default. To show the debug logs set `export BROWSEREXPORT_LOGS=10` (uses [logging levels](https://docs.python.org/3/library/logging.html#logging-levels))

### `save`

```
>>>PMARK
perl -E 'print "`"x3, "\n"'
browserexport save --help
perl -E 'print "`"x3, "\n"'
```

Since browsers in general seem to remove old history seemingly randomly, I'd recommend backing up your history periodically, like:

```shell
$ browserexport save -b firefox --to ~/data/browser_history
$ browserexport save -b chrome --to ~/data/browser_history
$ browserexport save -b safari --to ~/data/browser_history
```

That copies the sqlite databases which contains your history `--to` some backup directory.

### `inspect`/`merge`

```
>>>PMARK
perl -E 'print "`"x3, "\n"'
browserexport inspect --help
perl -E 'print "`"x3, "\n"'
```

```
>>>PMARK
perl -E 'print "`"x3, "\n"'
browserexport merge --help
perl -E 'print "`"x3, "\n"'
```

As an example:

```bash
browserexport --debug merge ~/data/firefox/* ~/data/chrome/*
[D 210417 21:12:18 merge:38] merging information from 24 sources...
[D 210417 21:12:18 parse:19] Reading visits from /home/sean/data/firefox/places-20200828223058.sqlite...
[D 210417 21:12:18 common:40] Chrome: Running detector query 'SELECT * FROM keyword_search_terms'
[D 210417 21:12:18 common:40] Firefox: Running detector query 'SELECT * FROM moz_meta'
[D 210417 21:12:18 parse:22] Detected as Firefox
[D 210417 21:12:19 parse:19] Reading visits from /home/sean/data/firefox/places-20201010031025.sqlite...
[D 210417 21:12:19 common:40] Chrome: Running detector query 'SELECT * FROM keyword_search_terms'
....
[D 210417 21:12:48 common:40] Firefox: Running detector query 'SELECT * FROM moz_meta'
[D 210417 21:12:48 common:40] Safari: Running detector query 'SELECT * FROM history_tombstones'
[D 210417 21:12:48 parse:22] Detected as Safari
[D 210417 21:12:48 merge:51] Summary: removed 3001879 duplicates...
[D 210417 21:12:48 merge:52] Summary: returning 334490 visit entries...

Use vis to interact with the data

[1] ...
```

To dump all that info to JSON:

```
browserexport merge --json ~/data/browser_history/*.sqlite > ./history.json
du -h history.json
67M     history.json
```

## Library Usage

#### Comparisons with Promnesia

### Testing

```bash
git clone https://github.com/seanbreckenridge/browserexport
cd ./browserexport
pip install '.[testing]'
mypy ./browserexport
pytest
```
