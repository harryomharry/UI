from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models


# HD- what does an instance of "current" class do? any links to where (template file, views etc.) 
# an instance is being used.. e.g. def campaign_send(request) in views.py 

@python_2_unicode_compatible
class current(models.Model):
	campaign_id = models.CharField(max_length=200)
	vendor_id = models.CharField(max_length=200)
	clientname = models.CharField(max_length=200)
	clientnum = models.CharField(max_length=200)
	offer_id = models.CharField(max_length=200)
	offernum = models.CharField(max_length=200)
	product_id = models.CharField(max_length=200)

	
	def __str__(self):
		return self.campaign_id


from django.contrib.auth.models import User
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)


    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username