# Generated by Django 4.1.7 on 2023-05-03 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_review_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='posting',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='posts.posting'),
        ),
    ]
