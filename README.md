# TootTicker

[![Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://opensource.org/licenses/GPL-3.0)

> Requesting account information via Mastodon API and saving it as JSON.

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Background

TootTicker is a Python script that fetches account information from provided Mastodon handles (@INSTANCE@USERNAME). The script utilizes the Mastodon API to retrieve details and saves this information in JSON files in the 'accounts' directory.

* It will also create a HTML overview with charts for each category

* Will follow all accounts in your config.json

* Will create all categories as lists in your Mastodon account and add accounts to it

* Will stream all lists to the #LIveToots section of the HTML body.

* Will save all toots to the toots/ folder as JSON

![image](https://github.com/Scobiform/TootTicker/assets/9046630/df24ebb3-2d89-409e-9f12-269c901f45da)

## Install
# Clone the repository
```
git clone https://github.com/Scobiform/TootTicker.git
```
# Change into the project directory
```
cd TootTicker
```
# Install dependencies
```
pip install Mastodon.py
```
```
pip install flask
```
## Usage

**TootTicker** is currently under heavy development, and its features and commands are subject to change. 
Open ``` localhost:5000 ``` in your browser

### Credits

Special thanks to the contributors from German media sites:

- Sebastian: [@pertsch.social@Sebastian](https://pertsch.social/@Sebastian)
- Mho: [@social.heise.de@mho](https://social.heise.de/@mho)

## Contributing

Contributions are welcome!

## License
**TootTicker** is licensed under the **GNU General Public License v3.0**.

### Libraries Used:
The following libraries are used in this project, each with its respective license:

- **Mastodon.py**: MIT License - [View License](https://github.com/halcy/Mastodon.py)
- **Chart.js**: MIT License - [View License](https://www.chartjs.org/)
- **Flask**: BSD License - [View License](https://flask.palletsprojects.com/en/2.0.x/)
- **Gunicorn**: Multiple Licenses (MIT and others) - [View License Details](https://github.com/benoitc/gunicorn?tab=License-1-ov-file#readme)

### Note:
Please ensure to adhere to the licensing terms of each library and tool used in your project.

