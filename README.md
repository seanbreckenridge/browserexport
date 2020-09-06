# ffexport

[![PyPi version](https://img.shields.io/pypi/v/ffexport.svg)](https://pypi.python.org/pypi/ffexport) [![Python 3.7|3.8](https://img.shields.io/pypi/pyversions/ffexport.svg)](https://pypi.python.org/pypi/ffexport) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

This backs up my firefox history and parses the resulting history (sqlite) files.

Primary function here is to export/interact with my firefox history. Functionality for Chrome are vestigal and I've left them there in case someone wants to mess with it. I recommend you take a look at [`promnesia`](https://github.com/karlicoss/promnesia) if you want immediate support for that.

See [here](https://web.archive.org/web/20190730231715/https://www.forensicswiki.org/wiki/Mozilla_Firefox_3_History_File_Format#moz_historyvisits) for how firefox stores its history.


## Install

`pip3 install ffexport`

Requires `python3.7+`

## Usage

```
Usage: ffexport [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  inspect  Extracts history/site metadata from one sqlite database.
  merge    Extracts history/site metadata from multiple sqlite databases.
  save     Backs up the current firefox sqlite history file.
```

Logs are hidden by default. To show the debug logs set `export FFEXPORT_LOGS=5` (uses [logging levels](https://docs.python.org/3/library/logging.html#logging-levels))

### save

```
Usage: ffexport save [OPTIONS]

  Backs up the current firefox sqlite history file.

Options:
  --browser [firefox|chrome]  Provide either 'firefox' or 'chrome' [defaults
                              to firefox]
  --profile TEXT              Use to pick the correct profile to back up. If
                              unspecified, will assume a single profile
  --to PATH                   Directory to store backup to  [required]
```

Since firefox (and browsers in general) seem to remove old history seemingly randomly, I'd recommend running the following periodically:

```
$ ffexport save --to ~/data/firefox/dbs
[D 200828 15:30:58 save_hist:67] backing up /home/sean/.mozilla/firefox/jfkdfwx.dev-edition-default/places.sqlite to /home/sean/data/firefox/dbs/places-20200828223058.sqlite
[D 200828 15:30:58 save_hist:71] done!
```

That atomically copies the firefox sqlite database which contains your history `--to` some backup directory.

### inspect

```
Usage: ffexport inspect SQLITE_DB

  Extracts history/site metadata from one sqlite database. Provide a firefox
  history sqlite databases as the first argument. Drops you into a REPL to
  access the data.

```

As an example:

```
$ ffexport inspect ~/data/firefox/dbs/places-20200828231237.sqlite
[D 200828 17:08:23 parse_db:73] Parsing visits from /home/sean/data/firefox/dbs/places-20200828231237.sqlite...
[D 200828 17:08:23 parse_db:92] Parsing sitedata from /home/sean/data/firefox/dbs/places-20200828231237.sqlite...
Demo: Your most common sites....
[('github.com', 13778),
 ('www.youtube.com', 8114),
 ('duckduckgo.com', 8054),
 ('www.google.com', 6542),
 ('discord.com', 6141),
 ('stackoverflow.com', 2528),
 ('gitlab.com', 1608),
 ('trakt.tv', 1362),
 ('letterboxd.com', 1053),
 ('www.reddit.com', 708)]

Use mvis or msite to access raw visits/site data, vis for the merged data

In [1]: ....
```

That drops you into a REPL with access to the history from that database (`vis` and `mvis`/`msite`)

### merge

Similar to `inspect`, but accepts multiple database backups, merging the `Visit`s together and dropping you into a REPL

```
Usage: ffexport merge [OPTIONS] SQLITE_DB...

  Extracts history/site metadata from multiple sqlite databases.

  Provide multiple sqlite databases as positional arguments, e.g.: ffexport
  merge ~/data/firefox/dbs/*.sqlite

  Provides a similar interface to inspect; drops you into a REPL to access
  the data.

Options:
  --include-live              In addition to any provided databases, copy
                              current (firefox) history to /tmp and merge it
                              as well
```

(also accepts the --browser and --profile arguments like `save`)

Example:

```
$ ffexport merge --include-live ~/data/firefox/dbs/*.sqlite
[D 200828 18:53:54 save_hist:67] backing up to /tmp/tmp8tvyotv9/places-20200829015354.sqlite
[D 200828 18:53:54 save_hist:71] done!
[D 200828 18:53:54 merge_db:52] merging information from 3 databases...
[D 200828 18:53:54 parse_db:71] Parsing visits from /home/sean/data/firefox/dbs/places-20200828223058.sqlite...
[D 200828 18:53:55 parse_db:90] Parsing sitedata from /home/sean/data/firefox/dbs/places-20200828223058.sqlite...
[D 200828 18:53:56 parse_db:71] Parsing visits from /home/sean/data/firefox/dbs/places-20200828231237.sqlite...
[D 200828 18:53:56 parse_db:90] Parsing sitedata from /home/sean/data/firefox/dbs/places-20200828231237.sqlite...
[D 200828 18:53:57 parse_db:71] Parsing visits from /tmp/tmp8tvyotv9/places-20200829015354.sqlite...
[D 200828 18:53:58 parse_db:90] Parsing sitedata from /tmp/tmp8tvyotv9/places-20200829015354.sqlite...
[D 200828 18:53:59 merge_db:64] Summary: removed 183,973 duplicates...
[D 200828 18:53:59 merge_db:65] Summary: returning 92,066 visit entries...
Python 3.8.5 (default, Jul 27 2020, 08:42:51)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.17.0 -- An enhanced Interactive Python. Type '?' for help.

Use merged_vis to access merged data from all databases
```

## Library Usage

Can also import and provide files from python elsewhere.

```
>>> import ffexport, glob
>>> visits = list(ffexport.read_and_merge(*glob.glob('data/firefox/dbs/*.sqlite')))  # note the splat, read_and_merge accepts variadic arguments
>>> visits[10000]
Visit(
  url="https://github.com/python-mario/mario",
  visit_date=datetime.datetime(2020, 6, 24, 2, 23, 32, 482000, tzinfo=<UTC>),
  visit_type=1,
  title="python-mario/mario: Powerful Python pipelines for your shell",
  description="Powerful Python pipelines for your shell . Contribute to python-mario/mario development by creating an account on GitHub.",
  preview_image="https://repository-images.githubusercontent.com/185277224/2ce27080-b915-11e9-8abc-088ab263dbd9",
)
```

For an example, see my [`HPI`](https://github.com/seanbreckenridge/HPI/blob/master/my/browsing.py) integration.

The `Visit` it returns is a `NamedTuple`; which is all serializable to json, except the `datetime`. You could convert the `datetime` to epoch time, create a corresponding `dict` and dump that to json, or just use my [`autotui`](https://github.com/seanbreckenridge/autotui) library to do that for you:

```
>>> import glob, ffexport, autotui
>>> visits = list(ffexport.read_and_merge(*glob.glob('data/firefox/dbs/*.sqlite')))
>>> json_items: str = autotui.namedtuple_sequence_dumps(visits, indent=None)  # infers types from the NamedTuple type hints
>>> json_items[:1000]
'[{"url": "https://www.mozilla.org/privacy/firefox/", "visit_date": 1593250194, "visit_type": 1, "title": null, "description": null, "preview_image": null}, {"url": "https://www.mozilla.org/en-US/firefox/78.0a2/firstrun/", "visit_date": 1593250194, "visit_type": 1, "title": "Firefox Developer Edition", "description": "Firefox Developer Edition is the blazing fast browser that offers cutting edge developer tools and latest features like CSS Grid support and framework debugging", "preview_image": "https://www.mozilla.org/media/protocol/img/logos/firefox/browser/developer/og.0e5d59686805.png"}, {"url": "https://www.mozilla.org/en-US/firefox/78.0a2/firstrun/", "visit_date": 1593324947, "visit_type": 1, "title": "Firefox Developer Edition", "description": "Firefox Developer Edition is the blazing fast browser that offers cutting edge developer tools and latest features like CSS Grid support and framework debugging", "preview_image": "https://www.mozilla.org/media/protocol/img/logos/firefox/b'
```

#### Notes

See [here](https://web.archive.org/web/20190730231715/https://www.forensicswiki.org/wiki/Mozilla_Firefox_3_History_File_Format#moz_historyvisits) for what the `visit_type` enum means.

I considered using [`cachew`](https://github.com/karlicoss/cachew) but because of the volume of the data, it ends up being slower than reading directly from the sqlite database exports. Both the `visits` and `sitedata` functions are `cachew` compliant though, you'd just have to wrap it yourself. See [`here`](https://github.com/seanbreckenridge/ffexport/issues/6) for more info.

---

`save_hist.py`/initial structure is modified from [`karlicoss/promnesia`](https://github.com/karlicoss/promnesia/)

