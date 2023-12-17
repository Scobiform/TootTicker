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
git clone https://github.com/your-username/TootTicker.git
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
1. Edit TootTicker.py
```
createSecrets():
    # Replace the following placeholders with your actual values
    app_name = 'TootTicker - boost your bubble'  # Replace with your desired app name
    instance_url = 'https://mastodon.social/'  # Replace with your Mastodon instance URL
    email = 'your@mail.com'  # Replace with your Mastodon account email
    password = 'yourPassword'  # Replace with your Mastodon account password
```
2. Run
```
python3 TootTicker.py
```
2. Wait till the gathering is done.

3. Open the index.html in public folder.

The account informations will be saved to accounts/ folder

## Contributing

Contributions are welcome!

## License
TootTicker is licensed under the GNU General Public License v3.0.
