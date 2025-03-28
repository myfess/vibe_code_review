from typing import Callable, Optional

class Logger:
    _instance: Optional['Logger'] = None
    _gui_callback: Optional[Callable[[str], None]] = None

    @classmethod
    def get_instance(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_gui_callback(cls, callback: Callable[[str], None]) -> None:
        cls._gui_callback = callback

    def log(self, message: str) -> None:
        """Log a message to the GUI if callback is set, otherwise print to console"""
        if self._gui_callback and callable(self._gui_callback):
            self._gui_callback(message)
        else:
            print(message)

# Create a global logger instance
logger = Logger.get_instance()
