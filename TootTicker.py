import tracemalloc
from mastodon import Mastodon
import os
import json
import time
from threading import Thread

# TootTicker - boost your media and journalists
# Gathering account informations from Mastodon and make them available as pure json files
# GPLv3 - 2023 - by scobiform.com
# github.com/Scobiform/TootTicker

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
    media = data['Media']
    creators = data['Creator']
    government = data['Government']
    NGO = data['NGO']

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
            toots = mastodon.account_statuses(user_id, limit=7)

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
                "Header": account[0]['header'],
                "Toots": toots
            }

            # Save the JSON file to the folder
            with open(os.path.join(accounts_directory, f"{user_id}.json"), 'w') as file:
                json.dump(account_info, file, indent=4, default=str)
            print(f"Saved account info for {account[0]['username']}")

            # Sleep for 2.1 seconds to avoid rate limiting
            time.sleep(2.1)

        except Exception as e:
            print(f"Error processing {url}: {e}")

# Function to generate HTML overview
def generateHTMLOverview():
    # Function to generate HTML overview

    def sort_accounts(accounts, key):
        # Helper function to sort accounts based on a given key
        return sorted(accounts, key=lambda x: x[key], reverse=True)

    # Create the 'public/' directory if it doesn't exist
    public_directory = 'public/'
    if not os.path.exists(public_directory):
        os.makedirs(public_directory)

    # Create CSS file
    generateCSSFile()

    # Define the output HTML file
    output_file = 'public/account_overview.html'

    # Open the HTML file for writing
    with open(output_file, 'w') as html_file:
        # Write the HTML header
        html_file.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n')
        html_file.write('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
        html_file.write(f'<link rel="stylesheet" href="account_overview.css">\n')
        html_file.write('<title>TootTicker - boost your media and journalists</title>\n</head>\n<body>\n')

        # Write a grid wrapper
        html_file.write('<div class="grid">\n')

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

            # Sort the list of accounts based on followers (you can replace this with other keys)
            accounts = sort_accounts(accounts, 'Followers')

            # Write the HTML header for each category
            html_file.write(f'<h1>{category} Accounts</h1>\n')

            # Iterate through each account in the sorted list
            for account_info in accounts:
                # Write a div for each account
                html_file.write('<div class="accountInfo">\n')

                # Write the account name as a header
                html_file.write(f'<h2>{account_info["Account Name"]}</h2>\n')

                # Display the avatar and header using img tags
                html_file.write(f'<img src="{account_info["Avatar"]}" alt="Avatar" style="max-width: 100px; max-height: 100px;">\n')

                # Write the rest of the account information
                for key, value in account_info.items():
                    if key not in ["Account Name", "Avatar", "Header", "Toots"]:
                        html_file.write(f'<p><strong>{key}:</strong> {value}</p>\n')

                # Write the toots
                for toot in account_info['Toots']:
                    html_file.write('<a href="'+str(toot["url"])+'" target="_blank"></a>')

                # Close the div
                html_file.write('</div>\n')

        # Close the grid wrapper
        html_file.write('</div>\n')

        # Write the HTML footer
        html_file.write('</body>\n</html>')

    print(f'HTML overview generated in {output_file}')


# Generate CSS file
def generateCSSFile():
    # Define the output CSS file
    output_file = 'public/account_overview.css'

    # Open the CSS file for writing
    with open(output_file, 'w') as css_file:
        # Write the CSS header
        css_file.write('body { font-family: sans-serif; background-color: #191b22; }\n')
        css_file.write('h2 { color: #d9e1e8; }\n')
        css_file.write('p { color: #d9e1e8; }\n')
        css_file.write('.accountInfo { background-color: #282c37; padding: 10px; margin-bottom: 10px; }\n')
        css_file.write('.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); grid-gap: 10px; }\n')

        # Add styles for the dark violet scrollbar
        css_file.write('/* Dark Violet Scrollbar Styles */\n')
        css_file.write('::-webkit-scrollbar {\n')
        css_file.write('  width: 12px;\n')
        css_file.write('}\n')
        css_file.write('::-webkit-scrollbar-thumb {\n')
        css_file.write('  background-color: #4B0082; /* Dark violet color */\n')
        css_file.write('  border-radius: 6px;\n')
        css_file.write('}\n')
        css_file.write('::-webkit-scrollbar-track {\n')
        css_file.write('  background-color: #1E1E1E; /* Dark background color */\n')
        css_file.write('}\n')
        css_file.write('::-webkit-scrollbar-corner {\n')
        css_file.write('  background-color: #1E1E1E; /* Dark background color */\n')
        css_file.write('}\n')
        css_file.write('::-webkit-scrollbar-thumb:hover {\n')
        css_file.write('  background-color: #6A5ACD; /* A lighter violet color on hover */\n')
        css_file.write('}\n')

    print(f'CSS file generated in {output_file}')
 
# Function to start the worker
def worker(mastodon):
    try:
        while True:
            # Create a list of threads
            threads = []

            # Iterate through each category and start a thread for each
            for category, urls in data.items():
                # Create account gathering thread for each category
                accountInfos = Thread(target=saveAccountInfoToJSON, args=(mastodon, category, urls))
                threads.append(accountInfos)
            
            # Create HTML overview thread
            htmlOverview = Thread(target=generateHTMLOverview)
            threads.append(htmlOverview)

            # Start all threads
            for thread in threads:
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Sleep for a period before restarting the process
            print("Sleeping for 60 seconds...")
            time.sleep(60)  # Sleep for 10 minutes (adjust as needed)
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