from django.contrib import admin
from .models import (
    AssetType, Asset, Vulnerability, Finding, BusinessGroup, SLAPolicy,
    RemediationCampaign, CampaignFinding, ScannerIntegration, FieldMapping,
    SeverityMapping, ScannerUpload, AssetTag
)
from .forms import FieldMappingForm

admin.site.register(AssetType)
admin.site.register(Asset)
admin.site.register(Vulnerability)
admin.site.register(Finding)
admin.site.register(BusinessGroup)
admin.site.register(SLAPolicy)
admin.site.register(RemediationCampaign)
admin.site.register(CampaignFinding)
admin.site.register(ScannerIntegration)

class FieldMappingAdmin(admin.ModelAdmin):
    form = FieldMappingForm
    list_display = ['integration', 'source_field', 'target_model', 'target_field', 'field_type', 'is_active', 'sort_order']
    list_filter = ['integration', 'target_model', 'field_type', 'is_active']
    search_fields = ['source_field', 'target_field', 'description']
    ordering = ['integration', 'target_model', 'sort_order']

admin.site.register(FieldMapping, FieldMappingAdmin)

admin.site.register(SeverityMapping)
admin.site.register(ScannerUpload)
admin.site.register(AssetTag)