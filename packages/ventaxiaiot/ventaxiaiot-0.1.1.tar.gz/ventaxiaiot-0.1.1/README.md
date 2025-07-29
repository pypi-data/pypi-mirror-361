# ventaxiaiot
A python library to comunicate with the Wifi module of the Vent Axia Sentinel Kinetic Advance S


# ventaxiaiot

An async Python library to comunicate with the Wifi module of the Vent Axia Sentinel Kinetic Advance S


This is an early release and **under active development**, so use at your own risk.


> [!IMPORTANT]
> This project is **not officially affiliated with or supported by Vent-Axia**. Functionality may break at any time if the Vent-Axia API changes without warning.



## Installation

The easiest method is to install using pip (`pip`/`pip3`):

```bash
pip install ventaxiaiot
```


Installing within a [Python virtual environment](https://docs.python.org/3/library/venv.html) is recommended:


```bash
python -m venv .venv
source .venv/bin/activate
pip install ventaxiaiot
```

To upgrade  to the latest version:

```bash
pip install --upgrade ventaxiaiot
```




## Running as CLI.


```bash
cli.py status 
```

Configuration file will be searched for in `./.config.json` 

### Example configuration file

```config.json
{
  "host": "host-ip",
  "port": 0,
  "identity": "secert-id",
  "psk_key": "device-wifi-password",
  "wifi_device_id": "your-device-model"
}
```