from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^clinic/$', views.get_clinic_detail, name='get_clinic_detail'),
    url(r'^new/$', views.new_item, name='new_item'),
]