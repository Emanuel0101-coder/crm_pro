
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "Digite seu usuário",
            "autocomplete": "username",
            "autofocus": True,
        })

        self.fields["password"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "Digite sua senha",
            "autocomplete": "current-password",
        })

        self.fields["username"].label = "Usuário"
        self.fields["password"].label = "Senha"
