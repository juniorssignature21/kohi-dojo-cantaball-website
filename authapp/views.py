from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_http_methods

from .forms import RegisterUserForm
from .email import send_resend_email

User = get_user_model()


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


def custom_500_view(request):
    return render(request, '500.html', status=500)


def custom_403_view(request, exception):
    return render(request, '403.html', status=403)


def custom_400_view(request, exception):
    return render(request, '400.html', status=400)


def custom_401_view(request, exception):
    return render(request, '401.html', status=401)


def custom_405_view(request, exception):
    return render(request, '405.html', status=405)


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            messages.success(request, 'Login Successful!!')

            if next_url:
                return redirect(next_url)
            return redirect('store:shop')

        messages.error(request, 'Invalid Email or Password!!')
        return redirect('login')

    return render(request, 'login.html')


def register(request):
    form = RegisterUserForm()
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)

            messages.success(request, 'Registration and login successful!')
            return redirect('store:shop')

        errors = next(iter(form.errors.values()))[0]
        print(errors)
        messages.error(request, errors)
        return redirect('register')

    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('store:shop')


def _build_password_reset_url(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = f"/auth/reset-password/{uid}/{token}/"
    if not settings.DEBUG and settings.SITE_URL:
        base = settings.SITE_URL.rstrip('/')
    else:
        base = request.build_absolute_uri('/').rstrip('/')
    return f"{base}{path}"


@require_http_methods(["GET", "POST"])
def forgot_password(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        success_msg = (
            "If an account exists for that email, a password reset link has been sent."
        )

        if not email:
            messages.error(request, "Please enter your email address.")
            return redirect("forgot_password")

        user = User.objects.filter(email__iexact=email).first()
        if user:
            reset_url = _build_password_reset_url(request, user)
            html = render_to_string(
                "authapp/password_reset_email.html",
                {"user": user, "reset_url": reset_url},
            )
            text = (
                f"Reset your Kohi Dojo password:\n\n{reset_url}\n\n"
                "If you did not request this, ignore this email."
            )
            result = send_resend_email(
                to=user.email,
                subject="Reset your Kohi Dojo password",
                html=html,
                text=text,
            )
            if result is None:
                messages.error(
                    request,
                    "We couldn't send the reset email right now. Please try again shortly.",
                )
                return redirect("forgot_password")

        messages.success(request, success_msg)
        return redirect("login")

    return render(request, "forgot_password.html")


def _get_user_from_uidb64(uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


@require_http_methods(["GET", "POST"])
def reset_password(request, uidb64, token):
    user = _get_user_from_uidb64(uidb64)
    if user is None or not default_token_generator.check_token(user, token):
        return render(request, "reset_password_invalid.html")

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password updated. You can log in now.")
            return redirect("login")
    else:
        form = SetPasswordForm(user)

    for field in form.fields.values():
        field.widget.attrs.update({"class": "form-control auth-input"})

    return render(request, "reset_password.html", {"form": form, "user": user})
