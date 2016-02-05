from handlers import Handler
from slacker import Slacker


class SlackHandler(Handler):
    def __init__(self, plugin, service_key, channel):
        super(SlackHandler, self).__init__()
        self.service_key = service_key
        self.channel = channel
        self.slack = Slacker(self.service_key)

    def down_alert(self, url, message, details):
        self.slack.chat.post_message(self.channel, text=message,
                                     username='PyPinger', icon_emoji=':pager:')
        self.slack.chat.post_message(self.channel, text=details,
                                     username='PyPinger', icon_emoji=':pager:')

    def up_alert(self, url, message):
        self.slack.chat.post_message(self.channel, text=message,
                                     username='PyPinger', icon_emoji=':pager:')
