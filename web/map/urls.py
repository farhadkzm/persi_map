from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^api/delete_item', views.api_delete_item),
    url(r'^api/admin/delete_item', views.api_admin_delete_item),
    url(r'^api/create_item', views.api_create_update_item),
    url(r'^api/search$', views.api_search),
    url(r'^service/edit$', views.edit_service),
    url(r'^service/admin/sec/items$', views.admin_items),
    url(r'^service/new$', views.new_service),
    url(r'^$', views.index),
]
