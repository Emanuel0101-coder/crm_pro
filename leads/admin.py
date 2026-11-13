
from django.contrib import admin

from .models import Lead, LeadActivity


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company",
        "email",
        "phone",
        "status",
        "source",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "status",
        "source",
        "created_at",
    )

    search_fields = (
        "name",
        "company",
        "email",
        "phone",
    )

    autocomplete_fields = (
        "assigned_to",
        "created_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 25


@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):

    list_display = (
        "lead",
        "activity_type",
        "created_by",
        "created_at",
        "next_contact_at",
    )

    list_filter = (
        "activity_type",
        "created_at",
    )

    search_fields = (
        "lead__name",
        "description",
        "outcome",
    )

    autocomplete_fields = (
        "lead",
        "created_by",
    )

    readonly_fields = (
        "created_at",
    )

    list_per_page = 25
