from mastodon import Mastodon
import json
import time

# TootTicker - boost your media and journalists
# This script will fetch the account information from the provided Mastodon URLs
# and save the information to a JSON file

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

def get_account_infos():
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
                    "Bot": account[0]['bot']
                }

                # Print account information from the mastodon user
                # Do not print if already in the list
                for key, value in account_info.items():
                    print(f"{key}: {value}")

                # Save the JSON file to the folder
                with open(os.path.join(accounts_directory, str(user_id) + '.json'), 'w') as file:
                    json.dump(account_info, file, indent=4, default=str)

                # Rate limiting
                time.sleep(2)

        except Exception as e:
            print(f"Error processing {url}: {e}")


def main():
    # Who Am I
    print(mastodon.me().username)

if __name__ == '__main__':
    get_account_infos()
