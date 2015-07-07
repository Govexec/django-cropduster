from django.conf.urls.defaults import patterns, url
import os

urlpatterns = patterns('',
	url(r'^_static/(?P<path>.*)$', "django.views.static.serve", {"document_root": os.path.dirname(__file__) + "/media"}, name='cropduster-static'),
	
	url(r'^upload/$', "cropduster2.views.upload", name='cropduster-upload'),
	
	url(r'^ratio/$', "cropduster2.views.get_ratio", name='cropduster-ratio'),
	
)
