from django.urls import path

from . import views

app_name = 'djwiki'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('<str:page_name>/<int:pk>', views.PageArchiveView.as_view(), name='page_archive'),
    path('space/select', views.SpaceSelectView.as_view(), name='space_select'),
    path('space:<slug:slug>', views.SpaceView.as_view(), name='space'),
    path('user:<str:profileusername>', views.UserProfileView.as_view(), name='user'),
    path('<str:pk>/edit', views.PageEditView.as_view(), name='page_edit'),
    path('search', views.SearchView.as_view(), name='search'),
    path('mywiki', views.MyView.as_view(), name='mywiki'), # unlinked so far

    # Always last, as we fall back to this by default
    path('<str:pk>', views.PageView.as_view(), name='page_view'),
]
