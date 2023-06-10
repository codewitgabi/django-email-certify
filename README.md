# Project Description

`email_verification` is a django package that verifies a user's email on registration.

- An email is sent to registered users to verify their email before login. 
- All users that are not verified after 24hrs will be automatically deleted from the database.

# Installation

```
pip install django-email-certify
```

## Setup
After a successful installation, you will need to setup your django project to use the package. Follow the steps below to do that.

First, we need to add `email_verification` to our project's `INSTALLED_APPS`

```
# settings.py

INSTALLED_APPS = [
    # ...other apps
    "email_verification.apps.EmailVerificationConfig",
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_HOST_USER = "your_email_user"
EMAIL_HOST_PASSWORD = "your_email_password"
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = "Default<no_reply@domain.com>"

LOGIN_URL = "" # ensure to set this
```

Next, we will add the url configuration for our package.

```
# urls.py

urlpatterns = [
    # ...other urls
    path("verify-email/", include("email_verification.urls")),
]
```

```
python manage.py migrate
```

Next, we'll need to handle inactive user deletion for our project. To do that, we will be adding some configuration to our `wsgi.py` file

```
# wsgi.py

from threading import Thread

application = get_wsgi_application() # already in code

# this should come after the get_wsgi_application() object
from email_verification.views import delete_inactive_users

t = Thread(target=delete_inactive_users)
t.start()
```

That's all for the configurations. Next up, we will be using verifying our users using a django form

```
# views.py

from email_verification.views import VerifyEmail

def signup(request):
    form = RegisterForm() # create your form class
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            VerifyEmail(request, form)
    
    return render(request, "register.html", {"form": form})
```

