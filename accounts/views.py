from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UserProfileForm, UserForm, PasswordForm

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    profile_form = UserProfileForm(instance=request.user.userprofile)
    user_form = UserForm(instance=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile, files=request.FILES)
        user_form = UserForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            return HttpResponseRedirect(reverse('accounts:profile'))
    return render(request, 'accounts/edit_profile.html', {'profile_form': profile_form, 'user_form': user_form})

@login_required
def change_password(request):
    user = request.user # type: User
    form = PasswordForm(user=user)
    if request.method == 'POST':
        form = PasswordForm(user=user, data=request.POST)
        if form.is_valid():
            new_pass = form.cleaned_data['new_password1']
            user.set_password(new_pass)
            user.save()
            user = authenticate(
                username=user.username,
                password=new_pass)
            login(request, user)
            messages.success(request, 'Your password successfully changed!')
            return HttpResponseRedirect(reverse('accounts:profile'))
    return render(request, 'accounts/change_password.html', {'form': form})

def sign_in(request):
    if request.user and str(request.user) != 'AnonymousUser':
        messages.success(
            request,
            "You're already logged in!"
        )
        return HttpResponseRedirect(
            reverse('home')
        )
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if form.user_cache is not None:
                user = form.user_cache
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(
                        reverse('accounts:profile')
                    )
                else:
                    messages.error(
                        request,
                        "That user account has been disabled."
                    )
            else:
                messages.error(
                    request,
                    "Username or password is incorrect."
                )
    return render(request, 'accounts/sign_in.html', {'form': form})

def sign_up(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            messages.success(
                request,
                "You're now a user! You've been signed in, too."
            )
            return HttpResponseRedirect(reverse('accounts:profile'))
    return render(request, 'accounts/sign_up.html', {'form': form})

@login_required
def sign_out(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return HttpResponseRedirect(reverse('home'))