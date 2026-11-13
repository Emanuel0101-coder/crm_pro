
from django.urls import path
from . import views

app_name = "leads"

urlpatterns = [
    path("", views.lead_list, name="list"),
    path("novo/", views.lead_create, name="create"),

    path("acompanhamentos/", views.followup_list, name="followups"),
    path(
        "acompanhamentos/<int:pk>/concluir/",
        views.followup_complete,
        name="followup_complete"
    ),

    path("<int:pk>/", views.lead_detail, name="detail"),
    path(
        "<int:pk>/interacoes/nova/",
        views.lead_activity_create,
        name="activity_create"
    ),
    path("<int:pk>/editar/", views.lead_update, name="update"),
    path("<int:pk>/excluir/", views.lead_delete, name="delete"),
]
