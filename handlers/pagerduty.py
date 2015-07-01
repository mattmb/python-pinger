from handlers import Handler
import pygerduty


class PDHandler(Handler):
    def __init__(self, plugin, service_key, org):
        super(PDHandler, self).__init__()
        self.service_key = service_key
        self.pager = pygerduty.PagerDuty(org, service_key)

    def down_alert(self, url, message, details):
        self.pager.trigger_incident(self.service_key, message,
                                    url, details)

    def up_alert(self, url, message):
        self.pager.resolve_incident(self.service_key, url, message)
