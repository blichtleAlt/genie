from django import forms

class SearchForm(forms.Form):
    ingredients = forms.CharField(max_length=100)
