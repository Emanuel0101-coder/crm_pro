
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import LeadActivity

from .forms import LeadForm, LeadActivityForm
from .models import Lead
from .permissions import get_user_leads, has_full_lead_access


def check_lead_access(user):
    """
    Permite acesso somente aos perfis autorizados.
    """
    if not user.is_authenticated:
        raise PermissionDenied

    if not has_full_lead_access(user) and user.role != "SELLER":
        raise PermissionDenied


@login_required
def lead_list(request):
    check_lead_access(request.user)

    leads = get_user_leads(request.user).select_related(
        "assigned_to",
        "created_by",
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    source = request.GET.get("source", "").strip()

    if search:
        leads = leads.filter(
            Q(name__icontains=search)
            | Q(company__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        )

    if status in Lead.Status.values:
        leads = leads.filter(status=status)

    if source in Lead.Source.values:
        leads = leads.filter(source=source)

    paginator = Paginator(leads, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "leads": page_obj,
        "search": search,
        "status": status,
        "source": source,
        "status_choices": Lead.Status.choices,
        "source_choices": Lead.Source.choices,
    }

    return render(request, "leads/lead_list.html", context)


@login_required
def lead_create(request):
    check_lead_access(request.user)

    if request.method == "POST":
        form = LeadForm(request.POST, user=request.user)

        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user

            if not has_full_lead_access(request.user):
                lead.assigned_to = request.user

            elif not lead.assigned_to:
                lead.assigned_to = request.user

            lead.save()

            messages.success(
                request,
                "Lead cadastrado com sucesso!"
            )

            return redirect("leads:list")

    else:
        form = LeadForm(user=request.user)

    return render(
        request,
        "leads/lead_form.html",
        {
            "form": form,
            "page_title": "Cadastrar lead",
        }
    )


@login_required
def lead_update(request, pk):
    check_lead_access(request.user)

    lead = get_object_or_404(
        get_user_leads(request.user),
        pk=pk
    )

    if request.method == "POST":
        form = LeadForm(
            request.POST,
            instance=lead,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Lead atualizado com sucesso!"
            )

            return redirect("leads:list")

    else:
        form = LeadForm(
            instance=lead,
            user=request.user,
        )

    return render(
        request,
        "leads/lead_form.html",
        {
            "form": form,
            "page_title": "Editar lead",
            "lead": lead,
        }
    )


@login_required
def lead_delete(request, pk):
    check_lead_access(request.user)

    if request.method != "POST":
        return redirect("leads:list")

    lead = get_object_or_404(
        get_user_leads(request.user),
        pk=pk
    )

    lead.delete()

    messages.success(
        request,
        "Lead excluído com sucesso!"
    )

    return redirect("leads:list")


@login_required
def lead_detail(request, pk):
    """
    Exibe os dados e o histórico de um lead.
    """

    check_lead_access(request.user)

    lead = get_object_or_404(
        get_user_leads(request.user).select_related(
            "assigned_to",
            "created_by",
        ),
        pk=pk
    )

    activities = lead.activities.select_related(
        "created_by"
    ).all()

    activity_form = LeadActivityForm()

    context = {
        "lead": lead,
        "activities": activities,
        "activity_form": activity_form,
    }

    return render(
        request,
        "leads/lead_detail.html",
        context
    )


@login_required
def lead_activity_create(request, pk):
    """
    Registra uma nova interação vinculada ao lead.
    """

    check_lead_access(request.user)

    lead = get_object_or_404(
        get_user_leads(request.user),
        pk=pk
    )

    if request.method != "POST":
        return redirect("leads:detail", pk=lead.pk)

    form = LeadActivityForm(request.POST)

    if form.is_valid():
        activity = form.save(commit=False)

        activity.lead = lead
        activity.created_by = request.user

        activity.save()

        messages.success(
            request,
            "Interação registrada com sucesso!"
        )

    else:
        messages.error(
            request,
            "Não foi possível registrar a interação. Verifique os campos preenchidos."
        )

    return redirect("leads:detail", pk=lead.pk)


@login_required
def followup_list(request):
    check_lead_access(request.user)

    now = timezone.now()
    today = timezone.localdate()

    # Busca os leads que o usuário tem permissão para visualizar.
    user_leads = get_user_leads(request.user)

    # Busca acompanhamentos pendentes que possuem data agendada.
    followups = LeadActivity.objects.filter(
        lead__in=user_leads,
        next_contact_at__isnull=False,
        is_completed=False
    ).select_related(
        "lead",
        "lead__assigned_to",
        "created_by"
    ).order_by("next_contact_at")

    # Indicadores da central de acompanhamentos.
    total_pending = followups.count()

    total_overdue = followups.filter(
        next_contact_at__lt=now
    ).count()

    total_today = followups.filter(
        next_contact_at__date=today
    ).count()

    # Filtros da listagem.
    status = request.GET.get("status", "all")

    if status == "overdue":
        followups = followups.filter(
            next_contact_at__lt=now
        )

    elif status == "today":
        followups = followups.filter(
            next_contact_at__date=today
        )

    elif status == "upcoming":
        followups = followups.filter(
            next_contact_at__gt=now
        )

    context = {
        "followups": followups,
        "total_pending": total_pending,
        "total_overdue": total_overdue,
        "total_today": total_today,
        "status": status,
        "now": now,
        "today": today,
    }

    return render(
        request,
        "leads/followup_list.html",
        context
    )


@login_required
def followup_complete(request, pk):
    check_lead_access(request.user)

    if request.method != "POST":
        return redirect("leads:followups")

    # Respeita as permissões de acesso aos leads.
    user_leads = get_user_leads(request.user)

    activity = get_object_or_404(
        LeadActivity,
        pk=pk,
        lead__in=user_leads,
        next_contact_at__isnull=False,
        is_completed=False
    )

    activity.is_completed = True
    activity.completed_at = timezone.now()

    activity.save(
        update_fields=["is_completed", "completed_at"]
    )

    messages.success(
        request,
        "Acompanhamento concluído com sucesso!"
    )

    return redirect("leads:followups")

