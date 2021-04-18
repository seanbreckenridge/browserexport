# browserexport

[![PyPi version](https://img.shields.io/pypi/v/browserexport.svg)](https://pypi.python.org/pypi/browserexport) [![Python 3.6|3.7|3.8|3.9](https://img.shields.io/pypi/pyversions/browserexport.svg)](https://pypi.python.org/pypi/browserexport) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

Previously [ffexport](https://pypi.org/project/ffexport/) (which just supported Firefox)

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

Logs are hidden by default. To show the debug logs set `export BROWSEREXPORT_LOGS=10` (uses [logging levels](https://docs.python.org/3/library/logging.html#logging-levels)) or pass the `--debug` flag.

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

This has recently been restructured, so this interface for this may change in future versions;

To save databases:

```python
from ffexport.save import backup_history
backup_history("firefox", "~/data/backups")
```

To merge/read visits from databases:

```python
from ffexport.merge import read_and_merge
read_and_merge(["/path/to/database", "/path/to/second/database", "..."])
```

If this doesn't support a browser and you wish to quickly extend without maintaining a fork (or contributing back to this repo), you can pass a `Browser` implementation (see [browsers/all.py](./browserexport/browsers/all.py) and [browsers/common.py](browserexport/browsers/common.py) for more info) to `browserexport.parse.read_visits` or programatically override/add your own browsers as part of the `browserexport.browsers` namespace package.

#### Comparisons with Promnesia

A lot of the initial queries/ideas here were taken from [promnesia](https://github.com/karlicoss/promnesia) and the [`browser_history.py`](https://github.com/karlicoss/promnesia/blob/0e1e9a1ccd1f07b2a64336c18c7f41ca24fcbcd4/scripts/browser_history.py) script, but creating a package here allows its to be more extendible, e.g. allowing you to locating additional databases.

The primary goals of promnesia and this are quite different -- this is tiny subset of that project -- it replaces the [`sources/browser.py`](https://github.com/karlicoss/promnesia/blob/master/src/promnesia/sources/browser.py) file with a package instead, while promnesia is an entire system to load data sources and uses the browser extension to search/interface with your past data.

Eventually this project may be used in promnesia to replace the `browser.py` file

### Testing

```bash
git clone https://github.com/seanbreckenridge/browserexport
cd ./browserexport
pip install '.[testing]'
mypy ./browserexport
pytest
```
