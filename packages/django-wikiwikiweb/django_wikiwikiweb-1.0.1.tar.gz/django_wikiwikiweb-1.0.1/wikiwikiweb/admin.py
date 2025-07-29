from django.contrib import admin

from .models import *


@admin.register(WikiPage)
class WikiPageAdmin(admin.ModelAdmin):

    list_display = ['name', 'space', 'updated']
    ordering = ['-updated']

    list_filter = ['space']
    show_facets = admin.ShowFacets.ALWAYS
    search_fields = ['name'] #, 'desc_hline', 'performance__artist__title']

    fields = [
            'name',
            'space',
            'content',
            'edit_reason',
            'created_by',
            'updated_by',
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('name',)
        return self.readonly_fields


@admin.register(WikiSpace)
class WikiSpaceAdmin(admin.ModelAdmin):

    list_display = ['name', 'homepage']

    fields = [
            'name',
            'description',
            'homepage',
    ]

    def get_form(self, request, obj=None, **kwargs):
        """Customise the homepage widget"""

        form = super(WikiSpaceAdmin, self).get_form(request, obj, **kwargs)
        field = form.base_fields['homepage']

        # Disable spurious/troublesome actions
        field.widget.can_add_related = False
        field.widget.can_view_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False

        # Filter options to this space
        field.queryset = WikiPage.objects.filter(space=obj)

        return form
