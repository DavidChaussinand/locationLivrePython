# Generated by Django 5.1.1 on 2024-09-25 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_livre_categorie_commentaire'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentaire',
            name='note',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=2),
        ),
    ]
