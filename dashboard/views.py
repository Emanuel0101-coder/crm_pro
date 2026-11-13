
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from leads.models import Lead, LeadActivity
from leads.permissions import get_user_leads, has_full_lead_access


@login_required
def home(request):
    now = timezone.now()
    today = timezone.localdate()

    user_leads = get_user_leads(request.user)

    total_leads = user_leads.count()

    followups = LeadActivity.objects.filter(
        lead__in=user_leads,
        next_contact_at__isnull=False,
        is_completed=False
    ).select_related(
        "lead",
        "lead__assigned_to",
        "created_by"
    )

    total_overdue = followups.filter(
        next_contact_at__lt=now
    ).count()

    total_today = followups.filter(
        next_contact_at__date=today
    ).count()

    upcoming_followups = followups.filter(
        next_contact_at__gt=now
    ).order_by("next_contact_at")[:5]

    # Leads agrupados por status
    status_counts = {
        item["status"]: item["total"]
        for item in user_leads.values("status").annotate(
            total=Count("id")
        )
    }

    status_labels = [
        label for value, label in Lead.Status.choices
    ]

    status_values = [
        status_counts.get(value, 0)
        for value, label in Lead.Status.choices
    ]

    # Leads agrupados por origem
    source_counts = {
        item["source"]: item["total"]
        for item in user_leads.values("source").annotate(
            total=Count("id")
        )
    }

    source_labels = [
        label for value, label in Lead.Source.choices
    ]

    source_values = [
        source_counts.get(value, 0)
        for value, label in Lead.Source.choices
    ]

    # Distribuição de leads por vendedor
    seller_labels = []
    seller_values = []

    if has_full_lead_access(request.user):
        seller_data = user_leads.values(
            "assigned_to__first_name",
            "assigned_to__last_name",
            "assigned_to__username"
        ).annotate(
            total=Count("id")
        ).order_by("-total")

        for item in seller_data:
            name = (
                f'{item["assigned_to__first_name"]} '
                f'{item["assigned_to__last_name"]}'
            ).strip()

            if not name:
                name = item["assigned_to__username"] or "Não atribuído"

            seller_labels.append(name)
            seller_values.append(item["total"])

    context = {
        "total_leads": total_leads,
        "total_overdue": total_overdue,
        "total_today": total_today,
        "upcoming_followups": upcoming_followups,

        "status_labels": status_labels,
        "status_values": status_values,

        "source_labels": source_labels,
        "source_values": source_values,

        "seller_labels": seller_labels,
        "seller_values": seller_values,
        "show_seller_chart": has_full_lead_access(request.user),
    }

    return render(request, "dashboard/home.html", context)
