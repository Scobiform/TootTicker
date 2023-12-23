import os
import json
import threading
import time
from threading import Event, Thread
import traceback
from flask import Flask, render_template, request
from mastodon import Mastodon, MastodonAPIError, MastodonFileNotFoundError, MastodonIllegalArgumentError, MastodonMalformedEventError, MastodonRatelimitError, MastodonServerError, MastodonVersionError, StreamListener

# TootTicker - boost your bubble
# Gathering account informations from Mastodon 
# and make them available as pure JSON
# GPLv3 - 2023 - by scobiform.com
# github.com/Scobiform/TootTicker

# THe following libraries are used in this project:
# Mastodon.py - MIT License - https://github.com/halcy/Mastodon.py
# Chart.js - MIT License - https://www.chartjs.org/
# Flask - BSD License - https://flask.palletsprojects.com/en/2.0.x/
# Gunicorn - https://gunicorn.org/

# You can see a demo of this project here: https://tootticker.scobiform.com/
# This project is still in development and will be updated frequently.
# If you have any suggestions or ideas, please let me know.

# Configuration (#Todo Refactor => config.json)
# You can remove your credentials after the first run
app_name = 'TootTicker - boost your bubble'  # Replace with your desired app name
instance_url = 'mastodon.social'  # Replace with your Mastodon instance URL
email = ''  # Replace with your Mastodon account email
password = ''  # Replace with your Mastodon account password

# Global variables
seen_toot_ids = set()  # A set to keep track of seen toot IDs for fast lookup
data = {}  # A dictionary to store the data from config.json

# Get data from config.json and save to data
with open('config.json', 'r') as file:
    data = json.load(file)

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

# Function to add accounts to Mastodon lists
def addAccountsToMastodonLists(mastodon, data):
    """
    Adds accounts to Mastodon lists based on their category.

    :param mastodon: An authenticated instance of the Mastodon API.
    :param accounts_by_category: A dictionary with category names as keys and lists of account handles as values.
    :param stop_token: A threading.Event() object used to stop the thread safely.
    """
    try:
        # Iterate through each category and its accounts
        for category_name, accounts in data.items():
            # Get or create the list for the current category
            list_id = getOrCreateList(mastodon, category_name)

            # Iterate through each account in the current category
            for account_name in accounts:
                # Resolve the account name to get the account ID
                search_result = mastodon.account_search(account_name)
                if search_result:
                    account_id = search_result[0]['id']
                    print(f"Resolved account {account_name} to ID {account_id}")

                    # Follow the account if not already following (optional based on your requirements)
                    mastodon.account_follow(account_id)

                    # Add the account to the list
                    added = mastodon.list_accounts_add(list_id, account_id)
                    if added:
                        print(f"Added {account_name} to {category_name}")
                    else:
                        print(f"Failed to add {account_name} to {category_name}")
                else:
                    print(f"No account found for {account_name}")
    # Handle exceptions - Mastodon.py
        '''https://mastodonpy.readthedocs.io/en/latest/03_errors.html'''
    except MastodonAPIError as e:
        print(f"MastodonAPIError: {e}")
    except MastodonIllegalArgumentError as e:
        print(f"MastodonIllegalArgumentError: {e}")
    except MastodonFileNotFoundError as e:
        print(f"MastodonFileNotFoundError: {e}")
    except MastodonMalformedEventError as e:
        print(f"MastodonMalformedEventError: {e}")
    except MastodonRatelimitError as e:
        print(f"MastodonRatelimitError: {e}")
    except MastodonVersionError as e:
        print(f"MastodonVersionError: {e}")
    except Exception as e:
        print(f"Error adding accounts to lists: {e}")

# Save toot to folder toots/
def saveJson(toot):
    ''' 
        
    '''
    try:
        # Create the 'toots/' directory if it doesn't exist
        if not os.path.exists('toots/'):
            # Create the directory 
            os.makedirs('toots/')
        with open(f"toots/{toot['id']}.json", encoding='utf-8', mode='w') as file:
            json.dump(toot, file, indent=4, default=str)
    except Exception as errorCode:
        print(errorCode)

# Function to get live toots
def getLiveTootsJSON(numberOfToots=420):
    global seen_toot_ids # A set to keep track of seen toot IDs for fast lookup
    toots = []

    for filename in os.listdir('toots/'):
        if filename.endswith('.json'):
            file_path = os.path.join('toots/', filename)

            # Check if the file was modified within the last 24 hours
            if os.path.getmtime(file_path) > time.time() - 86400:
                with open(file_path, 'r') as file:
                    try:
                        toot = json.load(file)
                        # Check if the toot's ID is new
                        if toot['id'] not in seen_toot_ids:
                            seen_toot_ids.add(toot['id'])
                            toots.append(toot)
                            print(f"Added toot {toot['id']} to live toots")
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from {filename}: {e}")

    # Sort the toots by creation time or other criteria if needed
    toots.sort(key=lambda x: x['created_at'], reverse=False)

    # Limit the number of toots to the specified amount
    limited_toots = toots[:numberOfToots]

    # Return the toots as a JSON string
    return json.dumps(limited_toots)

# Create a file if it doesn't exist
def createFile(file_name):
    try:
        with open(file_name, 'a'):
            pass
        print(f"File '{file_name}' created successfully.")
    except Exception as e:
        print(f"Error creating '{file_name}': {e}")

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
            # Sleep for 14 seconds to avoid rate limiting
            time.sleep(42)
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
# TODO: Refactor this is smaller bits
def footerScripts():
    '''Returns footer scripts
    
    Returns:
        [type] -- [description]
        
    '''

    #TODO: Refactor this is smaller bits
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
                            // Clear the container before appending new toots if necessary
                            // container.innerHTML = ''; // Uncomment this if you want to remove old toots when new ones arrive
                            
                            newToots.forEach(toot => {      
                                const mastodonHandle = `${toot.account.username}@${toot.url.split("https://")[1].split("/")[0]}`;
                                const tootElement = document.createElement('div'); // Moved inside the loop
                                tootElement.classList.add('toot');  // Add a 'toot' class to the div
                                            
                                tootElement.innerHTML = `
                                    <div class="tootAvatar">
                                        <a href="${meUrl}@${mastodonHandle}" alt="${toot.account.display_name}" 
                                        nofollow="true" 
                                        target="_blank" 
                                        rel="noopener noreferrer">
                                            <img src="${toot.account.avatar}">
                                        </a>
                                    </div>
                                    <div class="tootName">
                                        <a href="${meUrl}@${mastodonHandle}" alt="${toot.account.display_name}"
                                        nofollow="true"
                                        target="_blank"
                                        rel="noopener noreferrer">
                                            ${toot.account.display_name}
                                        </a>
                                    </div>
                                    <div class="tootDate">
                                        ${new Date(toot.created_at).toLocaleString('en-US', { hour12: false })}
                                    </div>
                                    <div class="toots-content">
                                        ${toot.content}
                                        <div class="mediaAttachments">
                                            ${toot.reblog ? toot.reblog.media_attachments.map(media => {
                                                if (media.type === 'image') {
                                                    return `<img src="${media.preview_url}" alt="${toot.account.display_name}">`;
                                                } else if (media.type === 'video') {
                                                    return `<video controls src="${media.preview_url}" alt="${toot.account.display_name}"></video>`;
                                                } else {
                                                    return `<a href="${media.url}" alt="${toot.account.display_name}">Attachment</a>`;
                                                }
                                            }).join('') : ''}
                                        </div>
                                        <div class="tootUrl">
                                            <a href="${meUrl}@${mastodonHandle}/${toot.id}"
                                            alt="View on Mastodon"
                                            aria-label="View on Mastodon"
                                            nofollow="true"
                                            target="_blank"
                                            rel="noopener noreferrer">
                                                 View on Mastodon
                                            </a>
                                        </div>
                                    </div>
                                `;
                                // Add the new toot to the container
                                container.appendChild(tootElement);  

                                // Scroll to the Bottom of the container
                                container.scrollTop = container.scrollHeight;
                            });
                        })
                        .catch(error => console.error('Error fetching new toots:', error));
                }
                // Poll for new toots every n seconds
                setInterval(fetchAndUpdateToots, 21000);
            </script>"""
    return scripts

# Function to get or create liveToots
def generateLiveTootsHTML():
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
    '''
        This class is used to listen to a Mastodon list.
        It inherits from StreamListener and overrides the on_update method.
    
    '''
    # Override the __init__ method
    def __init__(self):
        super().__init__()

    # Override the on_update method
    def on_update(self, status):
        if status['reblog']:
            print(f"New boost from list: {status['reblog']['content']}")
        else:
            print(f"New status from list: {status['content']}")
            saveJson(status)

    def on_notification(self, notification):
        print(f"New notification: {notification['type']}")

    def on_delete(self, status_id):
        print(f"Status deleted: {status_id}")

    def handle_heartbeat(self):
        print("Heartbeat received")
    
def StreamMastodonList(mastodon, list_id):
    try:
        # Create a listener
        listener = ListStreamer()
        mastodon.stream_list(list_id, listener) 
    except Exception as e:
        print(f"Error streaming list {list_id}")
        time.sleep(42)

# Worker function
def worker(add, save, stream, mastodon):
    """     Your worker function, which does something in the background.
    Arguments:
        addAccounts {int} -- Add accounts to Mastodon lists (0 = no, 1 = yes)
        saveAccountInfo {int} -- Save account information to JSON (0 = no, 1 = yes)
        mastodonListStreams {int} -- Stream Mastodon lists (0 = no, 1 = yes)
        mastodon {object} -- Mastodon object
        data {dict} -- Data from config.json
    """
    print("Worker is running...")
    try:
        # Create a list of threads
        threads = []     

        # Create a thread for each category
        if stream:
            # Iterate through each category and start a thread for each
            for category in data:
                print(category)
                listIdFromCategoryName = getOrCreateList(mastodon, category)
                #Create add accounts to Mastodon lists thread for each category
                if add:
                    addThread = Thread(target=addAccountsToMastodonLists, args=(mastodon, data[0]))
                    threads.append(addThread)
                # Create list stream thread for each category
                listStreams = Thread(target=StreamMastodonList, args=(mastodon, listIdFromCategoryName))
                threads.append(listStreams)

        # Create thread to save account information to JSON
        if save:
            # Iterate through each category and start a thread for each
            for category, urls in data.items():
                # Create account gathering thread for each category
                accountInfos = Thread(target=saveAccountInfoToJSON, args=(mastodon, category, urls))
                threads.append(accountInfos)

        # Start all threads
        for thread in threads:
            thread.start()
            
    except Exception as errorcode:
        print("ERROR: " + str(errorcode))

# Flask app
app = Flask(__name__)

# Initialize the app
def initialize_app(add, save, stream):
    """Initialize the Mastodon API and any global variables."""

    # Check for secrets
    checkForSecrets()  # Ensure this function sets necessary secrets

    # Authenticate the app
    mastodon = Mastodon(access_token='usercred.secret')

    # Who Am I (logging information about the authenticated user)
    me = mastodon.me()
    print("\nWho Am I?")
    print(me.username)
    print(me.id)
    print(me.url+'\n')

    # Start the worker
    ''' Parameters: addAccounts, saveAccountInfo, mastodonListStreams, mastodon  '''
    worker(add, save, stream, mastodon) 

# Route for the index page
@app.route('/')
def index():
    # Get the live toots JSON
    live_toots_html = generateLiveTootsHTML()  # Assume this function returns HTML for live toots
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

# Mock Toot
MockToot = type('MockToot', (object,), {'id': 1, 'content': 'Hello, World!', 'account': {'username': 'scobiform', 'display_name': 'Scobiform', 'avatar': 'https://files.mastodon.social/accounts/avatars/000/000/001/original/6c3f0d5a6d5c5f9f.png', 'url': 'https://mastodon.social/@scobiform'}})

# Route for the latest toots
@app.route('/get_latest_toots')
def latest_toots():
    toots = getLiveTootsJSON()
    return toots

# Route for the error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                           error_code=404, 
                           error_message='The requested URL was not found on the server.', 
                           request=request), 404

# Create the app
def create_app():
    initialize_app(0,0,1)
    return app