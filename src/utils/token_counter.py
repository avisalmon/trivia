class TokenCounter:
    def __init__(self):
        self.tokens_sent = 0
        self.tokens_received = 0
        self._instance = None
    
    @classmethod
    def get_instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = TokenCounter()
        return cls._instance
    
    def add_tokens(self, sent: int, received: int):
        self.tokens_sent += sent
        self.tokens_received += received
    
    def get_counts(self) -> tuple:
        return self.tokens_sent, self.tokens_received
    
    def reset(self):
        self.tokens_sent = 0
        self.tokens_received = 0 