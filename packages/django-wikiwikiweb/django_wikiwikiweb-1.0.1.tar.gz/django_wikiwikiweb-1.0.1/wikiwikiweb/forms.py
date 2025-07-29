from django.forms import (
    Form, ModelChoiceField, ModelForm
)

from .models import WikiPage, WikiSpace


# TODO: consider whether there should even be a name field. Maybe the ONLY way
# people should get here is via viewing a non-existent (yet) page. Thus, the
# view wouldn't even need its own route in urls.py. Also we wouldn't need to
# think about name clashes
class PageCreateForm(ModelForm):

    class Meta:
        model = WikiPage
        fields = ['content', 'edit_reason']


class PageEditForm(ModelForm):

    def __init__(self, *args, **kwargs):
        """ There MUST be a simpler way to override a simple input value"""

        initial = kwargs.get('initial', {})
        initial['edit_reason'] = ''
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    class Meta:
        model = WikiPage
        fields = ['content', 'edit_reason']


class SpaceSelectForm(Form):

    space_choice = ModelChoiceField(
                        queryset=WikiSpace.objects.all(),
                        label='Please select a space:',
                    )
