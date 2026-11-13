
from .models import Lead


def has_full_lead_access(user):
    """
    Administradores e gerentes podem acessar todos os leads.
    Superusuários também possuem acesso total.
    """
    if not user.is_authenticated:
        return False

    return (
        user.is_superuser
        or user.role in [
            "ADMIN",
            "MANAGER",
        ]
    )


def get_user_leads(user):
    """
    Retorna os leads que o usuário pode visualizar.

    ADMIN / MANAGER: todos os leads.
    SELLER: somente leads atribuídos a ele.
    Outros perfis: nenhum lead.
    """
    if not user.is_authenticated:
        return Lead.objects.none()

    if has_full_lead_access(user):
        return Lead.objects.all()

    if user.role == "SELLER":
        return Lead.objects.filter(
            assigned_to=user
        )

    return Lead.objects.none()
