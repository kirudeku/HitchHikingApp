# Generated by Django 4.1.7 on 2023-05-03 08:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0004_remove_posting_cover'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'ordering': ['-created_at'], 'verbose_name': 'Rezervacija', 'verbose_name_plural': 'Rezervacijos'},
        ),
        migrations.AlterModelOptions(
            name='posting',
            options={'ordering': ['-created_at'], 'verbose_name': 'Skelbimas', 'verbose_name_plural': 'Skelbimai'},
        ),
        migrations.AlterField(
            model_name='booking',
            name='posting',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.posting'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='posting',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posting', to=settings.AUTH_USER_MODEL),
        ),
    ]
