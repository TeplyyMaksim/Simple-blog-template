from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^create/$', views.CreateView.as_view(), name='create'),
	url(r'^(?P<slug>[\w-]+)/edit/$', views.UpdateView.as_view(), name='edit'),
	url(r'^(?P<slug>[\w-]+)/delete/$', views.delete, name='delete'),
	url(r'^(?P<slug>[\w-]+)/$', views.detail, name='detail'),
]