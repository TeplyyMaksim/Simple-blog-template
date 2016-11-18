# The most comfortable imports
from django.shortcuts import render, get_object_or_404, redirect
# messages
from django.contrib import messages
# Work with HTTP
from django.http import HttpResponseRedirect, Http404
# CBView
from django.views import View
# For draftchecking
from django.utils import timezone
# For searching
from django.db.models import Q
# paginators import
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Post
from .forms import PostForm

# ----------------------------------------------------------------------


# Views live here
# First is home view
# For all posts
def home(request):	
	# global unpaged queryset
    # if statement pull all posts
    # for site stuff and only
    # undrafted posts for users
	if not(request.user.is_staff) or not(request.user.is_superuser):
		# Comment below showing sorting
		# by using base filtering
		# queryset_list = Post.objects.exclude(late_publish__gt=timezone.now())
		queryset_list = Post.objects.actual()
	else:
		queryset_list = Post.objects.all()
	
	# Getting actual search stuff
	# From search input with name q
	# And using Q searching system
	# .distinct() prevents repeating
	query = request.GET.get('q')
	if query:
		queryset_list = queryset_list.filter(
			Q(title__icontains=query) |
			Q(content__icontains=query) |
			Q(user__first_name__icontains=query) |
			Q(user__last_name__icontains=query)
		).distinct()
	# It is refreshing cicle for
	# returning drafted posts in the
	# right order with other posts
	# and it works!!!
	for post in [query for query in queryset_list if not query.late_publish is None]:
		if post.late_publish < timezone.now():
			post.timestamp = post.late_publish
			post.late_publish = None
			post.save()
	
	
	# creating Paginator
	paginator = Paginator(queryset_list, 5) # Show 5 contacts per page
	# getting request from User
	page = request.GET.get('page')
	
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)
	context={
		"actual_datetime": timezone.now(),
		"title": 'Best coffee blog ever',
		"post_list": queryset,
	}
	return render(request, 'home.html', context)

# Detail view in
# Function based view
# Representing
def detail(request, slug=None):
	# Return 404 error if user
	# wants to look post, that
	# is in draft
	post = get_object_or_404(Post, slug=slug)
	if not(post.late_publish is None) and(post.late_publish > timezone.now()) and (not(request.user.is_staff) or not(request.user.is_superuser)):
		raise Http404
	context = {
		"actual_datetime": timezone.now(),
		'post': post,
	}
	return render(request, 'detail.html', context)


# Create view in
# Class based view
# Representing
class CreateView(View):
	
	def get(self, request, *args, **kwargs):
		if not(request.user.is_staff) or not(request.user.is_superuser):
			raise Http404
		form = PostForm()
		context = {
			'form': form,
		}
		return render(request, 'post_form.html', context)
	
	def post(self, request, *args, **kwargs):
		if not(request.user.is_staff) or not(request.user.is_superuser):
			raise Http404
		form = PostForm(request.POST or None, request.FILES or None)
		if form.is_valid():
			instance = form.save(commit=False)
			# The user which creates Post
			# Become it's author
			instance.user = request.user
			instance.save()
			# Message success
			messages.success(request, "Successfully Created", extra_tags='test_extra_tag')			
			return HttpResponseRedirect(instance.get_absolute_url())
		# Message invalid input
		messages.error(request, "Not successfully Created")
		context = {
			'form': form,
		}
		return render(request, 'post_form.html', context)


# Update view in
# Function based view
# Representing
class UpdateView(View):
	
	def get(self, request, slug=None, *args, **kwargs):
		if not(request.user.is_staff) or not(request.user.is_superuser):
			raise Http404
		post = get_object_or_404(Post, slug=slug)
		form = PostForm(request.FILES or None, instance=post)
		context = {
			'post': post,
			'form': form,
		}
		return render(request, 'post_form.html', context)
	
	def post(self, request, slug=None, *args, **kwargs):
		if not(request.user.is_staff) or not(request.user.is_superuser):
			raise Http404
		post = get_object_or_404(Post, slug=slug)
		form = PostForm(request.POST or None, request.FILES or None, instance=post)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			# Message success
			messages.success(request, "Successfully Updated")
			return HttpResponseRedirect(instance.get_absolute_url())
		# Message success
		messages.success(request, "Not successfully Updated")
		context = {
			'form': form,
		}
		return render(request, 'post_form.html', context)


# Delete view in
# Function based view
# Representing
def delete(request, slug=None):
	if not(request.user.is_staff) or not(request.user.is_superuser):
		raise Http404
	post = get_object_or_404(Post, slug=slug)
	# Deleting posts image goes
	# From models signals and this
	# Function is not required now
	# post.image.delete(save=False)
	
	post.delete()
	# Message success deletind
	messages.success(request, "Successfully Deleted")
	return redirect('blog:home')