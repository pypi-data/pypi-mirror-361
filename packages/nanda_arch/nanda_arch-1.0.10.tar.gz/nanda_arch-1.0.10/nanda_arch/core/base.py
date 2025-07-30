from abc import ABC

from fastapi import APIRouter


class AppConfigBase(ABC):
    name: str
    models: list[str] | tuple[str]
    router: APIRouter
    db_connection: str
