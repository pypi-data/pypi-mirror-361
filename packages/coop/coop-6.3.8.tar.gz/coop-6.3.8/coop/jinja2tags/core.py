import json
import re
import warnings
from typing import List

import jinja2
import jinja2.ext
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.messages import get_messages
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import date, linebreaks_filter, linebreaksbr, time
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_htmx.jinja import django_htmx_script
from markupsafe import Markup
from wagtail.models import Page, Site


def add_form_class(bound_field, *args, **kwargs):
    """Add a class to a django form field widget"""
    attrs = bound_field.field.widget.attrs
    classes = sorted(set(attrs.get("class", "").split() + merge_classes(*args, **kwargs).split()))
    attrs["class"] = " ".join(classes)
    return bound_field


def add_form_attributes(bound_field, attributes={}):
    """Add 1 or more attributes to a django form field widget"""
    bound_field.field.widget.attrs.update(attributes)
    return bound_field


def include_static(path):
    """
    Include the contents of a file that has been compiled into the static directory
    """
    fullpath = finders.find(path)
    if fullpath is None:
        raise ValueError("Could not find file %s" % path)

    with open(fullpath, "r") as f:
        return f.read()


def debug_variable(variable):
    """Print all the fields available on a variable"""
    return format_html("<pre>{}</pre>", dir(variable))


def url(name, *args, **kwargs):
    """Reverse a URL name. Alias of ``django.core.urlresolvers.reverse``"""
    return reverse(name, args=args or None, kwargs=kwargs or None)


@jinja2.pass_context
def site_root(context):
    """Get the root page for the site"""
    # This lookup will be cached on the intermediary objects, so this will only
    # hit the DB once per request
    request = context["request"]
    return Site.find_for_request(request).root_page.specific


def svg_inline(name, classes=""):
    """
    Inline an SVG image with optional classes. SVG images are expected to be a template, not kept in
    the static files
    """
    svg_content = render_to_string("svgs/%s.svg" % name)

    if classes:
        soup = BeautifulSoup(svg_content, "html.parser")
        svg_tag = soup.find("svg")
        if svg_tag:
            existing_classes: str | List[str] = svg_tag.get("class", "")
            if isinstance(existing_classes, list):
                existing_classes = " ".join(existing_classes)
            svg_tag["class"] = f"{existing_classes} {classes}".strip()
        svg_content = str(soup)

    return mark_safe(svg_content)


@jinja2.pass_context
def breadcrumbs(context, page=None):
    """Print the top navigation menu for this site"""
    request = context.get("request")
    root = site_root(context)
    if page is None:
        page = context.get("page")
    ancestors = page.get_ancestors().filter(depth__gte=root.depth)

    return Markup(
        render_to_string(
            "tags/breadcrumbs.html",
            {
                "page": page,
                "ancestors": ancestors,
                "request": request,
            },
        )
    )


def model_classname(model_or_instance):
    """
    Generate a CSS class name from a Page model

    Usage::

        <html class="{{ self|model_classname }}">
    """
    if isinstance(model_or_instance, Page):
        model_or_instance = model_or_instance.content_type.model_class()

    try:
        meta = model_or_instance._meta
        return "page-{0}-{1}".format(meta.app_label, meta.model_name)
    except AttributeError:
        return ""


@jinja2.pass_context
def messages(context):
    """Get any messages from django.contrib.messages framework"""
    return get_messages(context.get("request"))


def json_dumps(value):
    """
    Dump the value to a JSON string. Useful when sending values to JavaScript
    """
    return Markup(json.dumps(value, cls=DjangoJSONEncoder))


@jinja2.pass_context
def qs(context, get=None, **kwargs):
    """
    Update a querydict with new values, and return it as a URL encoded string.
    Pass in the current ``request.GET``, and any items to set as keyword
    arguments. If a key has a value of ``None``, that key is removed from the
    querydict.

    The querydict is grabbed from ``request`.GET` in the context by default,
    but an alternative can be provided as the first positional argument.

    >>> request.GET.urlencode()
    "page=1&foo=bar"
    >>> qs(request.GET, page=2, baz="quux", foo=None)
    "page=2&baz=quux"
    """
    if get is None:
        get = context["request"].GET

    get = get.copy()
    for key, value in kwargs.items():
        if value is None:
            # Delete keys if value is None
            get.pop(key, None)
        else:
            get[key] = value
    return get.urlencode()


not_digit_re = re.compile(r"[^0-9+]+")


def tel(value):
    return "tel:{}".format(not_digit_re.sub("-", value).strip("-"))


def render_honeypot_field():
    # Deprecated
    warnings.warn("render_honeypot_field is deprecated, remove from templates")
    return ""


@jinja2.pass_context
def analytics_js(context, umami_id=None):
    hide: bool = settings.DEBUG
    if request := context.get("request"):
        hide |= getattr(request, "preview", False)
    umami_id = umami_id or getattr(settings, "UMAMI_ID", None)
    if not hide and umami_id:
        return mark_safe(
            f'<script async src="https://stats.neonjungle.com.au/script.js" data-website-id="{umami_id}"></script>'
        )
    return ""


def merge_classes(*args, **kwargs):
    """
    Merge classes together, removing any falsy values
    """
    classes = set()

    def process_dict(d):
        for key, value in d.items():
            if value:
                classes.add(key)

    for arg in args:
        if not arg:
            continue
        if isinstance(arg, str):
            classes.update(arg.split())
        elif isinstance(arg, dict):
            process_dict(arg)
        elif isinstance(arg, (list, tuple)):
            for item in arg:
                if isinstance(item, str):
                    classes.update(item.split())
                elif isinstance(item, dict):
                    process_dict(item)
        else:
            raise ValueError(f"Unsupported type {type(arg)}")
    process_dict(kwargs)
    return " ".join(classes)


class Extension(jinja2.ext.Extension):
    def __init__(self, environment):
        super().__init__(environment)

        self.environment.globals.update(
            {
                "breadcrumbs": breadcrumbs,
                "site_root": site_root,
                "static": staticfiles_storage.url,
                "include_static": include_static,
                "url": url,
                "svg": svg_inline,
                "model_classname": model_classname,
                "messages": messages,
                "DEBUG": settings.DEBUG,
                "qs": qs,
                "render_honeypot_field": render_honeypot_field,
                "analytics_js": analytics_js,
                "merj": merge_classes,
                "django_htmx_script": django_htmx_script,
            }
        )

        self.environment.filters.update(
            {
                "model_classname": model_classname,
                "add_form_class": add_form_class,
                "add_form_attributes": add_form_attributes,
                "debug_variable": debug_variable,
                "br": linebreaksbr,
                "p": linebreaks_filter,
                "json": json_dumps,
                "tel": tel,
                "time_format": time,
                "date_format": date,
            }
        )
