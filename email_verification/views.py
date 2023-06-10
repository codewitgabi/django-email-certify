from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import Token
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.timesince import timesince
import sys

User = get_user_model()

def delete_inactive_users():
	"""
	Delete inactive users after 24 hours.
	"""
	
	allowed_times = [
		"day", "days",
		"week", "weeks",
		"month", "months",
	]
	
	while True:
		# get users with is_active as False
		inactive_users = User.objects.filter(is_active=False)
			
		for user in inactive_users:
			user_date_joined =timesince(user.date_joined).split(", ")[0].split()[-1]
			
			if user_date_joined in allowed_times:
				sys.stdout.write(f"[INFO] Deleted <User: {user.id}>....\n")
				user.delete()
				

@transaction.atomic(durable=True, savepoint=False)
def VerifyEmail(request, form):
	"""
	request:
		holds the request content sent to this view.
	form:
		this parameter holds the register form data when the register form is submitted.
	rtype: instance of the created user
	"""
	subject = "Verify Your Email"
	user = form.save(commit=False)
	email = user.email
	user.is_active = False
	user.save()
	
	token = Token.objects.create(user=user)
	token.save()
	
	html_content = render_to_string("email_verification/mail.html", {"token": token}, request=request)

	mail = EmailMessage(
		subject,
		html_content,
		to=[email]
	)
	
	mail.content_subtype = "html"
	mail.fail_silently = False
	mail.send()

	return user


@transaction.atomic(durable=True, savepoint=False)
def pre_login(request, token):
	"""
	token:
		user verification token unique to every user.
	"""
	token = get_object_or_404(Token, id=token)
	if not token.has_expired:
		user = token.user
		user.is_active = True
		user.save()
		return render(
			request,
			"email_verification/pre-login-success.html",
			{"login_url": settings.LOGIN_URL}
		)
	return render(
		request, "email_verification/pre-login-failure.html")

