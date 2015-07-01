from handlers import Handler

class PDHandler(Handler):
    def __init__(self, **kwargs):
        super(PDHandler, self).__init__()
        for k, v in kwargs.items():
            print k, v
