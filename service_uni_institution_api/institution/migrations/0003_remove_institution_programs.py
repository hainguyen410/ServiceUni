# Generated by Django 4.2.5 on 2023-10-02 21:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0002_academicsession_alter_school_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institution',
            name='programs',
        ),
    ]