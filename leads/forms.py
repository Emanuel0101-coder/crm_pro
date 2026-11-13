
from django import forms
from django.contrib.auth import get_user_model

from .models import Lead, LeadActivity
from .permissions import has_full_lead_access

User = get_user_model()


class LeadForm(forms.ModelForm):

    class Meta:
        model = Lead

        fields = [
            "name",
            "company",
            "email",
            "phone",
            "source",
            "status",
            "assigned_to",
            "notes",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome completo",
            }),

            "company": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome da empresa",
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "exemplo@email.com",
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "(00) 00000-0000",
            }),

            "source": forms.Select(attrs={
                "class": "form-control",
            }),

            "status": forms.Select(attrs={
                "class": "form-control",
            }),

            "assigned_to": forms.Select(attrs={
                "class": "form-control",
            }),

            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Informações adicionais sobre o lead",
                "rows": 4,
            }),
        }

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        if self.user and not has_full_lead_access(self.user):

            # Vendedores não podem escolher o responsável.
            self.fields.pop("assigned_to")

        else:

            self.fields["assigned_to"].queryset = (
                User.objects
                .filter(is_active=True)
                .order_by("first_name", "username")
            )

            self.fields["assigned_to"].required = False

    def clean(self):

        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        if not email and not phone:
            raise forms.ValidationError(
                "Informe pelo menos um meio de contato: e-mail ou telefone."
            )

        return cleaned_data


class LeadActivityForm(forms.ModelForm):

    class Meta:
        model = LeadActivity

        fields = [
            "activity_type",
            "description",
            "outcome",
            "next_contact_at",
        ]

        widgets = {
            "activity_type": forms.Select(attrs={
                "class": "form-control",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Descreva o que aconteceu durante o contato...",
                "rows": 4,
            }),

            "outcome": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Qual foi o resultado dessa interação?",
                "rows": 3,
            }),

            "next_contact_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["next_contact_at"].required = False
        self.fields["next_contact_at"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

        self.fields["outcome"].required = False
