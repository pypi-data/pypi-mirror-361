from decimal import Decimal
from typing import Any, Optional
from uuid import UUID
from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.http.http_client import HttpClient

from .signals import nation_initialized


class NationModel(object):
    def __init__(self, req: HttpRequest, code: str) -> None:
        self._data = None
        client = HttpClient(req=req, name=settings.PLACE_SERVICE)
        response = client.get(path=f"/api/nations/?code={code.upper()}")
        
        if response.ok:
            json_data = response.json()
            self._data = (json_data.get("data") or [None])[0]

        nation_initialized.send(sender=self.__class__, instance=self)

    def _get(self, key: str, cast: Optional[Any] = None) -> Any:
        if not self._data or key not in self._data:
            return None
        value = self._data[key]
        if cast:
            try:
                return cast(value)
            except Exception:
                return None
        return value

    @property
    def id(self) -> UUID:
        return self._get("id", lambda v: UUID(str(v)))

    @property
    def code(self) -> str:
        return self._get("code", str)

    @property
    def name(self) -> str:
        return self._get("name", str)

    @property
    def phone(self) -> str:
        return self._get("phone", str)

    @property
    def capital(self) -> str:
        return self._get("capital", str)

    @property
    def languages(self) -> str:
        return self._get("languages", str)

    @property
    def north(self) -> Decimal:
        return self._get("north", lambda v: Decimal(str(v)))

    @property
    def south(self) -> Decimal:
        return self._get("south", lambda v: Decimal(str(v)))

    @property
    def east(self) -> Decimal:
        return self._get("east", lambda v: Decimal(str(v)))

    @property
    def west(self) -> Decimal:
        return self._get("west", lambda v: Decimal(str(v)))

    @property
    def flag(self) -> str:
        return self._get("flag", str)

    @property
    def flag_2x(self) -> str:
        return self._get("flag_2x", str)

    @property
    def flag_3x(self) -> str:
        return self._get("flag_3x", str)

    @property
    def flag_svg(self) -> str:
        return self._get("flag_svg", str)

    @property
    def is_active(self) -> bool:
        return self._get("is_active", bool)

    @property
    def continent_id(self) -> UUID:
        return self._get("continent", lambda v: UUID(str(v)))

    @property
    def currency_id(self) -> UUID:
        return self._get("currency", lambda v: UUID(str(v)))

    @property
    def data(self) -> Optional[dict]:
        return self._data
