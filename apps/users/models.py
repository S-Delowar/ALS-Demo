from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, profession, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        if not profession:
            raise ValueError("The Profession field must be set")

        if not password:
            raise ValueError("The Password field must be set")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            profession=profession,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, profession, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            email=email,
            profession=profession,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    profession = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["profession"]

    def __str__(self):
        return self.email
