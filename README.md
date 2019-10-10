# sp2battlebot

A bot for telegram. Get Splatoon2 battle info in telegram.

_* This project rewrite from [swift version](https://github.com/JoneWang/sp2battlebot-swift).*_

## Start

First, install dependencies.

``` bash
pip3 install -r requirements.txt
```

Set your bot token and administrator username in config.py.

``` bash
TELEGRAM_BOT_TOKEN = ''
ADMINISTRATOR_USERNAME = ''
```

Run

```bash
./sp2battlebot [start|stop|restart]
```

## Command

/setiksm - Set iksm_session.

/last - last50 - Show overview for last 50 battle.

/last - Get last battle info.

/last [0~49] - Get last battle with index.

/startpush - Startup push service.

/stoppush - Stop push service.

## Require

* python3
