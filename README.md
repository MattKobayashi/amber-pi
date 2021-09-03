# amber-pi

amber-pi is a Python script for polling the [Amber Electric API](https://app.amber.com.au/developers/) and using the data to set [PiStop traffic lights](https://github.com/PiHw/Pi-Stop/blob/master/README.md) according to the current power price.

## Installation

Ensure you have Python 3.x installed on your system (it's pre-installed on [Raspberry Pi OS](https://www.raspberrypi.org/software/)). Install the dependencies from requirements.txt if they're not already installed (again, these are pre-installed with Raspberry Pi OS):

```bash
cd /path/to/requirements

python3 -m pip install -r requirements.txt
```

## Usage

Edit the script and add your API key and site ID from the Amber Electric API. The variables you need to edit are:

* `apiKey`
* `siteId`

You can also optionally adjust the prices (in c/kWh) that trigger changes to the lights. The variables are:

* `alertHigh`: Above this price, the red light is set.
* `alertLow`: Below this price, the green light is set.
* All prices in between will trigger an amber light.

The script is intended to be run as a cronjob. Edit your crontab:

```bash
crontab -e
```

Add the following line (use this link if you want to change how often the script is called):

```
1/5 * * * * python3 /path/to/script/amber-pi.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)