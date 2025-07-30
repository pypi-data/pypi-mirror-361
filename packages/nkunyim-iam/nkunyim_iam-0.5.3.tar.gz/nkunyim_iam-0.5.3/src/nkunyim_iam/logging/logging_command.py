from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.http.http_client import HttpClient


class LoggingCommand:
    
    def __init__(self, req: HttpRequest) -> None:
        self.client = HttpClient(req=req, name=settings.LOGGING_SERVICE)
        super().__init__()
        
        
    def send(self, typ: str, data: dict) -> None:
        self.client.post(path=f"/api/{str(data[typ]).lower()}_logs/", data=data)
       