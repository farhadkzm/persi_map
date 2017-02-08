from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^new/$', views.new_item, name='new_item'),
]