from django import forms

class ATSForm(forms.Form):
    job_description = forms.CharField(
        label="Job Description",
        widget=forms.Textarea(attrs={
            "rows": 8,
            "placeholder": "Paste the job description here..."
        })
    )
    rewrite_resume = forms.BooleanField(
        required=False,
        initial=True,
        label="Also generate an optimized resume rewrite"
    )
