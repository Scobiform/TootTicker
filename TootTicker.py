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
    output_file = 'account_overview.html'

    # Get the list of JSON files in the 'accounts/' folder
    json_files = [f for f in os.listdir('accounts/') if f.endswith('.json')]

    # Open the HTML file for writing
    with open(output_file, 'w') as html_file:
        # Write the HTML header
        html_file.write('<html>\n<head>\n<title>Account Overview</title>\n</head>\n<body>\n')

        # Write the table header
        html_file.write('<table border="1">\n<tr>\n<th>File Name</th>\n<th>Contents</th>\n</tr>\n')

        # Iterate through each JSON file
        for json_file in json_files:
            # Read the contents of the JSON file
            with open(f'accounts/{json_file}', 'r') as file:
                try:
                    # Attempt to load JSON content
                    json_content = json.load(file)
                except json.decoder.JSONDecodeError as e:
                    # Handle JSON decoding error (e.g., empty file or invalid JSON)
                    print(f"Error decoding {json_file}: {e}")
                    continue

            # Write a table row with the file name and contents
            html_file.write(f'<tr>\n<td>{json_file}</td>\n<td><pre>{json.dumps(json_content, indent=2)}</pre></td>\n</tr>\n')

        # Write the HTML footer
        html_file.write('</table>\n</body>\n</html>')

    print(f'HTML overview generated in {output_file}')

def worker(mastodon):
    try:
        # Create the UI thread
        generateUI = Thread(target=generate_html_overview)

        # Create account gathering thread
        accountInfos = Thread(target=get_account_infos, args=(mastodon,))

        # Create a list of threads
        threads = []

        # Start the UI thread
        threads.append(generateUI)
        # Start the account gathering thread
        threads.append(accountInfos)

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