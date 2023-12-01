from mastodon import Mastodon
import json
import time

# TootTicker - boost your media and journalists
# This script will fetch the account information from the provided Mastodon URLs
# and save the information to a JSON file

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

def get_account_infos():
    account_info_list = []  # List to store account information

    for url in mastodon_urls:
        try:
            # Resolve the profile URL to get the account details
            account = mastodon.account_search(url)

            if account:
                user_id = account[0]['id']

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
                for key, value in account_info.items():
                    print(f"{key}: {value}")

                # Append the account_info dictionary to the list
                account_info_list.append(account_info)

                # Rate limiting
                #time.sleep(5)

        except Exception as e:
            print(f"Error processing {url}: {e}")

    # Save the account information to a JSON file
    with open('account_info.json', 'w') as json_file:
        json.dump(account_info_list, json_file, indent=2)

def main():
    # Who Am I
    print(mastodon.me().username)

if __name__ == '__main__':
    get_account_infos()
