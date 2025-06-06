import uuid
from django.db import models
from django.contrib.auth.models import User
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
        db_table = 'vulnerabilities'
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
    """Enhanced integration model supporting all future integration types"""
    
    # Integration Types
    INTEGRATION_TYPE_CHOICES = [
        ('file_upload', 'File Upload'),
        ('api', 'API Connection'),
        ('cloud_storage', 'Cloud Storage'),
        ('webhook', 'Webhook'),
        ('database', 'Database Connection'),
        ('message_queue', 'Message Queue'),
        ('custom', 'Custom Integration'),
    ]
    
    # Status Types  
    STATUS_CHOICES = [
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('testing', 'Testing'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
        ('deprecated', 'Deprecated'),
    ]
    
    # Environment Types
    ENVIRONMENT_CHOICES = [
        ('development', 'Development'),
        ('staging', 'Staging'),
        ('production', 'Production'),
    ]
    
    # Sync Status Choices
    SYNC_STATUS_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'), 
        ('partial', 'Partial Success'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled'),
    ]
    
    # ====== BASIC FIELDS (EXISTING) ======
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
    
    # ====== INTEGRATION MANAGEMENT FIELDS (NEW) ======
    
    # Integration Configuration
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPE_CHOICES, default='file_upload')
    vendor = models.CharField(max_length=100, blank=True, help_text="Vendor name (e.g., 'Tenable', 'Qualys')")
    logo_url = models.URLField(blank=True, help_text="Integration logo URL")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    environment = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICES, default='production')
    
    # Connection Configuration (JSONB for flexibility)
    connection_config = models.JSONField(default=dict, blank=True, help_text="Connection settings, credentials, endpoints")
    
    # Scheduling & Automation
    sync_enabled = models.BooleanField(default=False, help_text="Enable automatic syncing")
    sync_schedule = models.CharField(max_length=100, blank=True, help_text="Cron expression (e.g., '0 2 * * *')")
    sync_timezone = models.CharField(max_length=50, default='UTC', help_text="Timezone for scheduling")
    
    # Sync Status & Health
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=20, blank=True, choices=SYNC_STATUS_CHOICES)
    next_sync_at = models.DateTimeField(null=True, blank=True)
    
    # Error Tracking & Health
    consecutive_failures = models.IntegerField(default=0)
    total_error_count = models.IntegerField(default=0)
    last_error_message = models.TextField(blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)
    health_score = models.IntegerField(default=100, help_text="0-100 health score based on recent performance")
    
    # Rate Limiting & Performance
    rate_limit_config = models.JSONField(default=dict, blank=True, help_text="Rate limiting and throttling settings")
    
    # Data Processing Settings
    data_processing_config = models.JSONField(default=dict, blank=True, help_text="Data processing and transformation settings")
    
    # Notification Settings
    notification_config = models.JSONField(default=dict, blank=True, help_text="Alert and notification configuration")
    
    # Integration Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional metadata and custom fields")
    
    # Statistics & Metrics
    total_records_processed = models.BigIntegerField(default=0)
    total_assets_created = models.IntegerField(default=0) 
    total_vulnerabilities_created = models.IntegerField(default=0)
    total_findings_created = models.IntegerField(default=0)
    average_sync_duration = models.FloatField(null=True, blank=True, help_text="Average sync time in minutes")
    
    # Feature Flags
    feature_flags = models.JSONField(default=dict, blank=True, help_text="Enable/disable specific features")
    
    class Meta:
        db_table = 'integrations'
        ordering = ['name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['integration_type']),
            models.Index(fields=['vendor']),
            models.Index(fields=['health_score']),
            models.Index(fields=['last_sync_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.vendor})" + (f" v{self.version}" if self.version else "")

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
        db_table = 'integration_field_mappings'
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
    file_hash = models.CharField(max_length=64, null=True, blank=True, 
                               help_text="SHA-256 hash for duplicate detection", db_index=True)
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
        constraints = [
            models.UniqueConstraint(
                fields=['file_hash'],
                name='unique_file_hash',
                condition=models.Q(file_hash__isnull=False)
            ),
        ]

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


class UserProfile(models.Model):
    """
    Extended user profile to store Supabase-specific information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    supabase_user_id = models.CharField(max_length=255, unique=True)
    business_group = models.ForeignKey(
        'BusinessGroup', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User's default business group for data access"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.supabase_user_id}"
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class SystemLog(models.Model):
    """System logs for monitoring application and infrastructure"""
    
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    LOG_SOURCES = [
        ('django', 'Django Application'),
        ('docker', 'Docker Container'),
        ('system', 'System'),
        ('nginx', 'Nginx'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.CharField(max_length=20, choices=LOG_LEVELS, db_index=True)
    source = models.CharField(max_length=50, choices=LOG_SOURCES, db_index=True)
    module = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_index=True
    )
    request_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['level']),
            models.Index(fields=['source']),
            models.Index(fields=['user']),
            models.Index(fields=['request_id']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} [{self.level}] {self.source}: {self.message[:100]}"


class IntegrationTemplate(models.Model):
    """Pre-configured integration templates for quick setup"""
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('coming_soon', 'Coming Soon'),
        ('beta', 'Beta'),
        ('deprecated', 'Deprecated'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    vendor = models.CharField(max_length=100)
    integration_type = models.CharField(max_length=20, choices=ScannerIntegration.INTEGRATION_TYPE_CHOICES)
    logo_url = models.URLField(blank=True)
    description = models.TextField()
    
    # Template Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Template Configuration
    default_config = models.JSONField(default=dict, help_text="Default connection configuration")
    required_fields = models.JSONField(default=list, help_text="List of required configuration fields")
    optional_fields = models.JSONField(default=list, help_text="List of optional configuration fields")
    field_mappings_template = models.JSONField(default=list, help_text="Pre-configured field mappings")
    
    # Setup Instructions
    setup_instructions = models.TextField(blank=True, help_text="Markdown formatted setup instructions")
    documentation_url = models.URLField(blank=True)
    support_contact = models.EmailField(blank=True)
    
    # Validation Rules
    validation_rules = models.JSONField(default=dict, help_text="Validation rules for configuration")
    
    # Capabilities
    capabilities = models.JSONField(default=list, help_text="List of integration capabilities")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integration_templates'
        ordering = ['vendor', 'name']
    
    def __str__(self):
        return f"{self.vendor} {self.name}"


class IntegrationSyncLog(models.Model):
    """Detailed logging for integration sync activities"""
    
    TRIGGER_TYPE_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('manual', 'Manual'),
        ('webhook', 'Webhook'),
        ('retry', 'Retry'),
    ]
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('partial', 'Partial Success'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled'),
    ]
    
    integration = models.ForeignKey(ScannerIntegration, on_delete=models.CASCADE, related_name='sync_logs')
    
    # Sync Session Details
    sync_id = models.UUIDField(unique=True, default=uuid.uuid4, help_text="Unique identifier for this sync session")
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPE_CHOICES)
    triggered_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Status & Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Statistics
    records_processed = models.IntegerField(default=0)
    records_created = models.IntegerField(default=0) 
    records_updated = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    # Error Details
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True, help_text="Detailed error information")
    
    # Performance Metrics
    performance_metrics = models.JSONField(default=dict, blank=True, help_text="Performance and timing metrics")
    
    # Sync Summary
    sync_summary = models.JSONField(default=dict, blank=True, help_text="Summary of sync results")
    
    class Meta:
        db_table = 'integration_sync_logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['integration', '-started_at']),
            models.Index(fields=['status']),
            models.Index(fields=['trigger_type']),
        ]
    
    def __str__(self):
        return f"{self.integration.name} sync {self.sync_id} - {self.status}"


class IntegrationAlert(models.Model):
    """Alert management for integration issues"""
    
    ALERT_TYPE_CHOICES = [
        ('sync_failure', 'Sync Failure'),
        ('consecutive_failures', 'Consecutive Failures'),
        ('health_degraded', 'Health Degraded'),
        ('quota_exceeded', 'Quota Exceeded'),
        ('connection_error', 'Connection Error'),
        ('data_quality_issue', 'Data Quality Issue'),
        ('performance_degraded', 'Performance Degraded'),
        ('configuration_error', 'Configuration Error'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('suppressed', 'Suppressed'),
    ]
    
    integration = models.ForeignKey(ScannerIntegration, on_delete=models.CASCADE, related_name='alerts')
    
    # Alert Details
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Alert Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Notification Status
    notifications_sent = models.JSONField(default=dict, blank=True, help_text="Track which notifications were sent")
    
    # Alert Metadata
    alert_data = models.JSONField(default=dict, blank=True, help_text="Additional alert context")
    
    # Timestamps
    first_occurred_at = models.DateTimeField(auto_now_add=True)
    last_occurred_at = models.DateTimeField(auto_now=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    occurrence_count = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'integration_alerts'
        ordering = ['-first_occurred_at']
        indexes = [
            models.Index(fields=['integration', 'status']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.integration.name}: {self.title} ({self.severity})"


class IntegrationQuota(models.Model):
    """API quota and usage tracking"""
    
    integration = models.OneToOneField(ScannerIntegration, on_delete=models.CASCADE, related_name='quota')
    
    # Quota Limits
    monthly_api_calls_limit = models.IntegerField(null=True, blank=True)
    daily_api_calls_limit = models.IntegerField(null=True, blank=True)
    hourly_api_calls_limit = models.IntegerField(null=True, blank=True)
    
    # Current Usage
    monthly_api_calls_used = models.IntegerField(default=0)
    daily_api_calls_used = models.IntegerField(default=0)
    hourly_api_calls_used = models.IntegerField(default=0)
    
    # Reset Timestamps
    last_monthly_reset = models.DateTimeField(auto_now_add=True)
    last_daily_reset = models.DateTimeField(auto_now_add=True)
    last_hourly_reset = models.DateTimeField(auto_now_add=True)
    
    # Quota Status
    quota_exceeded = models.BooleanField(default=False)
    quota_warning_sent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'integration_quotas'
    
    def __str__(self):
        return f"{self.integration.name} quota"
