class Logger:
    _instance = None
    _gui_callback = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_gui_callback(cls, callback):
        cls._gui_callback = callback

    def log(self, message: str):
        """Log a message to the GUI if callback is set, otherwise print to console"""
        if self._gui_callback:
            self._gui_callback(message)
        else:
            print(message)

# Create a global logger instance
logger = Logger.get_instance()
