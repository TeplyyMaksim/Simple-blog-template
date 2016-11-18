# Library from where we call
# function, that parses our
# texts in sharable format
# for web (Social links)
from urllib import quote_plus
# Django template library
from django import template

# Creating class object,
# what allows us to add 
# functionality in our template
register = template.Library()

# Registration function urlify
# As a filter for templates
# By using decorator
@register.filter
def urlify(value):
	return quote_plus(value.encode('utf8'))