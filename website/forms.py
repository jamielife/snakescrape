from django import forms

class CreateNew(forms.Form):
    url = forms.CharField(label="Website URL", max_length=2048)
    jobTitle = forms.CharField(label="Job Title", max_length=255)
    pageElement = forms.CharField(label="Page Element", max_length=255, required=False)
    pageClass = forms.CharField(label="Page Class", max_length=255, required=False)