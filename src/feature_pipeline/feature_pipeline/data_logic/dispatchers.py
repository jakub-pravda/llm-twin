from loguru import logger


class DebugDispatcher:
    
    @staticmethod
    def debug_message(message):
        logger.debug("Message from dispatcher: {}", message)
        return message