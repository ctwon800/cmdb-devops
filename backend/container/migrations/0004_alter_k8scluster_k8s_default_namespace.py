# Generated by Django 4.2.13 on 2024-08-13 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('container', '0003_k8scluster_k8s_default_namespace'),
    ]

    operations = [
        migrations.AlterField(
            model_name='k8scluster',
            name='k8s_default_namespace',
            field=models.CharField(blank=True, default='default', help_text='k8s_default_namespace', max_length=255, verbose_name='k8s_default_namespace'),
        ),
    ]
