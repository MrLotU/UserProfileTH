from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import PasswordForm, UserForm, UserProfileForm


@login_required
def profile(request):
    """Renders a users profile"""
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    """Renders profile editing page"""
    # Create the forms
    profile_form = UserProfileForm(instance=request.user.userprofile)
    user_form = UserForm(instance=request.user)
    # Check method
    if request.method == 'POST':
        # Create the forms
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile, files=request.FILES)
        user_form = UserForm(request.POST, instance=request.user)
        # Validate
        if profile_form.is_valid() and user_form.is_valid():
            # Save
            profile_form.save()
            user_form.save()
            # Redirect to profile
            return HttpResponseRedirect(reverse('accounts:profile'))
    # Render template
    return render(request, 'accounts/edit_profile.html', {'profile_form': profile_form, 'user_form': user_form})

@login_required
def change_password(request):
    """Renders password editing page"""
    # Create the form
    user = request.user # type: User
    form = PasswordForm(user=user)
    # Check method
    if request.method == 'POST':
        # Create the form
        form = PasswordForm(user=user, data=request.POST)
        # Validate
        if form.is_valid():
            # Save
            new_pass = form.cleaned_data['new_password1']
            user.set_password(new_pass)
            user.save()
            user = authenticate(
                username=user.username,
                password=new_pass)
            login(request, user)
            messages.success(request, 'Your password successfully changed!')
            # Redirect to profile
            return HttpResponseRedirect(reverse('accounts:profile'))
    # Render template
    return render(request, 'accounts/change_password.html', {'form': form})

def sign_in(request):
    """Renders sign in page"""
    # Check if user is already logged in
    if request.user and str(request.user) != 'AnonymousUser':
        messages.success(
            request,
            "You're already logged in!"
        )
        # Redirect to home
        return HttpResponseRedirect(reverse('home'))
    # Create form
    form = AuthenticationForm()
    # Check method
    if request.method == 'POST':
        # Create form
        form = AuthenticationForm(data=request.POST)
        # Validate
        if form.is_valid():
            # Save
            if form.user_cache is not None:
                user = form.user_cache
                if user.is_active:
                    login(request, user)
                    # Redirect to profile
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
    # Render template
    return render(request, 'accounts/sign_in.html', {'form': form})

def sign_up(request):
    """Renders sign up page"""
    # Check if user is already logged in
    if request.user and str(request.user) != 'AnonymousUser':
        messages.success(
            request,
            "You're already logged in!"
        )
        # Redirect to home
        return HttpResponseRedirect(reverse('home'))
    # Create form
    form = UserCreationForm()
    # Check method
    if request.method == 'POST':
        # Create form
        form = UserCreationForm(data=request.POST)
        # Validate
        if form.is_valid():
            # Save
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
            # Redirect to profile
            return HttpResponseRedirect(reverse('accounts:profile'))
    # Render template
    return render(request, 'accounts/sign_up.html', {'form': form})

@login_required
def sign_out(request):
    """Logs out user"""
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return HttpResponseRedirect(reverse('home'))
