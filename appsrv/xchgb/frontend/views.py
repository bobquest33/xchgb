from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib import messages

from frontend.forms import *
from xchgb import transaction

"""Should return True if the user has been registered with the transaction server."""
def finished_registration(user):
    return bool(user.email)

"""Replace Django's login_required with this one, which checks finished_registration()."""
def login_required(f):
    def new_f(request, *args, **kwargs):
        if not finished_registration(request.user):
            return redirect(finish_registration)
        else:
            return f(request, *args, **kwargs)
    return django_login_required(new_f)

def welcome(request):
    pass

def login(request):
    if not request.user.is_authenticated:
        return render_to_response('frontend/login.html', {}, RequestContext(request))
    else:
        return redirect(dashboard)

@django_login_required
def finish_registration(request):
    if finished_registration(request.user):
        return redirect(dashboard)

    if request.method == 'POST':
        form = FinishRegistrationForm(request.POST)
        if form.is_valid():
            try:
                transaction.new_account(request.user.username, form.cleaned_data['password'], form.cleaned_data['email'])
                request.user.email = form.cleaned_data['email']
                request.user.save()
                return redirect(dashboard)
            except transaction.ResponseError as error:
                messages.error(request, error)
    else:
        form = FinishRegistrationForm()

    return render_to_response('frontend/finish_reg.html', {'form': form}, RequestContext(request))

@login_required
def dashboard(request):
    return render_to_response('frontend/dashboard.html', {}, RequestContext(request))

def market_data(request):
    pass

@login_required
def buy_order(request):
    pass

@login_required
def sell_order(request):
    pass

@login_required
def deposit_funds(request):
    pass

@login_required
def withdraw_funds(request):
    pass

@login_required
def account_history(request):
    pass

def help(request):
    pass

def network_status(request):
    pass

@login_required
def api_help(request):
    pass

def about_bitcoin(request):
    pass

def legal(request):
    pass

def contact(request):
    pass