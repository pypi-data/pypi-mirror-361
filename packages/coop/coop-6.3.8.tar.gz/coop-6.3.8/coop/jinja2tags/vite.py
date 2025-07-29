import jinja2.ext
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django_vite.core.asset_loader import DjangoViteAssetLoader
from django_vite.templatetags.django_vite import vite_asset, vite_hmr_client


def static_url(path, config="default"):
    if settings.DEBUG:
        asset_loader = DjangoViteAssetLoader.instance()
        client = asset_loader._get_app_client(config)
        if client.dev_mode:
            # Server running in debug and we're loading from the vite dev server, fetch from public
            return asset_loader.generate_vite_asset_url(path, config)
    return staticfiles_storage.url(path)


class Extension(jinja2.ext.Extension):
    def __init__(self, environment):
        super().__init__(environment)

        self.environment.globals.update(
            {
                "vite_hmr_client": vite_hmr_client,
                "vite_asset": vite_asset,
                "static": static_url,
            }
        )
