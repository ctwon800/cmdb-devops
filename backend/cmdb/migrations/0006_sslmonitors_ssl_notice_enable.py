# Generated by Django 3.2.19 on 2024-05-10 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0005_rename_ssl_expire_date_sslmonitors_ssl_expire_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='sslmonitors',
            name='ssl_notice_enable',
            field=models.CharField(default='是', help_text='是否开启通知', max_length=255, null=True, verbose_name='是否开启通知'),
        ),
    ]