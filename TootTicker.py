import tracemalloc
from mastodon import Mastodon
import os
import json
import time
from threading import Thread

# TootTicker - boost your bubble
# Gathering account informations from Mastodon 
# and make them available as pure JSON
# GPLv3 - 2023 - by scobiform.com
# github.com/Scobiform/TootTicker

# THe following libraries are used in this project:
# Mastodon.py - GNU Affero General Public License v3.0
# Chart.js - MIT License - https://www.chartjs.org/

# You can see a demo of this project here: https://tootticker.scobiform.com/
# This project is still in development and will be updated frequently.
# If you have any suggestions or ideas, please let me know.

# Configuration
# You can remove your credentials after the first run
app_name = 'TootTicker - boost your bubble'  # Replace with your desired app name
instance_url = 'mastodon.social'  # Replace with your Mastodon instance URL
email = ''  # Replace with your Mastodon account email
password = ''  # Replace with your Mastodon account password

# Create a file if it doesn't exist
def create_file_if_not_exists(file_name):
    try:
        with open(file_name, 'a'):
            pass
        print(f"File '{file_name}' created successfully.")
    except Exception as e:
        print(f"Error creating '{file_name}': {e}")

# Create Mastodon app and get user credentials
def createSecrets():
    # Create the secrets files if they don't exist
    create_file_if_not_exists('clientcred.secret')
    create_file_if_not_exists('usercred.secret')

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
        <link rel="stylesheet" href="style.css">
        <script>

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
    </head>
    <body>
    """
    return html_header

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
    timestamp = time.strftime("%Y%m%d%H")
    with open(f'accounts/data-{timestamp}.json', 'w') as file:
        file.write(js_data_object)

    # Return the JavaScript object notation
    return js_data_object

# Function to generate HTML overview
def generateAccountOverview():

    # Get the current instance URL
    meUrl = 'https://'+mastodon.me().url.split("https://")[1].split("/")[0]

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
        # Get the list of JSON files in the 'accounts/' folder for the current category
        json_files = [f for f in os.listdir(f'accounts/{category}/') if f.endswith('.json')]

        # List to store account information
        accounts = []

        # Iterate through each JSON file
        for json_file in json_files:
            # Read the contents of the JSON file
            with open(f'accounts/{category}/{json_file}', 'r') as file:
                try:
                    # Attempt to load JSON content
                    account_info = json.load(file)
                    # Append the account information to the list
                    accounts.append(account_info)
                except json.decoder.JSONDecodeError as e:
                    # Handle JSON decoding error (e.g., empty file or invalid JSON)
                    print(f"Error decoding {json_file}: {e}")
                    continue

        # Sort the list of accounts based on followers
        accounts = sort_accounts(accounts, 'Followers')

        # Write the HTML header for each category
        html_content += f'<h1 onclick="toggleVisibility(\'{category}\')">{category}</h1>\n'

        # Write the category chart container
        html_content += f'<div id="chart-container-{category}" class="{category}"></div>\n'

        # Iterate through each account in the sorted list
        for account_info in accounts:
            
            # Get the account ID
            account_id = account_info["Account ID"]

            # Get the account header image URL
            header_image_url = account_info.get("Header", "")

            # Write a div for each account with class as the category
            html_content += f'<div class="accountInfo {category}" style="display:none;">\n'

            # Write a div for the account facts
            html_content += '<div class="accountFacts">'

            # Display the avatar using img tag
            html_content += f'<img src="{account_info["Avatar"]}" alt="Avatar" style="max-width: 100px; max-height: 100px;">\n'

            # Write the account name as a header
            tempUrl = meUrl+'/@'+ account_info["Account Name"] + account_info["Instance"]
            html_content += f'<h2><a href="{tempUrl}" target="_blank" rel="noopener noreferrer">{account_info["Display Name"]}</a></h2>\n'

            # Display note
            html_content += f'<p>{account_info["Note"]}</p>\n'

            # Open account ul
            html_content += '<ul class="stats">\n'

            # Write the rest of the account information
            for key, value in account_info.items():
                if key not in ["Account Name", "Avatar", "Header", "TootsList", "Account URL", "Display Name", "Instance", "Account ID", "Created", "Last Active", "Note"]:
                    html_content += f'<ii><strong>{key}</strong> {value}</li>\n'

            for toot in account_info["TootsList"]:
                # Get the toot ID
                toot_id = toot["id"]

                # Get the toot date
                toot_date = toot["created_at"]

                # Get the toot URL
                toot_url = toot["url"]

                # Get the toot content
                toot_content = toot["content"]

                # Get the toot media attachments
                toot_media_attachments = toot["media_attachments"]
                
                if toot["reblog"] is not None:
                    toot_content = toot["reblog"].get("content", "No content")
                    toot_media_attachments = toot["reblog"].get("media_attachments", "")
                    toot_url = toot["reblog"].get("url", "")

                # Get the toot replies count
                toot_replies_count = toot["replies_count"]

                # Get the toot reblogs count
                toot_reblogs_count = toot["reblogs_count"]

                # Get the toot favourites count
                toot_favourites_count = toot["favourites_count"]

                # Write the toot date
                html_content += f'<p class="tootDate">{toot_date}</p>\n'

                # Write the toot content
                html_content += f'<div class="toot" id="{toot_id}">\n'

                # Write the toot content
                html_content += f'{toot_content}'

                # Write the toot URL if not none
                if toot_url is not None:
                    html_content += f'<p class="tootUrl"><a href="{toot_url}" target="_blank" rel="noopener noreferrer">View on Mastodon</a></p>\n'

                # Write the toot media attachments
                if len(toot_media_attachments) > 0:
                    for media_attachment in toot_media_attachments:
                        html_content += f'<img src="{media_attachment["preview_url"]}" alt="Media Attachment">\n'

                # Write the toot counts
                html_content += f'<p class="tootCounts">Replies: {toot_replies_count} | Reblogs: {toot_reblogs_count} | Favourites: {toot_favourites_count}</p>\n'

                # Close the toot div
                html_content += '</div>\n'

            # Close account ul
            html_content += '</ul>\n'      

            # Close the accountFacts div
            html_content += '</div>\n'

            # Close the accountInfo div
            html_content += '</div>\n'

    # Close the grid wrapper
    html_content += '</div>\n'

    # Return the HTML content
    return html_content

# Function to generate the footer
def generateHTMLFooter():
    html_footer = ("""
            <script>
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

                
            </script>
        </body>
    </html>
    """)
    return html_footer

# Function to generate CSS file
def generateCSSFile(output_file='public/style.css'):
    try:
        css_content = """
        :root { --primary-color: #6364FF;
                --secondary-color: #ffffff;}
        body { font-family: sans-serif; background-color: #191b22; }
        h1 { color: #ffffff; background-color: var(--primary-color); padding: 2.1rem; cursor: pointer; }
        h2, { color: var(--secondary-color); 
                font-size: 1.4em;
                margin-block-start: 0em;
                margin-block-end: 0em;
                margin-inline-start: 0px;
                margin-inline-end: 0px;
                font-weight: 420;}
        p { color: var(--secondary-color); text-align: start; }
        a, a:hover, a:visited, a:active, a:focus, a:link { color: var(--secondary-color); }
        ul { list-style-type: none; padding: 0; color: var(--secondary-color); }
        .accountInfo { background-color: #282c37; padding: 10px; margin-bottom: 10px; }
        .accountFacts { background: rgba(25, 27, 34, 0.7); padding: 10px; border-radius: 2vh;
                        min-width: 320px; }
        .grid { display: unset;}
        .toots-content { background: rgba(25, 27, 34, 0.7); padding: 10px; }
        .toots-toggle { cursor: pointer; color: var(--secondary-color); 
                        background-color: var(--primary-color); padding: 0.7rem;
                        text-align: right; }
        .toot { background-color: #191b22; padding: 10px; 
                margin-bottom: 10px; border-radius: 1vh; max-width:91vw;
                margin-top: -6.3vh;}
        .toot img { border-radius: 1vh; 
                    float: none;
                    display: block; margin-left: auto; margin-right: auto; 
                    max-width: 100%; 
                    max-height: 100%; }
        .tootDate { background: var(--primary-color); color:var(--secondary-color); padding: 10px; 
                    margin-bottom: 10px; 
                    font-size: 0.7rem; 
                    border-radius: 1vh;}
        .tootUrl { color: var(--secondary-color); padding: 10px; margin-bottom: 10px; font-size: 0.7rem; }
        .tootCounts {color: var(--secondary-color); padding: 10px; margin-bottom: 10px; font-size: 0.7rem; }
        .stats { display: flex; flex-wrap: wrap; }
        hr { border: 0; height: 1px; background: #6364FF; }
        .chart { width: 100%; height: 42% !important; }
        img { border-radius: 50%;}
        /* Dark Violet Scrollbar Styles */
        ::-webkit-scrollbar { width: 12px; display: none; }
        ::-webkit-scrollbar-thumb { background-color: #4B0082; border-radius: 6px; }
        ::-webkit-scrollbar-track, ::-webkit-scrollbar-corner { background-color: #1E1E1E; }
        ::-webkit-scrollbar-thumb:hover { background-color: #6A5ACD; }
        """

        # Foreach key in data
        for key in data:
            css_content += f".{key} {{ min-height: 42vh;  }}\n"

        with open(output_file, 'w') as css_file:
            css_file.write(css_content)

        print(f'CSS file generated in {output_file}')
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")

# Function to generate index.html from the account_overview.html
def generateIndexFile():
    try:
        # Create the 'public/' directory if it doesn't exist
        public_directory = 'public/'
        if not os.path.exists(public_directory):
            os.makedirs(public_directory)

        # Create CSS file
        generateCSSFile()

        # Define the output HTML file
        output_file = 'public/index.html'

        # Open the HTML file for writing
        with open(output_file, 'w', encoding='utf-8') as html_file:
            # Write the components to the HTML file
            html_header = generateHTMLHeader()
            html_file.write(html_header)
            html_accountOverview = generateAccountOverview()
            html_file.write(html_accountOverview)
            html_footer = generateHTMLFooter()
            html_file.write(html_footer)

        print(f'index.html generated in {output_file}')
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")

# Function to start the worker threads
def worker(mastodon, on=True):
    try:
        while True:
            # Create a list of threads
            threads = []

            if on:
                # # Iterate through each category and start a thread for each
                for category, urls in data.items():
                    # Create account gathering thread for each category
                    accountInfos = Thread(target=saveAccountInfoToJSON, args=(mastodon, category, urls))
                    threads.append(accountInfos)

            # Thread for generating index.html
            if not on:
                indexFile = Thread(target=generateIndexFile)
                threads.append(indexFile)
            
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

    # Enable tracemalloc
    tracemalloc.start()

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

    # Start Worker
    worker(mastodon)

if __name__ == '__main__':
    main()
input()