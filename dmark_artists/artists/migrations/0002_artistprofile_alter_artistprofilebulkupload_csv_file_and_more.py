# Generated by Django 4.0.2 on 2022-03-18 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.CharField(max_length=120)),
                ('song', models.CharField(max_length=120)),
                ('price', models.IntegerField()),
                ('downloads', models.IntegerField(default=0)),
                ('total_amount', models.IntegerField(default=0)),
                ('month', models.CharField(max_length=120)),
                ('year', models.IntegerField()),
                ('company', models.CharField(max_length=120)),
            ],
        ),
        migrations.AlterField(
            model_name='artistprofilebulkupload',
            name='csv_file',
            field=models.FileField(upload_to='artists/bulkupload/%Y%m'),
        ),
        migrations.AlterField(
            model_name='artistprofilebulkupload',
            name='date_uploaded',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='artistprofilebulkupload',
            name='uploaded',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_data', to='artists.artistprofile'),
        ),
    ]
