import logging
from logging import LogRecord

from django.conf import settings


class RequireNoBugsnagSetting(logging.Filter):
    """We want to turn off normal email error logging when buggsnag settings are present"""

    def filter(self, record):
        return not hasattr(settings, "BUGSNAG")


class RequireNoSentryInstalled(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        try:
            import sentry_sdk  # noqa

            return False
        except ImportError:
            return True
