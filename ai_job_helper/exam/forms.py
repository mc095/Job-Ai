from django import forms

class JobRoleForm(forms.Form):
    job_role = forms.CharField(
        label="Enter a Job Role",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "w-full border rounded p-2", "placeholder": "e.g., Backend Engineer"})
    )
