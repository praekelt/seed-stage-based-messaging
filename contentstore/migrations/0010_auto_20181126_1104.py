# Generated by Django 2.1.2 on 2018-11-26 11:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contentstore', '0009_add_messageset_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageset',
            name='default_schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='message_sets', to='contentstore.Schedule'),
        ),
        migrations.AlterField(
            model_name='messageset',
            name='label',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='User-readable name'),
        ),
        migrations.AlterField(
            model_name='messageset',
            name='next_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contentstore.MessageSet'),
        ),
    ]