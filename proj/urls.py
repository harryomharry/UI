from django.conf.urls import url
from django.conf.urls import patterns, url

from . import views

# HD- When a user makes a request for a page, Django controller takes over to look 
# for the corresponding view via the url.py file, and then return the HTML response 
# or a 404 not found error, if not found. "urlpatterns" tuple has three elements
# -- regex Pattern for mapping url; call relevant views module; name

urlpatterns = [

    # current_test
    #url(r'^$', views.index, name='index'),
	
## HD- provide a little structure to the various urls. either here or in the documentation

    url(r'^home/$', views.welcome, name='welcome'),
    url(r'^home/Morrison/campaigns/$', views.campaign_send, name='campaign'),
    url(r'^home/campaign_receive/$', views.campaign_receive, name='campaign_receive'),
    url(r'^home/Morrison/campaigns/suppliers/$', views.vendor_send, name='vendors'),
    url(r'^home/vendor_receive/$', views.vendor_receive, name='vendor_receive'),
    url(r'^home/Morrison/campaigns/suppliers/offers$', views.offer_send, name='offers'),
    url(r'^home/offer_receive/$', views.offer_receive, name='offer_receive'),
    url(r'^home/Morrison/campaigns/suppliers/offers/products$', views.product_send, name='products'),
    url(r'^home/product_receive/$', views.product_receive, name='product_receive'),
    url(r'^home/test/$', views.test, name='test'),
    url(r'^home/excel_file_export/$', views.excel_file, name='excel_file_export'),
    url(r'^home/Morrison/file_download/$', views.export_page, name='export_page'),

    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),

]
