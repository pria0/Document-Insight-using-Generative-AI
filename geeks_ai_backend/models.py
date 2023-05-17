from django.db import models
from django.utils.translation import gettext_lazy as _

class ActivityTracking(models.Model):
    active = models.BooleanField(verbose_name=_('Active'), default=True)
    is_deleted = models.BooleanField(verbose_name=_('Is Deleted'), default=False)
    created_at = models.DateTimeField(verbose_name=_('Created At'),
                    auto_now_add=True, help_text=_("Date when created."), null=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),
                    auto_now=True, help_text=_("Date when updated."), null=True)
    deleted_at = models.DateTimeField(verbose_name=_('Deleted At'),
                    default=None, null=True, blank=True, help_text=_("Date when deleted"))
    delete_reason = models.CharField(max_length=300, verbose_name=_('Delete Reason'),
                    default=None, null=True, blank=True, help_text=_("Delete Reason"))

    class Meta:
        abstract = True