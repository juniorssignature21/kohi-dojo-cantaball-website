from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import RegisterUserForm

# Create your views here.
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
            return redirect('app:home')

        else:
            messages.success(request, 'Invalid Email or Password!!')
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
            return redirect('app:home')
        
        else:
            errors = next(iter(form.errors.values()))[0]
            print(errors)  # Log errors for debugging
            messages.error(request, errors)
            return redirect('register')
        
    context = {
        'form':form
    }
    return render(request, 'register.html', context)
