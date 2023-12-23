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

**TootTicker** is currently under heavy development, and its features and commands are subject to change. Below are the basic steps to get started with it, but please refer to the latest documentation for the most up-to-date information.

### Getting Started

1. **Installation**: 
   - Describe how to install your application, including any prerequisites like Python, Node.js, etc.
   - Provide any commands needed to install the project or its dependencies.

2. **Configuration**: 
   - Guide users through setting up any necessary configuration files, environment variables, or secrets.

3. **Running the Application**: 
   - Give instructions on how to start the application and any necessary services.
   - Include examples of command-line usage if applicable.

### Common Tasks

- **Adding a Category**: Describe how users can add a category for list streaming.
  ```bash
  command_or_steps_here
  
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

