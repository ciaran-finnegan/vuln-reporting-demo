from django.contrib import admin
from .models import (
    AssetType, AssetCategory, AssetSubtype, Asset, Vulnerability, Finding, BusinessGroup, SLAPolicy,
    RemediationCampaign, CampaignFinding, ScannerIntegration, FieldMapping,
    SeverityMapping, ScannerUpload, AssetTag
)
from .forms import FieldMappingForm

# Legacy AssetType
admin.site.register(AssetType)

# Enhanced Asset categorisation
class AssetSubtypeInline(admin.TabularInline):
    model = AssetSubtype
    extra = 0
    fields = ['name', 'cloud_provider', 'description']

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'subtype_count']
    search_fields = ['name', 'description']
    ordering = ['name']
    inlines = [AssetSubtypeInline]
    
    def subtype_count(self, obj):
        return obj.subtypes.count()
    subtype_count.short_description = 'Subtypes'

@admin.register(AssetSubtype)
class AssetSubtypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'cloud_provider', 'description', 'created_at']
    list_filter = ['category', 'cloud_provider']
    search_fields = ['name', 'description', 'category__name']
    ordering = ['category', 'cloud_provider', 'name']

# Other models
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