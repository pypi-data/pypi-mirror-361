import jinja2
import jinja2.ext
from webpack_loader.templatetags.webpack_loader import render_bundle as base_render_bundle


@jinja2.pass_context
def render_bundle(context, *args, **kwargs):
    return base_render_bundle(context, *args, **kwargs)


class Extension(jinja2.ext.Extension):
    def __init__(self, environment):
        super().__init__(environment)

        self.environment.globals.update({"render_bundle": render_bundle})
