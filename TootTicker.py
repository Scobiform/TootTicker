import tracemalloc
from mastodon import Mastodon
import os
import json
import time
from threading import Thread

# TootTicker - boost your media and journalists
# Gathering account informations from Mastodon and make them available as pure json files

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

# Load Mastodon URLs from the provided JSON
with open('mastodon_urls.json', 'r') as file:
    data = json.load(file)
    mastodon_urls = data['urls']

# Call the create_secrets function to generate credentials
# --- Uncomment the following line to generate credentials ---
#create_secrets()

# Create Mastodon API instance
mastodon = Mastodon(access_token='usercred.secret')

import os

def get_account_infos(mastodon):
    for url in mastodon_urls:
        try:
            # Resolve the profile URL to get the account details
            account = mastodon.account_search(url)
            
            if account:
                user_id = account[0]['id']

                # Create the 'accounts/' directory if it doesn't exist
                accounts_directory = 'accounts/'
                if not os.path.exists(accounts_directory):
                    os.makedirs(accounts_directory)

                # Get recent toots from the user's timeline
                toots = mastodon.account_statuses(user_id, limit=5)

                # Create a dictionary with account information
                account_info = {
                    "Account Name": account[0]['username'],
                    "Account URL": account[0]['url'],
                    "Account ID": user_id,
                    "Followers": account[0]['followers_count'],
                    "Following": account[0]['following_count'],
                    "Toots": account[0]['statuses_count'],
                    "Created": account[0]['created_at'],
                    "Last Active": account[0]['last_status_at'],
                    "Bot": account[0]['bot'],
                    "Avatar": account[0]['avatar'],
                    "Header": account[0]['header']
                }

                # Print account information from the mastodon user
                for key, value in account_info.items():
                    print(f"{key}: {value}")

                # Save the JSON file to the folder
                with open(os.path.join(accounts_directory, str(user_id) + '.json'), 'w') as file:
                    json.dump(account_info, file, indent=4, default=str)

        except Exception as e:
            print(f"Error processing {url}: {e}")

def generate_html_overview():
    # Define the output HTML file
    output_file = 'public/account_overview.html'

    # Get the list of JSON files in the 'accounts/' folder
    json_files = [f for f in os.listdir('accounts/') if f.endswith('.json')]

    # Open the HTML file for writing
    with open(output_file, 'w') as html_file:
        # Write the HTML header
        html_file.write('<html>\n<head>\n<title>Account Overview</title>\n</head>\n<body>\n')

        # Iterate through each JSON file
        for json_file in json_files:
            # Read the contents of the JSON file
            with open(f'accounts/{json_file}', 'r') as file:
                try:
                    # Attempt to load JSON content
                    account_info = json.load(file)
                except json.decoder.JSONDecodeError as e:
                    # Handle JSON decoding error (e.g., empty file or invalid JSON)
                    print(f"Error decoding {json_file}: {e}")
                    continue

            # Write a div for each JSON file
            html_file.write('<div style="border: 1px solid #ddd; padding: 10px; margin: 10px;">\n')
            
            # Write the account name as a header
            html_file.write(f'<h2>{account_info["Account Name"]}</h2>\n')

            # Display the avatar and header using img tags
            html_file.write(f'<img src="{account_info["Avatar"]}" alt="Avatar" style="max-width: 100px; max-height: 100px;">\n')
            html_file.write(f'<img src="{account_info["Header"]}" alt="Header" style="max-width: 300px; max-height: 150px;">\n')

            # Write the rest of the account information
            for key, value in account_info.items():
                if key not in ["Account Name", "Avatar", "Header"]:
                    html_file.write(f'<p><strong>{key}:</strong> {value}</p>\n')

            # Close the div
            html_file.write('</div>\n')

        # Write the HTML footer
        html_file.write('</body>\n</html>')

    print(f'HTML overview generated in {output_file}')

# Load the list of account IDs from the 'accounts/' folder
def getAccountIds():
    account_ids = []
    json_files = [f for f in os.listdir('accounts/') if f.endswith('.json')]
    for json_file in json_files:
        account_ids.append(json_file.replace('.json', ''))
    return account_ids

def stream_toots(mastodon):
    print("Starting stream...")
    # Load the list of account IDs
    account_ids = getAccountIds()

    # Print the list of account IDs
    #for account_id in account_ids:
    #    print(f"{account_id}")

# Callback function for handling incoming toots
def handle_toot(mastodon, toot, account_ids):
    try:
        if toot['account']['id'] in account_ids:
            # Retoot the toot if the account ID matches
            print(f"Retooting {toot['id']} from {toot['account']['username']}")
            mastodon.status_reblog(toot['id'])

    except Exception as e:
        print(f"Error processing toot: {e}")

def worker(mastodon):
    try:
        # Create the UI thread
        generateUI = Thread(target=generate_html_overview)

        # Create account gathering thread
        accountInfos = Thread(target=get_account_infos, args=(mastodon,))

        # Create the stream thread
        streamToots = Thread(target=stream_toots, args=(mastodon,))

        # Create a list of threads
        threads = []

        # Start the UI thread
        threads.append(generateUI)
        # Start the account gathering thread
        threads.append(accountInfos)
        # Start the stream thread
        threads.append(streamToots)

        # Start all threads
        for j in threads:
            j.start()

        # Wait for all threads to complete
        for j in threads:
            j.join()

    except Exception as errorcode:
        print("ERROR: " + str(errorcode))

def main():

    # Enable tracemalloc
    tracemalloc.start()
    
    # Authenticate the app
    global mastodon
    mastodon = Mastodon(access_token = 'usercred.secret')

    # Who Am I
    print(mastodon.me().username)

    # Start Worker
    worker(mastodon)

if __name__ == '__main__':
    main()
input()