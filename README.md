# browserexport

[![PyPi version](https://img.shields.io/pypi/v/browserexport.svg)](https://pypi.python.org/pypi/browserexport) [![Python 3.8|3.9|3.10|3.11](https://img.shields.io/pypi/pyversions/browserexport.svg)](https://pypi.python.org/pypi/browserexport) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

- [Supported Browsers](#supported-browsers)
- [Install](#install)
- [Usage](#usage)
  - [`save`](#save)
  - [`inspect`/`merge`](#inspectmerge)
- [Serializing to JSON](#json)
- [Shell Completion](#shell-completion)
- [Usage with HPI](#hpi)
- [Library Usage](#library-usage)
- [Comparisons with promnesia](#comparisons-with-promnesia)
- [Contributing](#contributing)
  - [Development](#development)
  - [Testing](#testing)

This:

- locates and backs up browser history by copying the underlying database files to some directory you specify
- can identify and parse the resulting database files into some common schema:

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

## Supported Browsers

This currently supports:

- [Firefox](https://www.mozilla.org/en-US/firefox/new/)
  - [Waterfox](https://www.waterfox.net/)
  - [Floorp](https://floorp.app/)
  - [Librewolf](https://librewolf.net/)
  - Firefox Android (pre-2020 schema and current [Fenix](https://github.com/mozilla-mobile/fenix))
- [Chrome](https://www.google.com/chrome/)
  - [Chromium](https://www.chromium.org/chromium-projects/)
  - [Brave](https://brave.com/)
  - [Vivaldi](https://vivaldi.com/)
  - [Opera](https://www.opera.com/)
  - [Arc](https://arc.net/)
  - [Edge](https://www.microsoft.com/edge) (and [Dev Channel](https://www.microsoft.com/edge/download/insider))
- [Safari](https://www.apple.com/safari/)
- [Palemoon](https://www.palemoon.org/)

This can probably extract visits from other Firefox/Chromium-based browsers, but it doesn't know how to locate them to `save` them

## Install

`python3 -m pip install --user browserexport`

Requires `python3.7+`

## Usage

### `save`

```
Usage: browserexport save [OPTIONS]

  Backs up a current browser database file

Options:
  -b, --browser
      [chrome | firefox | opera | safari | brave | waterfox |
      librewolf | floorp | chromium | vivaldi | palemoon | arc |
      edge | edgedev]
                                  Browser name to backup history for
  --pattern TEXT                  Pattern for the resulting timestamped filename, should include an
                                  str.format replacement placeholder for the date [default:
                                  browser_name-{}.extension]
  -p, --profile TEXT              Use to pick the correct profile to back up. If unspecified, will assume a
                                  single profile  [default: *]
  --path FILE                     Specify a direct path to a database to back up
  -t, --to DIRECTORY              Directory to store backup to. Pass '-' to print database to STDOUT
                                  [required]
  -h, --help                      Show this message and exit.
```

Must specify one of `--browser`, or `--path`

After your browser history reaches a certain size, browsers typically remove old history over time, so I'd recommend backing up your history periodically, like:

```shell
$ browserexport save -b firefox --to ~/data/browsing
$ browserexport save -b chrome --to ~/data/browsing
$ browserexport save -b safari --to ~/data/browsing
```

That copies the sqlite databases which contains your history `--to` some backup directory.

If a browser you want to backup is Firefox/Chrome-like (so this would be able to parse it), but this doesn't support locating it yet, you can directly back it up with the `--path` flag:

```shell
$ browserexport save --path ~/.somebrowser/profile/places.sqlite \
  --to ~/data/browsing
```

The `--pattern` argument can be used to change the resulting filename for the browser, e.g. `--pattern 'places-{}.sqlite'` or `--pattern "$(uname)-{}.sqlite"`. The `{}` is replaced by the browser name.

Feel free to create an issue/contribute a [browser](./browserexport/browsers/) file to locate the browser if this doesn't support some browser you use.

Can pass the `--debug` flag to show [`sqlite_backup`](https://github.com/seanbreckenridge/sqlite_backup) logs

```
$ browserexport --debug save -b firefox --to .
[D 220202 10:10:22 common:87] Glob /home/sean/.mozilla/firefox with */places.sqlite (non recursive) matched [PosixPath('/home/sean/.mozilla/firefox/ew9cqpqe.dev-edition-default/places.sqlite')]
[I 220202 10:10:22 save:18] backing up /home/sean/.mozilla/firefox/ew9cqpqe.dev-edition-default/places.sqlite to /home/sean/Repos/browserexport/firefox-20220202181022.sqlite
[D 220202 10:10:22 core:110] Source database files: '['/tmp/tmpcn6gpj1v/places.sqlite', '/tmp/tmpcn6gpj1v/places.sqlite-wal']'
[D 220202 10:10:22 core:111] Temporary Destination database files: '['/tmp/tmpcn6gpj1v/places.sqlite', '/tmp/tmpcn6gpj1v/places.sqlite-wal']'
[D 220202 10:10:22 core:64] Copied from '/home/sean/.mozilla/firefox/ew9cqpqe.dev-edition-default/places.sqlite' to '/tmp/tmpcn6gpj1v/places.sqlite' successfully; copied without file changing: True
[D 220202 10:10:22 core:64] Copied from '/home/sean/.mozilla/firefox/ew9cqpqe.dev-edition-default/places.sqlite-wal' to '/tmp/tmpcn6gpj1v/places.sqlite-wal' successfully; copied without file changing: True
[D 220202 10:10:22 core:230] Running backup, from '/tmp/tmpcn6gpj1v/places.sqlite' to '/home/sean/Repos/browserexport/firefox-20220202181022.sqlite'
[D 220202 10:10:22 save:14] Copied 1840 of 1840 database pages...
[D 220202 10:10:22 core:246] Executing 'wal_checkpoint(TRUNCATE)' on destination '/home/sean/Repos/browserexport/firefox-20220202181022.sqlite'
```

For Firefox Android [Fenix](https://github.com/mozilla-mobile/fenix/), the database has to be manually backed up (probably from a rooted phone using [`termux`](https://termux.dev/en/)) from `data/data/org.mozilla.fenix/files/places.sqlite`.

### `inspect`/`merge`

These work very similarly, `inspect` is for a single database, `merge` is for multiple databases.

```
Usage: browserexport merge [OPTIONS] SQLITE_DB...

  Extracts visits from multiple sqlite databases

  Provide multiple sqlite databases as positional arguments, e.g.:
  browserexport merge ~/data/firefox/*.sqlite

  Drops you into a REPL to access the data

  Pass '-' to read from STDIN

Options:
  -s, --stream  Stream JSON objects instead of printing a JSON list
  -j, --json    Print result to STDOUT as JSON
  -h, --help    Show this message and exit.
```

As an example:

```
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

You can also read from STDIN, so this can be used in conjunction with `save`, to merge databases you've backed up and combine your current browser history:

```bash
browserexport save -b firefox -t - | browserexport merge --json --stream - ~/data/browsing/* >all.jsonl
```

Or, to just print the demo for your current browser history:

```bash
$ browserexport save -b firefox -t - | browserexport inspect -
Demo: Your most common sites....
 [('github.com', 21033),
  ...
```

Or, use [process substitution](https://tldp.org/LDP/abs/html/process-sub.html) to save multiple dbs in parallel and then merge them:

```bash
$ browserexport merge <(browserexport save -b firefox -t -) <(browserexport save -b chrome -t -)
```

Logs are hidden by default. To show the debug logs set `export BROWSEREXPORT_LOGS=10` (uses [logging levels](https://docs.python.org/3/library/logging.html#logging-levels)) or pass the `--debug` flag.

### JSON

To dump all that info to JSON:

```bash
$ browserexport merge --json ~/data/browsing/*.sqlite > ./history.json
du -h history.json
67M     history.json
```

Or, to create a quick searchable interface, using [`jq`](https://github.com/stedolan/jq) and [`fzf`](https://github.com/junegunn/fzf):

`browserexport merge -j --stream ~/data/browsing/*.sqlite | jq '"\(.url)|\(.metadata.description)"' | awk '!seen[$0]++' | fzf`

Merged files like `history.json` can also be used as inputs files themselves, this reads those by mapping the JSON onto the `Visit` schema directly.

In addition to `.json` files, this can parse `.jsonl` ([JSON lines](http://jsonlines.org/)) files, which are files which contain newline delimited JSON objects. This allows you to parse JSON objects one at a time, instead of loading the entire file into memory. The `.jsonl` file can be generated with the `--stream` flag:

```
browserexport merge --stream --json ~/data/browsing/*.sqlite > ./history.jsonl
```

_Additionally_, this can parse gzipped versions of those files - files like `history.json.gz` or `history.jsonl.gz`

If you don't care about keeping the raw databases for any other auxiliary info like form, bookmark data, or [from_visit](https://github.com/seanbreckenridge/browserexport/issues/30) info and just want the URL, visit date and metadata, you could use `merge` to periodically merge the bulky `.sqlite` files into a gzipped JSONL dump:

```bash
# backup databases
rsync -Pavh ~/data/browsing ~/.cache/browsing
# merge all sqlite databases into a single compressed, jsonl file
browserexport --debug merge --json --stream ~/data/browsing/* > '/tmp/browsing.jsonl'
gzip '/tmp/browsing.jsonl'
# test reading gzipped file
browserexport --debug inspect '/tmp/browsing.jsonl.gz'
# remove all old datafiles
rm ~/data/browsing/*
# move merged data to database directory
mv /tmp/browsing.jsonl.gz ~/data/browsing
```

I do this every couple months with a script [here](https://github.com/seanbreckenridge/bleanser/blob/master/bin/merge-browser-history), and then sync my old databases to a harddrive for more long-term storage

## Shell Completion

This uses `click`, which supports [shell completion](https://click.palletsprojects.com/en/8.1.x/options/) for `bash`, `zsh` and `fish`. To generate the completion on startup, put one of the following in your shell init file (`.bashrc`/`.zshrc` etc)

```bash
eval "$(_BROWSEREXPORT_COMPLETE=bash_source browserexport)" # bash
eval "$(_BROWSEREXPORT_COMPLETE=zsh_source browserexport)" # zsh
_BROWSEREXPORT_COMPLETE=fish_source browserexport | source  # fish
```

Instead of `eval`ing, you could of course save the generated completion to a file and/or lazy load it in your shell config, see [bash completion docs](https://github.com/scop/bash-completion/blob/master/README.md#faq), [zsh functions](https://zsh.sourceforge.io/Doc/Release/Functions.html), [fish completion docs](https://fishshell.com/docs/current/completions.html). For example for `zsh` that might look like:

```bash
mkdir -p ~/.config/zsh/functions/
_BROWSEREXPORT_COMPLETE=zsh_source browserexport > ~/.config/zsh/functions/_browserexport
```

```bash
# in your ~/.zshrc
# update fpath to include the directory you saved the completion file to
fpath=(~/.config/zsh/functions $fpath)
autoload -Uz compinit && compinit
```

## HPI

If you want to cache the merged results, this has a [module in HPI](https://github.com/karlicoss/HPI) which handles locating/caching and querying the results. See [setup](https://github.com/karlicoss/HPI/blob/master/doc/SETUP.org#install-main-hpi-package) and [module setup](https://github.com/karlicoss/HPI/blob/master/doc/MODULES.org#mybrowser).

That uses [cachew](https://github.com/karlicoss/cachew) to automatically cache the merged results, recomputing whenever you backup new databases

As a few examples:

```sh
✅ OK  : my.browser.all
✅     - stats: {'history': {'count': 1091091, 'last': datetime.datetime(2023, 2, 11, 1, 12, 37, 302883, tzinfo=datetime.timezone.utc)}}
✅ OK  : my.browser.export
✅     - stats: {'history': {'count': 1090850, 'last': datetime.datetime(2023, 2, 11, 4, 34, 12, 985488, tzinfo=datetime.timezone.utc)}}
✅ OK  : my.browser.active_browser
✅     - stats: {'history': {'count': 270363, 'last': datetime.datetime(2023, 2, 11, 22, 26, 24, 887722, tzinfo=datetime.timezone.utc)}}
```

```sh
# supports arbitrary queries, e.g. how many visits did I have in January 2020?
$ hpi query my.browser.all --order-type datetime --after '2022-01-01 00:00:00' --before '2022-01-31 23:59:59' | jq length
50432
# how many github URLs in the past month
$ hpi query my.browser.all --recent 4w -s | jq .url | grep 'github.com' -c
16357
```

## Library Usage

To save databases:

```python
from browserexport.save import backup_history
backup_history("firefox", "~/data/backups")
# or, pass a Browser implementation
from browserexport.browsers.all import Firefox
backup_history(Firefox, "~/data/backups")
```

To merge/read visits from databases:

```python
from browserexport.merge import read_and_merge
read_and_merge(["/path/to/database", "/path/to/second/database", "..."])
```

You can also use [`sqlite_backup`](https://github.com/seanbreckenridge/sqlite_backup) to copy your current browser history into a sqlite connection in memory, as a `sqlite3.Connection`

```python
from browserexport.browsers.all import Firefox
from browserexport.parse import read_visits
from sqlite_backup import sqlite_backup

db_in_memory = sqlite_backup(Firefox.locate_database())
visits = list(read_visits(db_in_memory))

# to merge those with other saved files
from browserexport.merge import merge_visits, read_and_merge
merged = list(merge_visits([
    visits,
    read_and_merge(["/path/to/another/database.sqlite", "..."]),
]))
```

If this doesn't support a browser and you wish to quickly extend without maintaining a fork (or contributing back to this repo), you can pass a `Browser` implementation (see [browsers/all.py](./browserexport/browsers/all.py) and [browsers/common.py](./browserexport/browsers/common.py) for more info) to `browserexport.parse.read_visits` or programatically override/add your own browsers as part of the [`browserexport.browsers` namespace package](https://github.com/seanbreckenridge/browserexport/blob/0705629e1dc87fe47d6f731018d26dc3720cf2fe/browserexport/browsers/all.py#L15-L24)

#### Comparisons with Promnesia

A lot of the initial queries/ideas here were taken from [promnesia](https://github.com/karlicoss/promnesia) and the [`browser_history.py`](https://github.com/karlicoss/promnesia/blob/0e1e9a1ccd1f07b2a64336c18c7f41ca24fcbcd4/scripts/browser_history.py) script, but creating a package here allows its to be more extendible, e.g. allowing you to override/locate additional databases.

TLDR on promnesia: lets you explore your browsing history in context: where you encountered it, in chat, on Twitter, on Reddit, or just in one of the text files on your computer. This is unlike most modern browsers, where you can only see when you visited the link.

Since [promnesia #375](https://github.com/karlicoss/promnesia/pull/375), `browserexport` is used in [promnesia](https://github.com/karlicoss/promnesia) in the `browser.py` file (to read any of the supported databases here from disk), see [setup](https://github.com/karlicoss/promnesia#setup) and [the browser source quickstart](https://github.com/karlicoss/promnesia/blob/master/doc/SOURCES.org#browser) in the instructions for more

## Contributing

Clone the repository and [optionally] create a [virtual environment](https://docs.python.org/3/library/venv.html) to do your work in.

```bash
git clone https://github.com/seanbreckenridge/browserexport
cd ./browserexport
# create a virtual environment to prevent possible package dependency conflicts
python -m venv .venv
source .venv/bin/activate
```

### Development

To install, run:

```bash
python3 -m pip install '.[testing]'
```

If running in a virtual environment, `pip` will automatically install dependencies into your virtual environment. If running `browserexport` happens to use the globally installed `browserexport` instead, you can use `python3 -m browserexport` to ensure its using the version in your virtual environment.

After making changes to the code, reinstall by running `pip install .`, and then test with `browserexport` or `python3 -m browserexport`

### Testing

While developing, you can run tests with:

```bash
pytest
flake8 ./browserexport
mypy ./browserexport
# to autoformat code
python3 -m pip install black
find browserexport tests -name '*.py' -exec python3 -m black {} +
```
