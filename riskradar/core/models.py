from django.db import models
from django.utils import timezone

SEVERITY_CHOICES = [
    ('Info', 'Info'),
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
    ('Critical', 'Critical'),
]

class AssetType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'asset_type'

    def __str__(self):
        return self.name

class AssetCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_category'
        verbose_name = 'Asset Category'
        verbose_name_plural = 'Asset Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class AssetSubtype(models.Model):
    subtype_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE, related_name='subtypes')
    name = models.CharField(max_length=100)
    cloud_provider = models.CharField(max_length=20, null=True, blank=True,
                                    help_text="AWS, Azure, GCP (for Cloud Resource category)")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_subtype'
        verbose_name = 'Asset Subtype'
        verbose_name_plural = 'Asset Subtypes'
        ordering = ['category', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name', 'cloud_provider'],
                name='unique_subtype_per_category'
            ),
        ]

    def __str__(self):
        if self.cloud_provider:
            return f"{self.category.name} - {self.name} ({self.cloud_provider})"
        return f"{self.category.name} - {self.name}"

class Asset(models.Model):
    name = models.CharField(max_length=255)
    # Legacy field - kept for backward compatibility during migration
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT, null=True, blank=True)
    # New enhanced fields
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='assets')
    subtype = models.ForeignKey(AssetSubtype, on_delete=models.SET_NULL, related_name='assets', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    hostname = models.CharField(max_length=255, null=True, blank=True)
    operating_system = models.CharField(max_length=100, null=True, blank=True)
    mac_address = models.CharField(max_length=50, null=True, blank=True)
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'asset'
        constraints = [
            models.UniqueConstraint(
                fields=['hostname', 'ip_address'],
                name='unique_hostname_ip',
                condition=models.Q(hostname__isnull=False, ip_address__isnull=False)
            ),
        ]
        ordering = ['name']

    def __str__(self):
        if self.subtype:
            return f"{self.name} ({self.subtype.name})"
        elif self.category:
            return f"{self.name} ({self.category.name})"
        elif self.asset_type:  # Fallback for legacy data
            return f"{self.name} ({self.asset_type.name})"
        return self.name

class Vulnerability(models.Model):
    external_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    external_source = models.CharField(max_length=50, null=True, blank=True,
                                     help_text="Scanner name (e.g., 'Nessus', 'Qualys')")
    cve_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    severity_level = models.SmallIntegerField(null=True, blank=True,
                                           help_text="Normalised severity 0-10")
    severity_label = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='Medium')
    cvss_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    fix_info = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    references = models.JSONField(default=list, blank=True, null=True)
    risk_factor = models.CharField(max_length=20, null=True, blank=True)
    exploit = models.JSONField(default=dict, blank=True)
    cvss = models.JSONField(default=dict, blank=True, null=True)
    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'vulnerability'
        ordering = ['-severity', '-cvss_score']
        constraints = [
            models.UniqueConstraint(
                fields=['cve_id'],
                name='unique_cve_id',
                condition=models.Q(cve_id__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['external_source', 'external_id'],
                name='unique_external_vuln',
                condition=models.Q(external_source__isnull=False, external_id__isnull=False)
            ),
        ]

    def __str__(self):
        return f"{self.external_id or 'No ID'}: {self.title[:50]}"

class ScannerIntegration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=50, default='vuln_scanner',
                          help_text="e.g., 'vuln_scanner', 'asset_inventory'")
    default_asset_category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, 
                                             null=True, blank=True,
                                             help_text="Default category for assets from this scanner")
    version = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scanner_integration'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}" + (f" v{self.version}" if self.version else "")

class Finding(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('fixed', 'Fixed'),
        ('accepted', 'Risk Accepted'),
        ('false_positive', 'False Positive'),
    ]
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='findings')
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.CASCADE, related_name='findings')
    integration = models.ForeignKey(ScannerIntegration, on_delete=models.CASCADE,
                                  related_name='findings', null=True,
                                  help_text="Scanner that discovered this finding")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    severity_level = models.SmallIntegerField(null=True, blank=True,
                                           help_text="Normalised severity 0-10")
    port = models.IntegerField(null=True, blank=True)
    protocol = models.CharField(max_length=20, null=True, blank=True)
    service = models.CharField(max_length=100, null=True, blank=True)
    plugin_output = models.TextField(blank=True)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    fixed_at = models.DateTimeField(null=True, blank=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'finding'
        constraints = [
            models.UniqueConstraint(
                fields=['asset', 'vulnerability', 'integration', 'port', 'protocol', 'service'],
                name='unique_finding_per_scanner'
            ),
        ]
        ordering = ['-risk_score', '-vulnerability__severity']

    def __str__(self):
        return f"{self.vulnerability.title} on {self.asset.name}"

    def save(self, *args, **kwargs):
        # Simple risk calculation for MVP (cap at 999.99 to prevent overflow)
        if not self.risk_score and self.vulnerability.severity_level:
            try:
                severity_level = float(self.vulnerability.severity_level)
                self.risk_score = min(severity_level * 10, 999.99)
            except (ValueError, TypeError):
                self.risk_score = 50  # Default fallback
        elif not self.risk_score:
            severity_scores = {'Critical': 10, 'High': 8, 'Medium': 5, 'Low': 2, 'Info': 1}
            self.risk_score = min(severity_scores.get(self.vulnerability.severity, 0) * 10, 999.99)
        # Update severity_level if not set
        if not self.severity_level and self.vulnerability.severity_level:
            self.severity_level = self.vulnerability.severity_level
        # Auto-set fixed_at when status changes to fixed
        if self.status == 'fixed' and not self.fixed_at:
            self.fixed_at = timezone.now()
        super().save(*args, **kwargs)

class BusinessGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    criticality_score = models.IntegerField(default=5, help_text="1-10, where 10 is most critical")
    assets = models.ManyToManyField(Asset, related_name='business_groups', blank=True)

    class Meta:
        db_table = 'business_group'

    def __str__(self):
        return self.name

class SLAPolicy(models.Model):
    name = models.CharField(max_length=100)
    business_group = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='sla_policies')
    is_default = models.BooleanField(default=False)
    severity_days = models.JSONField(default=dict, help_text='{"Critical": 1, "High": 7, "Medium": 30, "Low": 90, "Info": 365}')

    class Meta:
        db_table = 'sla_policy'
        verbose_name = 'SLA Policy'
        verbose_name_plural = 'SLA Policies'

    def __str__(self):
        return f"{self.name} ({'Default' if self.is_default else self.business_group})"

class RemediationCampaign(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    findings = models.ManyToManyField(Finding, through='CampaignFinding', related_name='campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'remediation_campaign'

    def __str__(self):
        return self.name

    @property
    def progress_percentage(self):
        total = self.findings.count()
        if total == 0:
            return 0
        fixed = self.findings.filter(status='fixed').count()
        return round((fixed / total) * 100, 2)

class CampaignFinding(models.Model):
    campaign = models.ForeignKey(RemediationCampaign, on_delete=models.CASCADE)
    finding = models.ForeignKey(Finding, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        db_table = 'campaign_finding'
        unique_together = ['campaign', 'finding']

class FieldMapping(models.Model):
    FIELD_TYPE_CHOICES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('decimal', 'Decimal'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('datetime', 'DateTime'),
    ]
    TARGET_MODEL_CHOICES = [
        ('asset', 'Asset'),
        ('vulnerability', 'Vulnerability'),
        ('finding', 'Finding'),
    ]
    integration = models.ForeignKey(ScannerIntegration, on_delete=models.CASCADE, related_name='field_mappings')
    source_field = models.CharField(max_length=200, help_text="XML path or field name from scanner (e.g., 'host-ip' or 'ReportItem@pluginID')")
    target_model = models.CharField(max_length=50, choices=TARGET_MODEL_CHOICES)
    target_field = models.CharField(max_length=100, help_text="Model field name (e.g., 'ip_address' or 'extra.os')")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default='string')
    is_required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True, help_text="Default value if source field is empty")
    transformation_rule = models.TextField(blank=True, help_text="Python expression for complex transformations")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'field_mapping'
        ordering = ['integration', 'target_model', 'sort_order']
        unique_together = ['integration', 'source_field', 'target_model', 'target_field']

    def __str__(self):
        return f"{self.integration.name}: {self.source_field} → {self.target_model}.{self.target_field}"

class SeverityMapping(models.Model):
    integration = models.ForeignKey(ScannerIntegration, on_delete=models.CASCADE, related_name='severity_mappings')
    external_severity = models.CharField(max_length=50, help_text="Scanner-specific severity value")
    internal_severity_label = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    internal_severity_level = models.SmallIntegerField(help_text="Normalised severity 0-10")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'severity_mapping'
        ordering = ['integration', 'external_severity']
        unique_together = ['integration', 'external_severity']

    def __str__(self):
        return f"{self.integration.name}: {self.external_severity} → {self.internal_severity_label} ({self.internal_severity_level})"

class ScannerUpload(models.Model):
    integration = models.ForeignKey(ScannerIntegration, on_delete=models.CASCADE, related_name='uploads')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(null=True, blank=True)
    file_path = models.TextField()  # Supabase Storage path
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    error_message = models.TextField(blank=True)
    stats = models.JSONField(default=dict, blank=True)
    processing_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'scanner_upload'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} ({self.integration.name}) - {self.status}"

class AssetTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tag_key = models.CharField(max_length=100, null=True, blank=True, help_text="Dynamic tag key (e.g. 'owner')")
    tag_value = models.CharField(max_length=255, null=True, blank=True, help_text="Dynamic tag value (e.g. 'alice@example.com')")
    # Add any other fields as needed

    class Meta:
        db_table = 'asset_tag'
        verbose_name = 'Asset Tag'
        verbose_name_plural = 'Asset Tags'

    def __str__(self):
        if self.tag_key and self.tag_value:
            return f"{self.name} ({self.tag_key}:{self.tag_value})"
        return self.name
