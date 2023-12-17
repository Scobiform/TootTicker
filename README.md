![TootTicker Header](https://files.mastodon.social/accounts/headers/111/505/407/593/832/846/original/fdbeaeee174c3375.png)

# TootTicker

[![Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://opensource.org/licenses/GPL-3.0)

> Requesting account information via Mastodon API and saving it as pure JSON.

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Background

TootTicker is a Python script that fetches account information from provided Mastodon handles (@INSTANCE@USERNAME). The script utilizes the Mastodon API to retrieve details and saves this information in JSON files in the 'accounts' directory.

It will also create a basic html overview in the 'public' folder.

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
## Usage

### 1. Edit TootTicker.py

First, you need to configure `TootTicker.py` with your details:

```python
# Configuration
app_name = 'TootTicker - boost your bubble'  # Replace with your desired app name
instance_url = 'mastodon.social'  # Replace with your Mastodon instance URL
email = ''  # Replace with your Mastodon account email
password = ''  # Replace with your Mastodon account password
```

### 2. Run the Script

Execute the script by running the following command in your terminal:

```bash
python3 TootTicker.py
```

### 3. Wait for Data Gathering

Allow some time for the script to gather the necessary data.

### 4. Access the Results

After the data gathering is complete:

- Open `index.html` located in the `public` folder.

The account information will be saved in the `accounts/` folder.

### Credits

Special thanks to the contributors from German media sites:

- Sebastian: [@pertsch.social@Sebastian](https://pertsch.social/@Sebastian)
- Mho: [@social.heise.de@mho](https://social.heise.de/@mho)

## Contributing

Contributions are welcome!

## License
TootTicker is licensed under the GNU General Public License v3.0.
