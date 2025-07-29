from django.urls import include, path

# the app urls.py must be include()d to pick up the route namespace ie 'djwiki'

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('wikiwikiweb.urls')),
]
