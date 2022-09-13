from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def ping(request):
    return HttpResponse("pong")


def login_api_view(request: HttpRequest):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if 'next' in request.POST:
            return redirect(request.POST['next'])
        return HttpResponse('')
    else:
        return HttpResponse('', status=401)


@login_required
def logout_api_view(request):
    logout(request)
    return HttpResponse()
