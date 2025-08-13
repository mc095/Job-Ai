from django import forms

class AnalysisForm(forms.Form):
    job_description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6, "placeholder": "Paste the job description here..."}),
        label="Job Description"
    )
