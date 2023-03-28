from django import forms


class HoneynetForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    hostname = forms.CharField(
        label="ESXi hostname",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    username = forms.CharField(
        label="ESXi username",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="ESXi password",
        max_length=128,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    nic = forms.CharField(
        label="Physical NIC",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    switch = forms.CharField(
        label="Switch name",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
