from typing import Union
from uuid import uuid4

from django.conf import settings
from django.http import HttpRequest

from nkunyim_iam.dtos.client_model import ClientModel
from nkunyim_iam.dtos.location_model import LocationModel
from nkunyim_iam.dtos.user_agent_model import UserAgentModel
from nkunyim_iam.dtos.nation_model import NationModel

from nkunyim_iam.services.client_service import ClientService
from nkunyim_iam.services.location_service import LocationService
from nkunyim_iam.services.nation_service import NationService
from nkunyim_iam.services.user_agent_service import UserAgentService

from nkunyim_iam.http.http_session import HttpSession


class HttpContext:
    def __init__(self, req: HttpRequest) -> None:
        self._req = req
        self._session = HttpSession(req=req)

        self._app = {}
        self._role: Union[dict, None] = None
        self._business: Union[dict, None] = None
        self._user: Union[dict, None] = self._session.get_user()
        self._page: Union[dict, None] = None
        self._pages: Union[dict, None] = None
        self._navs: Union[list[dict], None] = None

    def create(self) -> None:
        env = settings.NKUNYIM_ENV
        path = self._req.path.lower()
        paths = path.strip('/').split('/') if path.strip('/') else ['/']
        node = paths[-1] if paths else "index"

        self._page = {
            "path": path,
            "paths": paths,
            "node": node,
            "name": f"{node.title()}Page"
        }

        pages = dict(settings.NKUNYIM_PAGES)
        navs, menu_groups = [], {"toolbox": [], "manage": [], "system": []}

        account = self._session.get_account()
        user = self._user
        menus = account.get("menus", []) if account else []
        role = account.get("role") if account else None
        business = account.get("business") if account else None

        if user and user.get("is_superuser"):
            menus.append({
                "id": str(uuid4()),
                "node": "system",
                "module": {
                    "id": str(uuid4()),
                    "name": "Xvix",
                    "title": "AutoFix",
                    "caption": "Manage auto-fix data",
                    "icon": "mdi mdi-auto-fix",
                    "path": "xvix",
                    "route": "#xvix",
                },
                "items": [],
                "is_active": True
            })

        for menu in menus:
            node = menu.get("node")
            module = menu.get("module", {})
            items = menu.get("items", [])

            if node in menu_groups:
                menu_groups[node].append(menu)

            mod_name = module.get("name", "")
            mod_path = module.get("path", "")
            if mod_name and mod_path:
                page_key = f"{mod_name.title()}Page"
                page_val = f"./{mod_path.lower()}/home.{env}"
                pages[page_key] = page_val

            for item in items:
                page_info = item.get("page", {})
                item_name = page_info.get("name", "")
                item_path = page_info.get("path", "")
                if item_name and item_path:
                    item_key = f"{mod_name.title()}{item_name.title()}Page"
                    item_val = f"./{mod_path.lower()}/{item_path.lower()}.{env}"
                    pages[item_key] = item_val

        for group_name, group_menus in menu_groups.items():
            if group_menus:
                navs.append({"name": group_name.title(), "menus": group_menus})

        self._pages = pages
        self._navs = navs
        if user and user.get("username") and self._session.get_subdomain() == "app":
            self._role = role
            self._business = business

    @property
    def app(self) -> ClientModel:
        return ClientService(req=self._req, sess=self._session).get()

    @property
    def role(self) -> Union[dict, None]:
        return self._role

    @property
    def business(self) -> Union[dict, None]:
        return self._business

    @property
    def user(self) -> Union[dict, None]:
        return self._user

    @property
    def page(self) -> Union[dict, None]:
        return self._page

    @property
    def pages(self) -> Union[dict, None]:
        return self._pages

    @property
    def navs(self) -> Union[list[dict], None]:
        return self._navs

    @property
    def user_agent(self) -> UserAgentModel:
        return UserAgentService(req=self._req, sess=self._session).get()

    @property
    def location(self) -> LocationModel:
        return LocationService(req=self._req, sess=self._session).get()

    @property
    def nation(self) -> NationModel:
        loc = self.location
        return NationService(req=self._req, sess=self._session).get(code=loc.country_code.upper())

    @property
    def data(self) -> dict:
        exclude_keys = {
            'aes_key', 'rsa_public_pem', 'rsa_private_pem', 'rsa_passphrase',
            'algorithm', 'client_secret', 'grant_type', 'response_type', 'scope'
        }

        app_data = {k: v for k, v in (self.app.data or {}).items() if k not in exclude_keys}

        return {
            **app_data,
            "page": self.page,
            "pages": self.pages,
            "navs": self.navs,
            "user": self.user,
            "role": self.role,
            "business": self.business,
            "user_agent": self.user_agent.data,
            "location": self.location.data,
            "nation": self.nation.data,
        }

    @property
    def root(self) -> str:
        return self._session.get_subdomain()
