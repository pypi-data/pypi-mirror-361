import re

from django import template
from django.urls import reverse

from ..models import WikiPage


register = template.Library()

# I've tried to enforce https://wiki.c2.com/?WikiCase as far as sensible
# There will be omissions/exceptions
FMT_WIKINAME = r'(?<![=/])\b[A-Z]+[a-zA-Z0-9]+[A-Z][a-zA-Z0-9]+\b'


@register.filter
def linkify(pagetext):

    wikinames = set(re.findall(FMT_WIKINAME, pagetext))

    for item in wikinames:
        my_regex = r"\b(?=\w)" + re.escape(item) + r"\b(?!\w)"
        pagetext = re.sub(my_regex, _make_link(item), pagetext)

    return pagetext


def _make_link(wikiname):

    try:
        obj = WikiPage.objects.get(name=wikiname)
        page_exists = True
    except:
        page_exists = False

    # TODO: proper string formatting

    url = reverse('djwiki:page_view', kwargs={'pk': wikiname})

    link = '<span class="wikilink"><a href="' + url + '"'

    if not page_exists:
        link = link + ' class="newpage"'

    link = link + '>' + wikiname + '</a></span>'

    return link

@register.filter
def make_title(wikiname):
    # See: https://stackoverflow.com/questions/199059/a-pythonic-way-to-insert-a-space-before-capital-letters
    # return re.sub(r"(\w)([A-Z])", r"\1 \2", wikiname)
    return re.sub(r"(?<=\w)([A-Z])", r" \1", wikiname)
