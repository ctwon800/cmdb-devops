# Generated by Django 4.2.13 on 2024-07-30 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('container', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='k8scluster',
            name='k8s_cluster_is_default',
            field=models.BooleanField(default=False, help_text='k8s_cluster_is_default', verbose_name='k8s_cluster_is_default'),
        ),
    ]