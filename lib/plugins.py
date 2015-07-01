class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        """Called when a Plugin derived class is imported"""
 
        if not hasattr(cls, 'plugins'):
            # Called when the metaclass is first instantiated
            cls.plugins = {}
        else:
            # Called when a plugin class is imported
            cls.register_plugin(cls, attrs)
 
    def register_plugin(cls, plugin, attrs):
        """Add the plugin to the plugin list and perform any registration logic"""
 
        # create a plugin instance and store it
        # optionally you could just store the plugin class and lazily instantiate
        #instance = plugin()
 
        # save the plugin reference
        cls.plugins[attrs['__module__'].split('.')[1]] = plugin
 
        ## apply plugin logic - in this case connect the plugin to blinker signals
        ## this must be defined in the derived class
        #instance.__init__()
