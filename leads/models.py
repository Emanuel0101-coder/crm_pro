
from django.conf import settings
from django.db import models


class Lead(models.Model):

    class Status(models.TextChoices):
        NEW = "NEW", "Novo"
        CONTACTED = "CONTACTED", "Em contato"
        QUALIFIED = "QUALIFIED", "Qualificado"
        CONVERTED = "CONVERTED", "Convertido"
        LOST = "LOST", "Perdido"

    class Source(models.TextChoices):
        INSTAGRAM = "INSTAGRAM", "Instagram"
        FACEBOOK = "FACEBOOK", "Facebook"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        WEBSITE = "WEBSITE", "Site"
        REFERRAL = "REFERRAL", "Indicação"
        PHONE = "PHONE", "Telefone"
        LINKEDIN = "LINKEDIN", "LinkedIn"
        OTHER = "OTHER", "Outros"

    name = models.CharField(
        "Nome",
        max_length=150
    )

    company = models.CharField(
        "Empresa",
        max_length=150,
        blank=True
    )

    email = models.EmailField(
        "E-mail",
        blank=True
    )

    phone = models.CharField(
        "Telefone",
        max_length=20,
        blank=True
    )

    source = models.CharField(
        "Origem",
        max_length=20,
        choices=Source.choices,
        default=Source.OTHER
    )

    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )

    notes = models.TextField(
        "Observações",
        blank=True
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads",
        verbose_name="Responsável"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_leads",
        verbose_name="Cadastrado por"
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
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["source"]),
            models.Index(fields=["assigned_to"]),
        ]

    def __str__(self):
        return self.name


class LeadActivity(models.Model):

    class ActivityType(models.TextChoices):
        CALL = "CALL", "Ligação"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        EMAIL = "EMAIL", "E-mail"
        MEETING = "MEETING", "Reunião"
        NOTE = "NOTE", "Observação"
        OTHER = "OTHER", "Outro"

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Lead"
    )

    activity_type = models.CharField(
        "Tipo de interação",
        max_length=20,
        choices=ActivityType.choices,
    )

    description = models.TextField(
        "Descrição"
    )

    outcome = models.TextField(
        "Resultado",
        blank=True
    )

    next_contact_at = models.DateTimeField(
        "Próximo contato",
        null=True,
        blank=True
    )
    

    # Controle de conclusão do acompanhamento
    is_completed = models.BooleanField(
        "Concluído",
        default=False
    )

    completed_at = models.DateTimeField(
        "Data de conclusão",
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_activities",
        verbose_name="Registrado por"
    )

    created_at = models.DateTimeField(
        "Data do registro",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Interação do lead"
        verbose_name_plural = "Interações dos leads"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["lead", "-created_at"]),
            models.Index(fields=["activity_type"]),
            models.Index(fields=["next_contact_at", "is_completed"]),
        ]

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.lead.name}"
