import logging
from fastapi import FastAPI
from importlib import import_module

from tortoise.contrib.fastapi import RegisterTortoise

from nanda_arch.core.base import AppConfigBase

logger = logging.getLogger(__name__)


def get_app_instance_config(path: str) -> AppConfigBase:
    """
    Importa dinamicamente um módulo de app e retorna a instância de sua AppConfig.
    """
    try:
        app_module = import_module(path)
    except ImportError as e:
        # Usar 'from e' preserva o traceback original da exceção, o que ajuda muito no debug.
        raise ImportError(f'Não foi possível encontrar o módulo de app em `{path}`') from e

    app_config_class = getattr(app_module, 'AppConfig', None)
    if not app_config_class:
        raise AttributeError(f'O módulo `{path}` não possui uma classe `AppConfig`.')

    return app_config_class()


class AppRegistry:
    """
        Responsável por descobrir, configurar e registrar todas as aplicações
        instaladas (INSTALLED_APPS) na instância do FastAPI.
    """

    def __init__(self, app: FastAPI):

        # noinspection PyUnresolvedReferences
        from system.settings import INSTALLED_APPS, ORM_SETTINGS_CONNECTIONS

        self.fastapi_app = app
        self.tortoise_settings = {
            'connections': ORM_SETTINGS_CONNECTIONS,
            'apps': {
                'aerich': {
                    'models': ['aerich.models'],
                    'default_connection': 'default',
                }
            }
        }

        self._installed_apps = INSTALLED_APPS
        self._configure_apps()
        self._register_tortoise()


    def _configure_apps(self):
        """
            Itera sobre as apps instaladas, inclui seus routers e prepara
            a configuração do Tortoise ORM.
        """
        for app_path in self._installed_apps:
            config = get_app_instance_config(app_path)
            self.fastapi_app.include_router(config.router)
            self.tortoise_settings['apps'][config.name] = {
                'models': config.models,
                'default_connection': config.db_connection,
            }

        logger.debug("Configurações do Tortoise-ORM finalizadas: %s", self.tortoise_settings)

    def _register_tortoise(self):
        """
            Registra o Tortoise ORM na instância do FastAPI com as configurações montadas.
        """
        RegisterTortoise(
            self.fastapi_app,
            config=self.tortoise_settings,
        )