from django.db import migrations, models
import django.contrib.postgres.fields

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vulnerability',
            name='published_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vulnerability',
            name='modified_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vulnerability',
            name='references',
            field=models.JSONField(default=list, blank=True),
        ),
        migrations.AddField(
            model_name='vulnerability',
            name='risk_factor',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vulnerability',
            name='exploit',
            field=models.JSONField(default=dict, blank=True),
        ),
        migrations.AddField(
            model_name='vulnerability',
            name='cvss',
            field=models.JSONField(default=dict, blank=True),
        ),
    ] 