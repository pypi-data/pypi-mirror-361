from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.fields import CIEmailField
from wagtail.search import index


class EmailUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class AbstractEmailUser(index.Indexed, AbstractUser):
    username = None
    # FIXME this is deprecating in dj5
    email = CIEmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = EmailUserManager()

    search_fields = [
        index.AutocompleteField("first_name"),
        index.SearchField("first_name"),
        index.AutocompleteField("last_name"),
        index.SearchField("last_name"),
        index.AutocompleteField("email"),
        index.SearchField("email"),
        index.FilterField("is_staff"),
        index.FilterField("is_superuser"),
    ]

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    class Meta:
        abstract = True
