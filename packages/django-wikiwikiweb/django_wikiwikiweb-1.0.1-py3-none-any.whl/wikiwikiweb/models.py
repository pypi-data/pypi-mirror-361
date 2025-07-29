from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords


class WikiSpace(models.Model):

    spaceid = models.AutoField(primary_key=True)
    name = models.SlugField(default='', null=False)
    description = models.TextField(blank=True, null=True)
    homepage = models.ForeignKey('WikiPage', blank=True, null=True, on_delete=models.PROTECT)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Wiki Space'
        ordering = ['name']

    def __str__(self):
        return self.name


class WikiPage(models.Model):

    name = models.CharField('Page Name', max_length=255, primary_key=True)
    space = models.ForeignKey(WikiSpace, on_delete=models.PROTECT, default=1)
    content = models.TextField('Page Content', blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    updated = models.DateTimeField(blank=False, null=False, auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pagescreated')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pagesupdated')

    #updated = models.DateTimeField(blank=False, null=False, auto_now=True)
    edit_reason = models.CharField('Reason for Edit', max_length=256, default='Created')
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Wiki Page'

    def __str__(self):
        return self.name
