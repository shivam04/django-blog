from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
	url(r'^$', "posts.views.posts_list",name="lists"),
    url(r'^create/$', "posts.views.posts_create"),
    url(r'^(?P<slug>[\w-]+)/$', "posts.views.posts_detail",name="detail"),
    url(r'^(?P<slug>[\w-]+)/edit/$', "posts.views.posts_update",name="update"),
    url(r'^(?P<slug>[\w-]+)/delete/$', "posts.views.posts_delete"),

]
