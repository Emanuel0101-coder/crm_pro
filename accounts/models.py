
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        MANAGER = "MANAGER", "Gerente"
        SELLER = "SELLER", "Vendedor"

    email = models.EmailField(
        "E-mail",
        unique=True
    )

    role = models.CharField(
        "Cargo",
        max_length=20,
        choices=Role.choices,
        default=Role.SELLER
    )

    phone = models.CharField(
        "Telefone",
        max_length=20,
        blank=True
    )

    created_at = models.DateTimeField(
        "Data de cadastro",
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        "Última atualização",
        auto_now=True
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return self.get_full_name() or self.username
