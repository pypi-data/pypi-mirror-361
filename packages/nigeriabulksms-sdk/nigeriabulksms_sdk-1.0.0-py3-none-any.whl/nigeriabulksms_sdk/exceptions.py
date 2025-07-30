
class NigeriaBulkSMSException(Exception):
    """Custom exception for NigeriaBulkSMS API errors."""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


