# Generated by Django 4.0.2 on 2022-03-18 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0002_artistprofile_alter_artistprofilebulkupload_csv_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistprofilebulkupload',
            name='month',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='artistprofilebulkupload',
            name='year',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
