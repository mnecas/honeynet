from django import forms


class HoneynetForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
class HoneypotForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
