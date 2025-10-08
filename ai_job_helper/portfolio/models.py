from django.db import models
from django.contrib.auth.models import User
from djongo import models as djongo_models
from bson import ObjectId
import json

class Portfolio(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
    portfolio_data = models.JSONField(default=dict)  # Store all form data as JSON
    selected_template = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Portfolio"

    class Meta:
        ordering = ['-updated_at']

# Portfolio templates available
PORTFOLIO_TEMPLATES = [
    {
        'id': 'template1',
        'name': 'Elegant Light',
        'description': 'Light, elegant design with subtle animations',
        'preview': '/static/portfolio/previews/template1.jpg'
    },
    {
        'id': 'template2',
        'name': 'Interactive Dark',
        'description': 'Immersive dark theme with interactive effects',
        'preview': '/static/portfolio/previews/template2.jpg'
    },
    {
        'id': 'template3',
        'name': 'Professional Clean',
        'description': 'Business-ready, clean layout focusing on clarity',
        'preview': '/static/portfolio/previews/template3.jpg'
    }
]

