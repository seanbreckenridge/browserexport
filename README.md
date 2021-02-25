# ffexport

[![PyPi version](https://img.shields.io/pypi/v/ffexport.svg)](https://pypi.python.org/pypi/ffexport) [![Python 3.6|3.7|3.8|3.9](https://img.shields.io/pypi/pyversions/ffexport.svg)](https://pypi.python.org/pypi/ffexport) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

This backs up firefox history and parses the resulting history (sqlite) files.

Primary function here is to export/interact with my firefox history. Functionality for Chrome are vestigal and I've left them there in case someone wants to mess with it. I recommend you take a look at [`promnesia`](https://github.com/karlicoss/promnesia) if you want immediate support for that.

See [here](https://web.archive.org/web/20190730231715/https://www.forensicswiki.org/wiki/Mozilla_Firefox_3_History_File_Format#moz_historyvisits) for how firefox stores its history.

## Install

`pip3 install ffexport`

Requires `python3.6+`

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

The `inspect` and `merge` commands also accept a `--json` flag, which dumps the result to STDOUT as JSON. Dates are serialized to epoch time.

Logs are hidden by default. To show the debug logs set `export FFEXPORT_LOGS=10` (uses [logging levels](https://docs.python.org/3/library/logging.html#logging-levels))

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
$ ffexport save --to ~/data/firefox
[D 200828 15:30:58 save_hist:67] backing up /home/sean/.mozilla/firefox/jfkdfwx.dev-edition-default/places.sqlite to /home/sean/data/firefox/places-20200828223058.sqlite
[D 200828 15:30:58 save_hist:71] done!
```

That atomically copies the firefox sqlite database which contains your history `--to` some backup directory.

### inspect

```
Usage: ffexport inspect [OPTIONS] SQLITE_DB

  Extracts history/site metadata from one sqlite database.

  Provide a firefox history sqlite databases as the first argument. Drops
  you into a REPL to access the data.

Options:
  --json  Print result to STDOUT as JSON
```

As an example:

```python
ffexport inspect ~/data/firefox/places-20200828223058.sqlite
[D 210225 04:38:27 parse_db:77] Reading individual visits from /home/sean/data/firefox/places-20200828223058.sqlite...
[D 210225 04:38:28 parse_db:96] Reading sitedata from /home/sean/data/firefox/places-20200828223058.sqlite...
Demo: Your most common sites....
[('github.com', 13775),
 ('www.youtube.com', 8108),
 ('duckduckgo.com', 8054),
 ('www.google.com', 6542),
 ('discord.com', 6134),
 ('sean.fish', 3264),
 ('stackoverflow.com', 2528),
 ('gitlab.com', 1608)]

Use mvis or msite to access raw visits/site data, vis for the merged data

In [1]: ....
```

That drops you into a REPL with access to the history from that database (`vis` and `mvis`/`msite`)

### merge

Similar to `inspect`, but accepts multiple database backups, removing any duplicates and dropping you into a REPL

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
  --json                      Print result to STDOUT as JSON
```

(also accepts the `--browser` and `--profile` flags like the `save` command, provide those if you have multiple profiles and are using the `--include-live` flag.

Example:

```python
ffexport merge --include-live ~/data/firefox/*.sqlite
[D 210225 04:39:43 save_hist:71] backing up /home/sean/.mozilla/firefox/lsinsptf.dev-edition-default/places.sqlite to /tmp/tmpv2ct3t0g/places-20210225123943.sqlite
[D 210225 04:39:43 save_hist:75] done!
[D 210225 04:39:43 merge_db:48] merging information from 10 databases...
[D 210225 04:39:43 parse_db:142] Reading visits from /home/sean/data/firefox/places-20200828223058.sqlite...
[D 210225 04:39:44 parse_db:142] Reading visits from /home/sean/data/firefox/places-20201010031025.sqlite...
[D 210225 04:39:45 parse_db:142] Reading visits from /home/sean/data/firefox/places-20201031031121.sqlite...
[D 210225 04:39:46 parse_db:142] Reading visits from /home/sean/data/firefox/places-20201121031143.sqlite...
[D 210225 04:39:47 parse_db:142] Reading visits from /home/sean/data/firefox/places-20201212031157.sqlite...
[D 210225 04:39:49 parse_db:142] Reading visits from /home/sean/data/firefox/places-20201226031225.sqlite...
[D 210225 04:39:50 parse_db:142] Reading visits from /home/sean/data/firefox/places-20210109031324.sqlite...
[D 210225 04:39:52 parse_db:142] Reading visits from /home/sean/data/firefox/places-20210208052811.sqlite...
[D 210225 04:39:53 parse_db:142] Reading visits from /home/sean/data/firefox/places-20210222065542.sqlite...
[D 210225 04:39:55 parse_db:142] Reading visits from /tmp/tmpv2ct3t0g/places-20210225123943.sqlite...
[D 210225 04:39:57 merge_db:60] Summary: removed 1,597,629 duplicates...
[D 210225 04:39:57 merge_db:61] Summary: returning 235,681 visit entries...

Use merged_vis to access merged data from all databases
```

To dump all that info to json:

```bash
$ ffexport merge --include-live --json ~/data/firefox/*.sqlite > ./history.json
$ du -h history.json
67M     history.json
```

## Library Usage

Can also import and provide files from python elsewhere. The two major functions you'd use are `ffexport.read_visits` (which reads/parses one database) and `ffexport.read_and_merge` (which parses multiple).

```python
>>> import ffexport, glob
>>> visits = list(ffexport.read_and_merge(*glob.glob('data/firefox/*.sqlite')))  # note the splat, read_and_merge accepts variadic arguments
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

For another example, see my [`HPI`](https://github.com/seanbreckenridge/HPI/blob/master/my/browsing.py) integration.

#### Notes

See [here](https://web.archive.org/web/20190730231715/https://www.forensicswiki.org/wiki/Mozilla_Firefox_3_History_File_Format#moz_historyvisits) for what the `visit_type` enum means.

I considered using [`cachew`](https://github.com/karlicoss/cachew) but because of the volume of the data, it ends up being slower than reading directly from the sqlite database exports. Both the `visits` and `sitedata` functions are `cachew` compliant though, you'd just have to wrap it yourself. See [`here`](https://github.com/seanbreckenridge/ffexport/issues/6) for more info.

---

`save_hist.py`/initial structure is modified from [`karlicoss/promnesia`](https://github.com/karlicoss/promnesia/)

---

### Testing

```bash
git clone https://github.com/seanbreckenridge/ffexport
cd ./ffexport
pip install '.[testing]'
mypy ./ffexport
pytest
```
