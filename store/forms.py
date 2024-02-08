from django import forms


# forms.py
class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search for Product Names and Descriptions',
            'class': 'form-control',
        }),
        label='',  # Set label to an empty string to remove it
    )

