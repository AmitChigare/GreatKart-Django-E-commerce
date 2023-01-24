from django import forms
from .models import Account

# class ContactForm(forms.Form):
#     subject = forms.CharField(max_length=100)
#     message = forms.CharField(widget=forms.Textarea)
#     sender = forms.EmailField()
#     cc_myself = forms.BooleanField(required=False)


class RegistrationForm(forms.ModelForm):
    # first_name = forms.CharField(max_length=100)
    # last_name = forms.CharField(max_length=100)
    # email = forms.EmailField(max_length=100)
    # phone_number = forms.CharField(max_length=100)
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Your First Name",
                "class": "form-control",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Your Last Name",
                "class": "form-control",
            }
        ),
    )
    email = forms.CharField(
        max_length=100,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Your Email Adddress",
                "class": "form-control",
            }
        ),
    )
    phone_number = forms.CharField(
        max_length=100,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Your Phone Number",
                "class": "form-control",
            }
        ),
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter Password",
                "class": "form-control",
            }
        ),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Repeat Password",
                "class": "form-control",
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

    # def __int__(self, *args, **kwargs):
    #     super(RegistrationForm, self).__init__(*args, **kwargs)
    #     # self.fields["first_name"].widget.attrs["placeholder"] = "Your First Name"
    #     # self.fields["last_name"].widget.attrs["placeholder"] = "Your Last name"
    #     # self.fields["email"].widget.attrs["placeholder"] = "Your Email"
    #     # self.fields["phone_number"].widget.attrs["placeholder"] = "Your Phone Number"
    #     # self.fields["first_name"].widget.attrs["class"] = "form-control"
    #     for field in self.fields():
    #         field.field.widget.attrs["class"] = "form-control"


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
