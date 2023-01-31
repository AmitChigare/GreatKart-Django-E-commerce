from django import forms
from .models import Account, UserProfile

# class ContactForm(forms.Form):
#     subject = forms.CharField(max_length=100)
#     message = forms.CharField(widget=forms.Textarea)
#     sender = forms.EmailField()
#     cc_myself = forms.BooleanField(required=False)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter Password",
            }
        ),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Repeat Password",
            }
        )
    )

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number", "email", "password"]

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password Does not match")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter First Name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter last Name"
        self.fields["phone_number"].widget.attrs["placeholder"] = "Enter Phone Number"
        self.fields["email"].widget.attrs["placeholder"] = "Enter Email Address"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


# class LoginForm(forms.ModelForm):
#     email = forms.EmailField(max_length=100)
#     password = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 "placeholder": "Enter Password",
#                 "class": "form-control",
#             }
#         )
#     )

#     class Meta:
#         model = Account
#         fields = ["email", "password"]

#     def clean(self):
#         cleaned_data = super(LoginForm, self).clean()


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number"]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False,
        error_messages={"invalid": ("Image files only")},
        widget=forms.FileInput,
    )

    class Meta:
        model = UserProfile
        fields = ["profile_picture", "address_line", "country", "state", "city"]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
