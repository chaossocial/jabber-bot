import time

from mastodon import Mastodon

mastodon = Mastodon(
    access_token = 'pytooter_usercred.secret',
    api_base_url = 'https://chaos.social'
)


def has_jabber_account(user):
    # As per https://wiki.archlinux.org/index.php/prosody#Listing_users
    user_list = subprocess.check_output(['ls', '-l', '/var/lib/prosody/*/accounts/*']).split('\n')
    return user.lower() in [u.lower() for u in user_list]


def create_jabber_account(user):
    password = subprocess.check_output(['pwgen', '-cny1', '32']).strip()
    user = subprocess.check_output(['prosodyctl', 'register', user, 'jabber.chaos.social', password])
    return password


def send_help(status):
    help_text = 'Hi! I am a helper bot for the chaos.social jabber server. If you want an account on our jabber server, message me with a message containing the word "register"!\n\nIf you have any questions, feel free to ask leah or rixx.'
    mastodon.status_reply(to_status=status['id'], help_text)


def parse_message(status):
    content = status['content']
    if 'register' in content.lower():
        return 'register'


def handle_notification(notification):
    if notification['type'] != 'mention':
        return
    status = notification['status']
    command = parse_message(status)
    if command != 'register':
        send_help(status)
        return
    if status['account']['username'] != status['account']['acct']:
        mastodon.status_reply(to_status=status['id'], 'Sorry, our Jabber accounts are only available to inhabitants of chaos.social.')
        return
    user = status['account']['username']
    if has_jabber_account(user):
        mastodon.status_reply(to_status=status['id'], '{}@jabber.chaos.social is already your registered jabber account – you can register only once.'.format(user))
        return
    password = create_jabber_account(user)
    mastodon.status_reply(to_status['id'], 'Your Jabber account has been created:\n\nUser: {user}@jabber.chaos.social\nPassword: {password}\n\nPlease change the password soon, using a client like Pidgin.', visibility='private')


if __name__ == '__main__':
    while True:
        try:
            for notification in mastodon.notifications():
                handle_notification(notification)
                mastodon.notifications_dismiss(notification['id'])
        except Exception as exc:
            print(exc)
        time.sleep(10)
