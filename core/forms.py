from django import forms  # Import forms from Django

class UploadFileForm(forms.Form):
    file = forms.FileField()  # Define a file field for uploading files
