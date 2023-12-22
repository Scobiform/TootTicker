import datetime
from flask import Flask, render_template
from mastodon import Mastodon, StreamListener
import os
import json
import time
from threading import Event, Thread

# TootTicker - boost your bubble
# Gathering account informations from Mastodon 
# and make them available as pure JSON
# GPLv3 - 2023 - by scobiform.com
# github.com/Scobiform/TootTicker

# THe following libraries are used in this project:
# Mastodon.py - MIT License - https://github.com/halcy/Mastodon.py
# Chart.js - MIT License - https://www.chartjs.org/
# Flask - BSD License - https://flask.palletsprojects.com/en/2.0.x/

# You can see a demo of this project here: https://tootticker.scobiform.com/
# This project is still in development and will be updated frequently.
# If you have any suggestions or ideas, please let me know.

# Configuration
# You can remove your credentials after the first run
app_name = 'TootTicker - boost your bubble'  # Replace with your desired app name
instance_url = 'mastodon.social'  # Replace with your Mastodon instance URL
email = ''  # Replace with your Mastodon account email
password = ''  # Replace with your Mastodon account password

# Flask app
app = Flask(__name__)

# Create a file if it doesn't exist
def createFile(file_name):
    try:
        with open(file_name, 'a'):
            pass
        print(f"File '{file_name}' created successfully.")
    except Exception as e:
        print(f"Error creating '{file_name}': {e}")

# Create a folder if it doesn't exist
def createFolder(folder_name):
    try:
        os.makedirs(folder_name, exist_ok=True)
        print(f"Folder '{folder_name}' created successfully.")
    except Exception as e:
        print(f"Error creating '{folder_name}': {e}")

# Create Mastodon app and get user credentials
def createSecrets():
    # Create the secrets files if they don't exist
    createFile('clientcred.secret')
    createFile('usercred.secret')

    # Create Mastodon app (client credentials)
    Mastodon.create_app(
        app_name,
        api_base_url=instance_url,
        to_file='clientcred.secret'
    )

    # Initialize Mastodon with client credentials
    mastodon = Mastodon(
        client_id='clientcred.secret',
        api_base_url=instance_url
    )

    # Log in and save user credentials
    mastodon.log_in(
        email,
        password,
        to_file='usercred.secret'
    )

# If secrets are not present, create them
def checkForSecrets():
    if os.path.exists('usercred.secret'):
        print("Secrets found.")
    else:
        print("Secrets not found.")
        createSecrets()

# Load configuration from JSON file
with open('config.json', 'r') as file:
    data = json.load(file)

# Function to get account information from Mastodon and save to JSON file
def saveAccountInfoToJSON(mastodon, category, urls):
    print(f"Starting account gathering for {category}...")

    # Create the 'accounts/' directory if it doesn't exist
    accounts_directory = f'accounts/{category}/'
    os.makedirs(accounts_directory, exist_ok=True)
    print(f"Saving account infos to {accounts_directory}")

    # Iterate through each URL in the list
    for url in urls:
        try:
            # Resolve the profile URL to get the account details
            account = mastodon.account_search(url)

            # Check if the account exists
            if not account:
                continue

            # Get the user ID
            user_id = account[0]['id']

            # Get recent toots from the user's timeline
            toots = mastodon.account_statuses(user_id, limit=1)

            # Create a dictionary with account information
            account_info = {
                "Account Name": account[0]['username'],
                "Account URL": account[0]['url'],
                "Display Name": account[0]['display_name'],
                "Instance": '@' + account[0]['url'].split('https://')[1].split('/')[0],
                "Account ID": user_id,
                "Note": account[0]['note'],
                "Followers": account[0]['followers_count'],
                "Following": account[0]['following_count'],
                "Toots": account[0]['statuses_count'],
                "Created": account[0]['created_at'],
                "Last Active": account[0]['last_status_at'],
                "Bot": account[0]['bot'],
                "Avatar": account[0]['avatar'],
                "Header": account[0]['header'],
                "TootsList": toots
            }

            # Save the JSON file to the folder
            with open(os.path.join(accounts_directory, f"{user_id}.json"), 'w') as file:
                json.dump(account_info, file, indent=4, default=str)
            print(f"Saved account info for {account[0]['username']}")

            # Sleep for 2.1 seconds to avoid rate limiting
            time.sleep(2.1)

        except Exception as e:
            print(f"Error processing {url}: {e}")

# Function to generate the HTML header
def generateHTMLHeader():
    # Write the HTML header
    html_header = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>TootTicker - boost your bubble</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://mastodon.social/embed.js" async="async"></script>
        <link rel="stylesheet" type="text/css" href="static/style.css">    
    </head>
    <body>
    """
    return html_header

# Header scripts
def headerScripts():
    scripts = """<script>

            function toggleVisibility(category) {
                var accounts = document.querySelectorAll("." + category);
                accounts.forEach(function(account) {
                    account.style.display = account.style.display === "none" ? "block" : "none";
                });
            }

            function toggleToots(elementId) {
                var element = document.getElementById(elementId);
                if (element) {
                    element.style.display = element.style.display === "none" ? "block" : "none";
                }
            }

        </script>
    """
    return scripts

# Function to generate the Chart.js data object
# Will save the data to a JSON file with timestamp
def generateChart():
    # Get categories from the data dictionary
    categories = list(data.keys())
    categories_data = {}

    for category in categories:
        category_path = f'accounts/{category}/'
        category_data = {}

        if os.path.exists(category_path):
            for json_file in os.listdir(category_path):
                if json_file.endswith('.json'):
                    with open(os.path.join(category_path, json_file), 'r') as file:
                        try:
                            account_info = json.load(file)
                            account_name = account_info["Display Name"]

                            # Initialize the data structure for this account
                            if account_name not in category_data:
                                category_data[account_name] = {'Followers': 0, 'Toots': 0, 'Following': 0}

                            # Increment the metrics
                            category_data[account_name]['Followers'] += account_info.get("Followers", 0)
                            category_data[account_name]['Following'] += account_info.get("Following", 0)

                            # Add the count of toots
                            category_data[account_name]['Toots'] += account_info.get("Toots",0)

                        except json.decoder.JSONDecodeError as e:
                            print(f"Error decoding {json_file}: {e}")

        categories_data[category] = category_data

    # Convert the Python dictionary to a JavaScript object notation
    js_data_object = json.dumps(categories_data, indent=4)

    # Save the JavaScript object notation to a file with timestamp
    timestamp = time.strftime("%Y%m%d%H%M")
    with open(f'accounts/data-{timestamp}.json', 'w') as file:
        file.write(js_data_object)

    # Return the JavaScript object notation
    return js_data_object

# Function to generate HTML overview
def generateAccountOverview():

    # Function to sort accounts based on a given key
    def sort_accounts(accounts, key):
        # Helper function to sort accounts based on a given key
        return sorted(accounts, key=lambda x: x[key], reverse=True)

    # Begin to write the HTML content
    html_content = '<div class="grid">\n'

    # Categories to iterate through
    categories = list(data.keys())

    # Iterate through each category
    for category in categories:
        # Write the HTML header for each category
        html_content += f'<h1 onclick="toggleVisibility(\'{category}\')">{category}</h1>\n'

        # Write the category chart container
        html_content += f'<div id="chart-container-{category}" class="{category}"></div>\n'

    # Close the grid wrapper
    html_content += '</div>\n'

    # Return the HTML content
    return html_content

# Function to generate the footer
def generateHTMLFooter():
    html_footer = ("""
        </body>
    </html>
    """)
    return html_footer

# Returns footer scripts
def footerScripts():
    scripts = """<script>
                const categoriesData = """ + generateChart() + """;

                function createChart(containerId, category, categoryData) {
                    const ctx = document.createElement('canvas');
                    document.getElementById(containerId).appendChild(ctx);

                    const datasets = [];
                    const labels = Object.keys(categoryData); // Account names

                    // Metrics to display (e.g., Followers, Toots, Following)
                    const metrics = ["Followers", "Toots", "Following"];

                    metrics.forEach(metric => {
                        const data = labels.map(label => categoryData[label][metric] || 0);
                        datasets.push({
                            label: `${metric}`,
                            data: data,
                            backgroundColor: getRandomColor(),
                            borderColor: 'rgba(0, 123, 255, 0.7)',
                            borderWidth: 1
                        });
                    });

                    new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: datasets
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: { beginAtZero: true }
                            }
                        }
                    });
                }

                window.onload = function() {
                    for (const [category, categoryData] of Object.entries(categoriesData)) {
                        createChart(`chart-container-${category}`, category, categoryData);
                    }
                };

                function getRandomColor() {
                        // Base color 99, 100, 255
                        const baseR = 99;
                        const baseG = 100;
                        const baseB = 255;

                        // Define a range for variation (+/- 42)
                        const range = 42;

                        // Generate random variations around the base color within the specified range
                        const r = Math.max(Math.min(baseR + Math.floor(Math.random() * (range * 2 + 1)) - range, 255), 0);
                        const g = Math.max(Math.min(baseG + Math.floor(Math.random() * (range * 2 + 1)) - range, 255), 0);
                        const b = Math.max(Math.min(baseB + Math.floor(Math.random() * (range * 2 + 1)) - range, 255), 0);

                        return `rgba(${r}, ${g}, ${b}, 0.5)`;
                }


                function fetchAndUpdateToots() {
                    fetch('/get_latest_toots')
                        .then(response => response.json())
                        .then(newToots => {
                            const container = document.getElementById('liveToots');
                            const meUrl = 'https://mastodon.social/';
                            const instanceUrl = '${toot.url.split("https://")[1].split("/")[0]}';
                            // Create an element for the new toot and add it to the container
                            const tootElement = document.createElement('div');
                            // clear the container
                            container.innerHTML = '';
                            newToots.forEach(toot => {                     
                                tootElement.classList.add('toot');  // Add a 'toot' class to the div
                                 
                                tootElement.innerHTML = `
                                    <div class="tootAvatar">
                                        <a href="${meUrl}/@${toot.account.username}@${instanceUrl}" alt="${toot.account.display_name}" 
                                        nofollow="true" 
                                        target="_blank" 
                                        rel="noopener noreferrer">
                                            <img src="${toot.account.avatar}">
                                        </a>
                                    </div>
                                    <div class="tootDate">
                                        ${toot.created_at}
                                    </div>
                                    <div class="toots-content">
                                        ${toot.content}
                                        <div class="tootUrl">
                                            <a href="${toot.url}">${toot.url}</a>
                                        </div>
                                    </div>
                                `;
                                // Add the new toot to the container
                                container.appendChild(tootElement);      
                            });
                        })
                        .catch(error => console.error('Error fetching new toots:', error));
                }
                // Poll for new toots every 7 seconds
                setInterval(fetchAndUpdateToots, 7000);
    
            </script>"""
    return scripts

# Route for the index page
@app.route('/')
def index():
    # Get the live toots JSON
    live_toots_html = generateLiveTootsHTML(mastodon)  # Assume this function returns HTML for live toots
    # Get the account overview HTML
    account_overview_html = generateAccountOverview()  # And this returns HTML for account overview
    # Get the HTML header
    html_header = generateHTMLHeader()
    # Get the header scripts
    header_scripts = headerScripts()
    # Get the HTML footer
    html_footer = generateHTMLFooter()
    # Get the footer scripts
    footer_scripts = footerScripts()

    # Render the template with the JSON string
    return render_template('index.html', 
        live_toots_html=live_toots_html, 
        account_overview_html=account_overview_html, 
        html_header=html_header, 
        header_scripts=header_scripts,
        html_footer=html_footer,
        footer_scripts=footer_scripts
    )
# Run Flask app
def run_flask_app():
    app.run(debug=True, use_reloader=False) 

@app.route('/get_latest_toots')
def latest_toots():
    toots = getLiveTootsJSON()
    return toots

# Function to add accounts to Mastodon lists
def addAccountsToMastodonLIsts(mastodon, accounts_by_category, stop_token=None):
    """
    Adds accounts to Mastodon lists based on their category.

    :param mastodon: An authenticated instance of the Mastodon API.
    :param accounts_by_category: A dictionary with category names as keys and lists of account handles as values.
    """ 
    # Create all lists if they don't exist
    for category in accounts_by_category.keys():
        list_id = getOrCreateList(mastodon, category)
        print(f"Created list '{category}' with ID {list_id}")

    for category, accounts in accounts_by_category.items():
        print(f"Adding accounts to list '{category}'")

        # Get the list ID
        list_id = getOrCreateList(mastodon, category)

        for account_name in accounts:
            try:
                # Resolve the account name to get the account ID
                account_id = mastodon.account_search(account_name)[0]['id']
                # Follow the account
                mastodon.account_follow(account_id)
                print(f"Followed account {account_id}")
                # Add the account to the list
                mastodon.list_accounts_add(list_id, account_id)
                print(f"Added account {account_id} to list '{category}'")
            except Exception as e:
                print(f"Error adding account {account_id} to list '{category}': {e}")

# Function to get or create a list
def getOrCreateList(mastodon, list_name):
    """
    Retrieves the ID of a list with the given name, or creates it if it doesn't exist.

    :param mastodon: An authenticated instance of the Mastodon API.
    :param list_name: The name of the list to retrieve or create.
    :return: The ID of the list.
    """
    # Retrieve all existing lists
    existing_lists = mastodon.lists()

    # Check if the list already exists and return its ID if it does
    for lst in existing_lists:
        if lst['title'].lower() == list_name.lower():
            return lst['id']

    # If the list does not exist, create it and return the new list's ID
    new_list = mastodon.list_create(list_name)
    return new_list['id']

# Save toot to folder toots/
def saveJson(toot):
    createFolder('toots/')
    try:    
        with open(f"toots/{toot['id']}.json", encoding='utf-8', mode='w') as file:
            json.dump(toot, file, indent=4, default=str)
    except Exception as errorCode:
        print(errorCode)

# Get all toots from toots/ folder as JSON
def getLiveTootsJSON(numberOfToots=7):
    date = datetime.datetime.now().timestamp()
    toots = []
    for toot in os.listdir('toots/'):
        if toot.endswith('.json'):
            # if date if less than 420 seconds old
            if date - os.path.getmtime(f"toots/{toot}") < 420:
                with open(f"toots/{toot}", 'r') as file:
                    toots.append(json.load(file))
    # Sort toots by date
    toots = sorted(toots, key=lambda x: x['created_at'], reverse=True)
    # Return only the latest toots
    return json.dumps(toots[:numberOfToots])

# Function to get or create liveToots
def generateLiveTootsHTML(mastodon):
    try:
        # Generate LiveToots HTML
        liveTootsHTML = f"""
            <div id="liveToots">              
        """
        liveTootsHTML += "</div>"
        return liveTootsHTML
    except Exception as errorCode:
        print(errorCode)

# List Streamer class
class ListStreamer(StreamListener):
    # Constructor
    def __init__(self):
        super().__init__()

    # Methods
    def on_update(self, status):
        if status['reblog']:
            print(f"New boost from list: {status['reblog']['content']}")
        else:
            print(f"New status from list: {status['content']}")
            # Append to liveToots.json
            saveJson(status)
            # Generate the index.html file

    def on_notification(self, notification):
        print(f"New notification: {notification['type']}")

    def on_delete(self, status_id):
        print(f"Status deleted: {status_id}")

def StreamMastodonLIst(mastodon, list_id):
    """
    Streams a specified Mastodon list.

    :param mastodon: An authenticated instance of the Mastodon API.
    :param list_id: The ID of the list you want to stream.
    """
    listener = ListStreamer()
    mastodon.stream_list(list_id, listener)

def worker(mastodon, on=False, stop_token=None):
    try:
        while True:
            # Check if the stopping token has been triggered
            if stop_token and stop_token.is_set():
                print("Stopping worker...")
                break

            # Create a list of threads
            threads = []

            # Create add accounts to Mastodon lists thread for each category
            # addAccounts = Thread(target=addAccountsToMastodonLIsts, args=(mastodon, data, stop_token))
            # threads.append(addAccounts)

            # Create stream Mastodon list thread for each category
            for category in data.keys():
                streamList = Thread(target=StreamMastodonLIst, args=(mastodon, getOrCreateList(mastodon, category)))
                threads.append(streamList)

            # Thread for flask app
            if not on:
                flaskApp = Thread(target=run_flask_app)
                threads.append(flaskApp)

            if on:
                # Iterate through each category and start a thread for each
                for category, urls in data.items():
                    # Create account gathering thread for each category
                    accountInfos = Thread(target=saveAccountInfoToJSON, args=(mastodon, category, urls))
                    threads.append(accountInfos)

            # Start all threads
            for thread in threads:
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Generate index.html
            if on:
                generateIndexFile()

            # Sleep for a period before restarting the process
            print("Sleeping for 5 minutes...")
            time.sleep(300)  # Sleep for 300 seconds (adjust as needed)
            print("Restarting...")

    except Exception as errorcode:
        print("ERROR: " + str(errorcode))

# Main function
def main():

    # Check for secrets
    checkForSecrets()
    
    # Authenticate the app
    global mastodon
    mastodon = Mastodon(access_token = 'usercred.secret')

    # Define the global data variable
    global data

    # Who Am I
    print("\nWho Am I?")
    print(mastodon.me().username)
    print(mastodon.me().id)
    print(mastodon.me().url+'\n')

    # Stopping token
    stop_token = Event()

    # Start Worker
    worker(mastodon, False, stop_token )

if __name__ == '__main__':
    main()
input()