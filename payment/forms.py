from django import forms
from .models import Shippingaddr


class ShippingForm(forms.ModelForm):
    # 'name' maps to the form field but the model field is 'shipping_name'
    # We override it here so the HTML form posts 'name' consistently
    name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        }),
        required=True
    )
    shipping_address = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Address'
        }),
        required=True
    )
    shipping_city = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your City'
        }),
        required=True
    )
    shipping_state = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your State'
        }),
        required=True
    )
    shipping_country = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Country'
        }),
        required=True
    )
    shipping_phone_number = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Telephone'
        }),
        required=True
    )
    shipping_email = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email'
        }),
        required=True
    )

    class Meta:
        model = Shippingaddr
        # 'name' here refers to the form field above, saved via save() override below
        fields = [
            'name',
            'shipping_address',
            'shipping_city',
            'shipping_state',
            'shipping_country',
            'shipping_phone_number',
            'shipping_email',
        ]
        exclude = ['customer']

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Map the form's 'name' field to the model's 'shipping_name' field
        instance.shipping_name = self.cleaned_data.get('name', '')
        if commit:
            instance.save()
        return instance


class PaymentForm(forms.Form):
    card_name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name on Card'
        }),
        required=True
    )
    card_exp = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Expiry Date (MM/YY)'
        }),
        required=True
    )
    card_cvv = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CVV'
        }),
        required=True
    )
    card_num = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Card Number (e.g. 1234 - **** - **** - ****)'
        }),
        required=True
    )