# browserexport

[![PyPi version](https://img.shields.io/pypi/v/browserexport.svg)](https://pypi.python.org/pypi/browserexport) [![Python 3.6|3.7|3.8|3.9](https://img.shields.io/pypi/pyversions/browserexport.svg)](https://pypi.python.org/pypi/browserexport) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

This:

- locates and backs up browser history by copying the underlying database files to some directory you specify
- can identify and parse the resulting sqlite files into some common schema

This doesn't aim to offer a way to 'restore' your history (see [#16](https://github.com/seanbreckenridge/browserexport/issues/16) for discussion), it just denormalizes and merges your history from backed up databases so its all available under some common format:

```
Visit:
  url: the url
  dt: datetime (when you went to this page)
  metadata:
    title: the <title> for this page
    description: the <meta description> tag from this page
    preview_image: 'main image' for this page, often opengraph/favicon
    duration: how long you were on this page
```

`metadata` is dependent on the data available in the browser (e.g. firefox has preview images, chrome has duration, but not vice versa)

This currently supports:

- Firefox (and Waterfox)
- Chrome (and Chromium, Brave, Vivaldi)
- Safari
- Palemoon

This might be able to extract visits from other Firefox/Chromium-based databases, but it doesn't know how to locate them to `save` them

## Install

`python3 -m pip install --user browserexport`

Requires `python3.6+`

## Usage

### `save`

```
Usage: browserexport save [OPTIONS]

  Backs up a current browser database file

Options:
  -b, --browser [chrome|firefox|safari|brave|waterfox|palemoon|chromium|vivaldi]
                                  Provide browser to backup, or specify
                                  directly with --path  [required]

  -p, --profile TEXT              Use to pick the correct profile to back up.
                                  If unspecified, will assume a single profile

  --path PATH                     Specify a direct path to a database to back
                                  up

  -t, --to PATH                   Directory to store backup to
  --help                          Show this message and exit.
```

Since browsers in typically remove old history over time, I'd recommend backing up your history periodically, like:

```shell
$ browserexport save -b firefox --to ~/data/browser_history
$ browserexport save -b chrome --to ~/data/browser_history
$ browserexport save -b safari --to ~/data/browser_history
```

That copies the sqlite databases which contains your history `--to` some backup directory.

If a browser you want to backup is Firefox/Chrome-like (so this would be able to parse it), but this doesn't support locating it yet, you can directly back it up with the `--path` flag:

```shell
$ browserexport save -b chromium --path ~/.somebrowser/profile/places.sqlite \
  --to ~/data/browser_history
```

Feel free to create an issue/contribute a [browser](./browserexport/browsers/) file to locate the browser if this doesn't support some browser you use.

### `inspect`/`merge`

```
Usage: browserexport inspect [OPTIONS] SQLITE_DB

  Extracts visits from a single sqlite database

  Provide a history database as the first argument
  Drops you into a REPL to access the data

Options:
  -s, --stream  Stream JSON objects instead of printing a JSON list
  -j, --json    Print result to STDOUT as JSON
  --help        Show this message and exit.
```

```
Usage: browserexport merge [OPTIONS] SQLITE_DB...

  Extracts visits from multiple sqlite databases

  Provide multiple sqlite databases as positional arguments, e.g.:
  browserexport merge ~/data/firefox/*.sqlite

  Drops you into a REPL to access the data

Options:
  -s, --stream  Stream JSON objects instead of printing a JSON list
  -j, --json    Print result to STDOUT as JSON
  --help        Show this message and exit.
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

Or, to create a quick searchable interface, using [`jq`](https://github.com/stedolan/jq) and [`fzf`](https://github.com/junegunn/fzf):

`browserexport merge -j --stream ~/data/browsing/*.sqlite | jq '"\(.url)|\(.metadata.description)"' | awk '!seen[$0]++' | fzf`

## Library Usage

To save databases:

```python
from browserexport.save import backup_history
backup_history("firefox", "~/data/backups")
```

To merge/read visits from databases:

```python
from browserexport.merge import read_and_merge
read_and_merge(["/path/to/database", "/path/to/second/database", "..."])
```

If this doesn't support a browser and you wish to quickly extend without maintaining a fork (or contributing back to this repo), you can pass a `Browser` implementation (see [browsers/all.py](./browserexport/browsers/all.py) and [browsers/common.py](./browserexport/browsers/common.py) for more info) to `browserexport.parse.read_visits` or programatically override/add your own browsers as part of the `browserexport.browsers` namespace package.

#### Comparisons with Promnesia

A lot of the initial queries/ideas here were taken from [promnesia](https://github.com/karlicoss/promnesia) and the [`browser_history.py`](https://github.com/karlicoss/promnesia/blob/0e1e9a1ccd1f07b2a64336c18c7f41ca24fcbcd4/scripts/browser_history.py) script, but creating a package here allows its to be more extendible, e.g. allowing you to override/locate additional databases.

The primary goals of promnesia and this are quite different -- this is tiny subset of that project -- it replaces the [`sources/browser.py`](https://github.com/karlicoss/promnesia/blob/master/src/promnesia/sources/browser.py) file with a package instead, while promnesia is an entire system to load data sources and use a browser extension to search/interface with your past data.

Eventually this project may be used in promnesia to replace the `browser.py` file

### Testing

```bash
git clone https://github.com/seanbreckenridge/browserexport
cd ./browserexport
pip install '.[testing]'
mypy ./browserexport
pytest
```
