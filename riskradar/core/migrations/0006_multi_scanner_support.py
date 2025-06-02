# Generated migration for multi-scanner support
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    
    dependencies = [
        ('core', '0005_alter_vulnerability_cvss'),
    ]
    
    operations = [
        # 1. Add missing scanner integration type
        migrations.AddField(
            model_name='scannerintegration',
            name='type',
            field=models.CharField(max_length=50, default='vuln_scanner', 
                                 help_text="e.g., 'vuln_scanner', 'asset_inventory'"),
        ),
        
        # 2. Re-add CVE support to vulnerabilities
        migrations.AddField(
            model_name='vulnerability',
            name='cve_id',
            field=models.CharField(max_length=50, null=True, blank=True, db_index=True),
        ),
        
        # 3. Add external_source for multi-scanner support
        migrations.AddField(
            model_name='vulnerability',
            name='external_source',
            field=models.CharField(max_length=50, null=True, blank=True,
                                 help_text="Scanner name (e.g., 'Nessus', 'Qualys')"),
        ),
        
        # 4. Add normalised severity fields
        migrations.AddField(
            model_name='vulnerability',
            name='severity_level',
            field=models.SmallIntegerField(null=True, blank=True,
                                         help_text="Normalised severity 0-10"),
        ),
        migrations.AddField(
            model_name='vulnerability',
            name='severity_label',
            field=models.CharField(max_length=20, default='Medium',
                                 choices=[('Info', 'Info'), ('Low', 'Low'), 
                                        ('Medium', 'Medium'), ('High', 'High'), 
                                        ('Critical', 'Critical')]),
        ),
        
        # 5. Add missing asset fields
        migrations.AddField(
            model_name='asset',
            name='operating_system',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='mac_address',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        
        # 6. Add integration reference to findings
        migrations.AddField(
            model_name='finding',
            name='integration',
            field=models.ForeignKey(
                null=True,  # Allow null during migration
                on_delete=django.db.models.deletion.CASCADE,
                related_name='findings',
                to='core.scannerintegration',
                help_text="Scanner that discovered this finding"
            ),
        ),
        
        # 7. Add severity_level to findings
        migrations.AddField(
            model_name='finding',
            name='severity_level',
            field=models.SmallIntegerField(null=True, blank=True,
                                         help_text="Normalised severity 0-10"),
        ),
        
        # 8. Add internal_severity_level to severity mapping
        migrations.AddField(
            model_name='severitymapping',
            name='internal_severity_level',
            field=models.SmallIntegerField(default=5,
                                         help_text="Normalised severity 0-10"),
        ),
        
        # 8.5. Update SeverityMapping unique constraint before renaming fields
        migrations.AlterUniqueTogether(
            name='severitymapping',
            unique_together=set(),
        ),
        
        # 9. Rename fields for clarity
        migrations.RenameField(
            model_name='vulnerability',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='vulnerability',
            old_name='solution',
            new_name='fix_info',
        ),
        migrations.RenameField(
            model_name='vulnerability',
            old_name='metadata',
            new_name='extra',
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='metadata',
            new_name='extra',
        ),
        migrations.RenameField(
            model_name='finding',
            old_name='metadata',
            new_name='details',
        ),
        migrations.RenameField(
            model_name='severitymapping',
            old_name='source_value',
            new_name='external_severity',
        ),
        migrations.RenameField(
            model_name='severitymapping',
            old_name='target_value',
            new_name='internal_severity_label',
        ),
        
        # 9.5. Restore SeverityMapping unique constraint with new field names
        migrations.AlterUniqueTogether(
            name='severitymapping',
            unique_together={('integration', 'external_severity')},
        ),
        
        # 10. Update unique constraints - remove old unique_together first
        migrations.AlterUniqueTogether(
            name='finding',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='finding',
            constraint=models.UniqueConstraint(
                fields=['asset', 'vulnerability', 'integration', 'port', 'protocol', 'service'],
                name='unique_finding_per_scanner'
            ),
        ),
        
        # 11. Add vulnerability constraints
        migrations.AddConstraint(
            model_name='vulnerability',
            constraint=models.UniqueConstraint(
                fields=['cve_id'],
                name='unique_cve_id',
                condition=models.Q(cve_id__isnull=False)
            ),
        ),
        migrations.AddConstraint(
            model_name='vulnerability',
            constraint=models.UniqueConstraint(
                fields=['external_source', 'external_id'],
                name='unique_external_vuln',
                condition=models.Q(external_source__isnull=False, external_id__isnull=False)
            ),
        ),
        
        # 12. Update asset unique constraint for better deduplication
        migrations.AlterUniqueTogether(
            name='asset',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='asset',
            constraint=models.UniqueConstraint(
                fields=['hostname', 'ip_address'],
                name='unique_hostname_ip',
                condition=models.Q(hostname__isnull=False, ip_address__isnull=False)
            ),
        ),
    ] 