# Generated by Django 3.2 on 2021-05-10 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bucket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('LD_limit', models.CharField(max_length=50)),
                ('bucket', models.CharField(max_length=100)),
                ('stage', models.CharField(max_length=50)),
            ],
        ),
    ]
