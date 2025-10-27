# Generated migration for email verification token expiration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_add_oauth_notification_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_verification_token_expires',
            field=models.DateTimeField(
                blank=True,
                help_text='Expiration time for email verification token (24 hours from creation)',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(
                default=False,
                help_text='Whether the user has verified their email address',
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='email_verification_token',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Token for email verification (cleared after verification)',
                max_length=64,
            ),
        ),
    ]
