# SondeHub-Amateur BalloonAlert Utility
What this tool does:
* Listens to the SondeHub-Amateur live data stream (using [pysondehub](https://github.com/projecthorus/pysondehub/))
* Filters telemetry based on:
  * Radius from a fixed location
  * A Geo-Fence
  * Flight type (e.g. pico-floater vs up-down balloon)
* Runs float predictions for floater balloons using the [SondeHub Tawhiri](https://github.com/projecthorus/tawhiri/) API
* Sends a notification if either the prediction, or the live telemetry matches the filters, via:
  * Email
  * (Other methods? TBD?)

### Contacts
* [Mark Jessop](https://github.com/darksidelemm) - vk5qi@rfhead.net

## Running
Make a copy of the example configuration file, and modify as required:
```shell
$ cp alert.cfg.example alert.cfg
```

(Optional, though recommended) Create a Python virtual environment:
```shell
$ python3 -m venv venv
$ . venv/bin/activate
```

Install required Python dependencies:
```shell
$ pip install -r requirements.txt
```

Run balloonalert:
```shell
$ python -m balloonalert alert.cfg
```