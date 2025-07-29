from .models import WikiSpace


def site_wide_context(request):

    return {
        'all_spaces': WikiSpace.objects.all().order_by('name'),
        'sess_space_key': request.session.get('sess_space_key'),
    }