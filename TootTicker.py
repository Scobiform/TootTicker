# TootTicker - boost your media and journalists
from mastodon import Mastodon
import json
import time

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

def retweet_from_all_accounts():
    for url in mastodon_urls:
        try:
            # Resolve the profile URL to get the account details
            account = mastodon.account_search(url)

            if account:
                user_id = account[0]['id']

                # Get recent toots from the user's timeline
                toots = mastodon.account_statuses(user_id, limit=5)

                # Print account information from the mastodon user
                print(f"Retweeting from {account[0]['username']}")
                print(f"Account URL: {account[0]['url']}")
                print(f"Account ID: {user_id}")
                # Print Followers and Following
                print(f"Followers: {account[0]['followers_count']}")
                print(f"Following: {account[0]['following_count']}")
                # Print the number of toots
                print(f"Toots: {account[0]['statuses_count']}")
                print(f"Created: {account[0]['created_at']}")
                print(f"Last Active: {account[0]['last_status_at']}")
                print(f"Last Status: {account[0]['last_status']}")
                print(f"Bot: {account[0]['bot']}")
                print(f"Avatar: {account[0]['avatar']}")
                print(f"Header: {account[0]['header']}")
                print(f"Emoji: {account[0]['emojis']}")
                print(f"Fields: {account[0]['fields']}")
                print(f"Moved: {account[0]['moved']}")
                print(f"Move: {account[0]['move']}")
                print(f"Moved To: {account[0]['moved_to']}")
                print(f"Follow Requests: {account[0]['follow_requests_count']}")
                print(f"Notifications: {account[0]['notifications']}")
                print(f"Username: {account[0]['username']}")
                print(f"Display Name: {account[0]['display_name']}")
                print(f"Header Static: {account[0]['header_static']}")
                print(f"Avatar Static: {account[0]['avatar_static']}")
                print(f"Acct: {account[0]['acct']}")
                print(f"URLs: {account[0]['urls']}")
                print(f"Stats: {account[0]['stats']}")

        except Exception as e:
            print(f"Error processing {url}: {e}")

def main():
    # Who Am I
    print(mastodon.me().username)

if __name__ == '__main__':
    retweet_from_all_accounts()
