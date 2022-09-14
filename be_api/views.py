from django.http import HttpResponse, HttpRequest, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Profile


def ok_resp(data: dict = None) -> JsonResponse:
    if (data == None):
        return JsonResponse({'ok': True})

    return JsonResponse({
        'ok': True,
        'data': data,
    })


def err_resp(err_code: int, err_msg: str, http_status: int = 200) -> JsonResponse:
    return JsonResponse({
        'ok': False,
        'error': {
            'code': err_code,
            'msg': err_msg,
        },
    }, status=http_status)


def http_401_unauthorized():
    return err_resp(401, 'unauthorized', http_status=401)


def require_login(handler=None):
    def f(request: HttpRequest):
        if not request.user.is_authenticated:
            return http_401_unauthorized()
        return handler(request)
    return f


def login_api_view(request: HttpRequest):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        return HttpResponse('')
    else:
        return http_401_unauthorized()


@require_login
def user_info_view(request: HttpRequest):
    username = request.user.get_username()

    user = User.objects.get(username=username)
    profile = user.profile

    return ok_resp({
        'username': username,
        'is_staff': profile.is_staff,
    })


@require_login
def logout_api_view(request: HttpRequest):
    logout(request)
    return ok_resp()


@require_login
def ping(request):
    return HttpResponse("pong")
