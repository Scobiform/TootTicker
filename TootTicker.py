import tracemalloc
from mastodon import Mastodon
import os
import json
import time
from threading import Thread

# TootTicker - boost your bubble
# Gathering account informations from Mastodon and make them available as pure json files
# GPLv3 - 2023 - by scobiform.com
# github.com/Scobiform/TootTicker

# THe following libraries are used in this project:
# Mastodon.py - GNU Affero General Public License v3.0
# Chart.js - MIT License - https://www.chartjs.org/

# Create Mastodon app and get user credentials
def create_secrets():
    # Replace the following placeholders with your actual values
    app_name = 'TootTicker - boost your media and journalists'  # Replace with your desired app name
    instance_url = 'https://mastodon.social/'  # Replace with your Mastodon instance URL
    email = 'your@mail.com'  # Replace with your Mastodon account email
    password = 'yourPassword'  # Replace with your Mastodon account password

    # Create Mastodon app (client credentials)
    Mastodon.create_app(
        app_name,
        api_base_url=instance_url,
        to_file='clientcred.secret'
    )

    # Fill in your credentials - RUN ONCE
    mastodon = Mastodon(client_id='clientcred.secret')
    mastodon.log_in(
        email,
        password,
        to_file='usercred.secret'
    )

#ToDo: Check for first run and create secrets
# Call the create_secrets function to generate credentials
# --- Uncomment the following line to generate credentials ---
#create_secrets()

# Load Mastodon URLs from the provided JSON
with open('mastodon_urls.json', 'r') as file:
    data = json.load(file)

# Create Mastodon API instance
mastodon = Mastodon(access_token='usercred.secret')

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
            toots = mastodon.account_statuses(user_id)

            # Create a dictionary with account information
            account_info = {
                "Account Name": account[0]['username'],
                "Account URL": account[0]['url'],
                "Display Name": account[0]['display_name'],
                "Instance": '@' + account[0]['url'].split('https://')[1].split('/')[0],
                "Account ID": user_id,
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
    <div id="charts-container"></div>
    """
    return html_header

    sideMenu = """
    <div id="sideMenu">
        <div id="blog">
            <a href="" target="_blank" rel="noopener noreferrer">Blog</a>
        </div>
        <div id="about">
            <a href="" target="_blank" rel="noopener noreferrer">About</a>
        </div>
        <div id="contact">
            <a href="" target="_blank" rel="noopener noreferrer">Contact</a>
        </div>
        <div id="donate">
            <a href="" target="_blank" rel="noopener noreferrer">Donate</a>
        </div>
        <div id="settings">
            <a href="" target="_blank" rel="noopener noreferrer">Settings</a>
        </div>
        <div id="search">
            <input type="text" id="search" name="search" placeholder="Search">
        </div>
    </div>
    """
    return sideMenu

# Function to generate the Chart.js data object
def generateChart():
    categories = ['Media', 'Creator', 'Government', 'NGO']
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
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    with open(f'public/data-{timestamp}.json', 'w') as file:
        file.write(js_data_object)

    # Return the JavaScript object notation
    return js_data_object

def compare_data():
    data_files = sorted([f for f in os.listdir('public') if f.startswith('data-') and f.endswith('.json')])
    if len(data_files) < 2:
        print("Not enough data to compare.")
        return

    # Load data from the two most recent files
    with open(f'public/{data_files[-2]}', 'r') as file:
        previous_data = json.load(file)
    
    with open(f'public/{data_files[-1]}', 'r') as file:
        latest_data = json.load(file)

    # Calculate the increase for each account in each category
    increase_data = {}
    for category in latest_data:
        increase_data[category] = {}
        for account, followers in latest_data[category].items():
            previous_followers = previous_data[category].get(account, 0)
            increase_data[category][account] = followers - previous_followers

    return increase_data

# Function to generate HTML overview
def generateAccountOverview():

    # Get the current instance URL
    meUrl = 'https://'+mastodon.me().url.split("https://")[1].split("/")[0]

    # Function to sort accounts based on a given key
    def sort_accounts(accounts, key):
        # Helper function to sort accounts based on a given key
        return sorted(accounts, key=lambda x: x[key], reverse=True)

    html_content = '<div class="grid">\n'

    # Categories to iterate through
    categories = ['Media', 'Creator', 'Government', 'NGO']

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
            html_content += f'<div class="accountInfo {category}" style="background-image: url(\'{header_image_url}\'); display:none;">\n'

            # Write a div for the account facts
            html_content += '<div class="accountFacts">'

            # Write the account name as a header
            tempUrl = meUrl+'/@'+ account_info["Account Name"] + account_info["Instance"]
            html_content += f'<h2><a href="{tempUrl}" target="_blank" rel="noopener noreferrer">{account_info["Display Name"]}</a></h2>\n'

            # Display the avatar using img tag
            html_content += f'<img src="{account_info["Avatar"]}" alt="Avatar" style="max-width: 100px; max-height: 100px;">\n'

            # Write the rest of the account information
            for key, value in account_info.items():
                if key not in ["Account Name", "Avatar", "Header", "TootsList", "Account URL", "Display Name", "Instance", "Account ID"]:
                    html_content += f'<p><strong>{key}:</strong> {value}</p>\n'

            # Write the Toots header
            #html_content += f'<h3 class="toots-toggle" onclick="toggleToots(\'toots-{account_id}\')">Toots</h3>\n'

            # # Write the Toots in a separate div
            # html_content += f'<div class="toots" id="toots-{account_id}" style="display:none;">\n'
            # if "Toots" in account_info:
            #     for toot in account_info["Toots"]:
            #         # Assuming 'Toot' is a dictionary and contains text in a 'content' key
            #         toot_content = toot.get("content", "No content")
            #         toot_url = toot.get("url", "")
            #         toot_created_at = toot.get("created_at", "")
            #         toot_replies_count = toot.get("replies_count", "")
            #         toot_reblogs_count = toot.get("reblogs_count", "")
            #         toot_favourites_count = toot.get("favourites_count", "")

            #             # Write the toot created at
            #         html_content += f'<div class="tootDate"><strong>Created At:</strong> <a href="{toot_url}" target="_blank" rel="noopener norefrrer">{toot_created_at}</a></div>\n'
            #         # Write the toot content
            #         html_content += f'<div class="toot">{toot_content}</div>\n'
            #         # Write the toot replies count
            #         html_content += f'<div class="tootCounts"><strong>Replies:</strong> {toot_replies_count} <strong>Reblogs:</strong> {toot_reblogs_count} <strong>Favourites:</strong> {toot_favourites_count}</div>\n'
            #         # Write a horizontal rule
            #         html_content += ('<hr>\n')
            # else:
            #     html_content += '<p>No toots found.</p>\n'

            html_content += '</div>\n'  # Close the toots div

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
                        borderColor: 'rgba(0, 123, 255, 1)',
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
                const r = Math.floor(Math.random() * 255);
                const g = Math.floor(Math.random() * 255);
                const b = Math.floor(Math.random() * 255);
                return `rgba(${r}, ${g}, ${b}, 0.5)`;
            }

        </script>
    """)
    return html_footer

# Function to generate CSS file
def generateCSSFile(output_file='public/style.css'):
    try:
        css_content = """
        body { font-family: sans-serif; background-color: #191b22; }
        h1 { color: #d9e1e8; background-color: #6364FF; padding: 2.1rem; cursor: pointer; }
        h2, p, a { color: #d9e1e8; }
        a:hover, a:visited, a:active, a:focus, a:link { color: #ff64FF; }
        .accountInfo { background-color: #282c37; padding: 10px; margin-bottom: 10px; }
        .accountFacts { background: rgba(25, 27, 34, 0.7); padding: 10px; min-width: px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(1fr)); grid-gap: 10px; }
        .toots-content { background: rgba(25, 27, 34, 0.7); padding: 10px; }
        .toots-toggle { cursor: pointer; color: #d9e1e8; background-color: #6364FF; padding: 0.7rem; }
        .toot { background-color: #282c37; padding: 10px; margin-bottom: 10px; }
        .tootDate { color:#ff64FF; padding: 10px; margin-bottom: 10px; font-size: 0.7rem; float: right;}
        .tootUrl { color: #ff64FF; padding: 10px; margin-bottom: 10px; font-size: 0.7rem; }
        .tootCounts {color: #ff64FF; padding: 10px; margin-bottom: 10px; font-size: 0.7rem; }
        hr { border: 0; height: 1px; background: #6364FF; }
        /* Dark Violet Scrollbar Styles */
        ::-webkit-scrollbar { width: 12px; display: none; }
        ::-webkit-scrollbar-thumb { background-color: #4B0082; border-radius: 6px; }
        ::-webkit-scrollbar-track, ::-webkit-scrollbar-corner { background-color: #1E1E1E; }
        ::-webkit-scrollbar-thumb:hover { background-color: #6A5ACD; }
        """

        with open(output_file, 'w') as css_file:
            css_file.write(css_content)

        print(f'CSS file generated in {output_file}')
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")

# function to get String from html file
def getHTMLStringFromFile(file):
    with open(file, 'r', encoding='utf-8') as file:
        return file.read()

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

# Function to start the worker
def worker(mastodon):
    try:
        while True:
            # Create a list of threads
            threads = []

            # Iterate through each category and start a thread for each
            # for category, urls in data.items():
            #     # Create account gathering thread for each category
            #     accountInfos = Thread(target=saveAccountInfoToJSON, args=(mastodon, category, urls))
            #     threads.append(accountInfos)
            
            # Create HTML overview thread
            htmlOverview = Thread(target=generateAccountOverview)
            threads.append(htmlOverview)

            # Create index.html thread
            indexFile = Thread(target=generateIndexFile)
            threads.append(indexFile)

            # Start all threads
            for thread in threads:
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Sleep for a period before restarting the process
            print("Sleeping for 420 seconds...")
            time.sleep(420)  # Sleep for 420 seconds (adjust as needed)
            print("Restarting...")

    except Exception as errorcode:
        print("ERROR: " + str(errorcode))

# Main function
def main():

    # Enable tracemalloc
    tracemalloc.start()
    
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