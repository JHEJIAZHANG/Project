# Generated migration for FileAttachment model changes

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_v2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileattachment',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='fileattachment',
            name='object_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]