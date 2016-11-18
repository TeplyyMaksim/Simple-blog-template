# I don't have an idea what this import does
from __future__ import unicode_literals
# Models themselves
from django.db import models
# I import settings for using
# Auth users application
from django.conf import settings
# For new manager
from django.utils import timezone
# Signals import
from django.db.models.signals import pre_save, pre_delete
# Every post has to have his own url
from django.core.urlresolvers import reverse
# __unicode__ and __str__ support
from django.utils.encoding import python_2_unicode_compatible
# slug creator function
# it's more powerful then
# classic django slugify
from uuslug import slugify


# Function that shows where and how file should be saved
def upload_location(instance, filename):
	return "{folder}/{filename}".format(folder=instance.slug, filename=filename)

# ----------------------------------------------------------------------


# Managers live here
# Manager looks like .all()
# In Model.objects.all()
# .create(), .delete() are
# managers too
class PostManager(models.Manager):
	# Rewriting all method
	# in code below
	# def all(self, *args, **kwargs):
	#	return super(PostManager, self).filter(publis__lte=timezone.now())
	
	def actual(self, *args, **kwargs):
		return self.all().exclude(late_publish__gt=timezone.now())

# ----------------------------------------------------------------------


# Models live here
# Decorator for __unicode__ and __str__
@python_2_unicode_compatible
class Post(models.Model):
	title = models.CharField(max_length=30)
	slug = models.SlugField(unique=True, blank=True, null=True)
	image = models.ImageField(
		upload_to=upload_location,
		null=True, 
		blank=True
	)
	content = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
	# Field for author of the post
	# It is foreign key from table
	# With authorisation and default
	# Author will be first user (admin)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
	# Field for creating post
	# in future
	late_publish = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)

	# Link to custom manager
	# objects is convention to 
	# name this variable, but if I
	# change name I should use
	# Post.another_name.active()
	objects = PostManager()
	
	# Everything thats don't mess with fields
	class Meta:
		ordering = ['-timestamp']
	
	# We don't need __unicode__ with decorator and imort,
	# just __str__ function
	def __str__(self):
		return u'{ttl}'.format(ttl=self.title)
	
	# Every Post has his own path now
	def get_absolute_url(self):
		return reverse('blog:detail', kwargs={'slug': self.slug})


# ----------------------------------------------------------------------


# Function that creates slugs
# It can call itself
def create_slug(instance, new_slug=None):
	# Slugifying title
	slug = slugify(instance.title)
	# Checking for comming new slug
	# It'll come if recursion occurs
	if new_slug is not None:
		slug = new_slug
	# Check for other slugs
	qs = Post.objects.filter(slug=slug).order_by('-id')
	exists = qs.exists()
	# If exists function runs again
	if exists:
		new_slug = "%s-%s"%(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)
	# If doesn't exist it return slug back
	return slug


# Function that goes before saving Post
def pre_save_post_receiver(sender, instance, *args, **kwargs):
	if (not instance.slug) or (instance.slug==None) or (instance.slug==''):
		instance.slug = create_slug(instance)

# Function that summons before deleting Post
def pre_delete_post(sender, instance, *args, **kwargs):
	if not(instance.image is None):
		instance.image.delete(save=True)
	
# This expression connects 	
pre_save.connect(pre_save_post_receiver, sender=Post)
pre_delete.connect(pre_delete_post, sender=Post)