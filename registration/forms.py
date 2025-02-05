from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from datetime import date

User = get_user_model()


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")


class UserNameUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ["username",]

    def __init__(self, *args, username=None, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)
        if username:
            self.fields["username"].widget.attrs["value"] = username

    def change(self, user):
            user.username = self.cleaned_data["username"]
            user.save()
            user.username_updated_at = date.today()
