

class SMSModel(object):
    
    def __init__(self, data: dict) -> None:
        self._phone = data['phone']
        self._message = data['message']
        
    @property
    def phone(self) -> str:
        return self._phone
    
    @property
    def message(self) -> str:
        return self._message