from django import forms
from .models import FieldMapping

class FieldMappingForm(forms.ModelForm):
    TARGET_FIELD_CHOICES = [
        ('hostname', 'Hostname'),
        ('ip_address', 'IP Address'),
        ('asset_type', 'Asset Type'),
        ('metadata.os', 'Metadata OS'),
        ('external_id', 'External ID'),
        ('name', 'Name'),
        ('cvss_score', 'CVSS Score'),
        ('description', 'Description'),
        ('solution', 'Solution'),
        ('metadata.family', 'Metadata Family'),
        ('metadata.synopsis', 'Metadata Synopsis'),
        ('port', 'Port'),
        ('protocol', 'Protocol'),
        ('service', 'Service'),
        ('plugin_output', 'Plugin Output'),
    ]

    target_field = forms.ChoiceField(choices=TARGET_FIELD_CHOICES)

    class Meta:
        model = FieldMapping
        fields = '__all__' 