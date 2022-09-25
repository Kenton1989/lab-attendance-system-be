from django.http import HttpResponse, HttpRequest, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings
from .models import Profile, Week, Lab, Course, Group, BaseSession, RegularSession, SpecialSession, MakeUpSession, CheckInRecord
import traceback
from django.db.models import Q, F
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
import json
from django.core import serializers
from django.contrib.auth.hashers import make_password
from datetime import datetime, date, time, timedelta

VISIBLE_USER_FIELDS = ['id', 'username', 'is_superuser',
                       'email', 'first_name', 'last_name', 'is_staff']


def ok_resp(data: any = None) -> JsonResponse:
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


def bad_request_400() -> JsonResponse:
    return err_resp(400, 'bad request', 400)


def unauthorized_401() -> JsonResponse:
    return err_resp(401, 'unauthorized', 401)


def not_found_404() -> JsonResponse:
    return err_resp(404, 'not found', 404)


def require_login(handler=None):
    def f(request: HttpRequest):
        if not request.user.is_authenticated:
            return unauthorized_401()
        return handler(request)
    return f


def json_post_request(handler=None):
    def f(request):
        try:
            data = json.loads(request.body)
        except:
            return bad_request_400()
        return handler(request, data)
    return f


def exception_as_500(handler=None):
    if settings.DEBUG:
        return handler

    def f(request: HttpRequest):
        try:
            handler(request)
        except Exception as e:
            traceback.print_exc()
            return err_resp(500, 'internal error', http_status=500)
    return f


@json_post_request
def login_api_view(request: HttpRequest, query: dict):
    try:
        username = query['username']
        password = query['password']
    except Exception as e:
        traceback.print_tb(e)
        return bad_request_400()

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return ok_resp()
    else:
        return unauthorized_401()


@require_login
def user_info_view(request: HttpRequest):
    username = request.user.get_username()

    user = User.objects.filter(username=username).values(
        *VISIBLE_USER_FIELDS).first()

    return ok_resp(user)


@require_login
def logout_api_view(request: HttpRequest):
    logout(request)
    return ok_resp()


@require_login
def ping(request):
    return ok_resp("pong")


def user_can_read_by(user: User) -> Q:
    if user.is_staff or user.is_superuser:
        return Q()  # can read all student
    return Q(pk=user.id)


def user_can_write_by(user: User) -> Q:
    if user.is_superuser:
        return Q()  # can modify all student
    return Q(pk=user.id)


@require_login
def get_user_view(request: HttpRequest):
    if 'id' in request.GET:
        user_id = int(request.GET['id'])
        key_query = Q(pk=user_id)
    elif 'username' in request.GET:
        username = request.GET['username']
        key_query = Q(username=username)
    else:
        return bad_request_400()

    user = User.objects.filter(key_query, user_can_read_by(
        request.user)).values(*VISIBLE_USER_FIELDS).first()
    if not user:
        return not_found_404()

    return ok_resp(user)


@require_login
def list_user_view(request: HttpRequest):
    user = request.user
    if 'q' in request.GET:
        q = request.GET['q']
        search_query = Q(username__contains=q) | Q(
            first_name__contains=q) | Q(last_name__contains=q)
    else:
        search_query = Q()

    read_perm = user_can_read_by(user)

    users = User.objects.filter(read_perm, search_query).values(
        'id', 'username', 'first_name', 'last_name')

    return ok_resp(list(users))


@require_login
@json_post_request
def add_user_view(request: HttpRequest, query: dict):
    try:
        password = query['password']
        query['password'] = make_password(password)
        user = User.objects.create(**query)
        user.save()
    except:
        traceback.print_exc()
        return bad_request_400()
    profile = Profile.objects.create(user=user, is_ta=False)
    profile.save()
    return ok_resp()


@require_login
@json_post_request
def update_user_view(request: HttpRequest, query: dict):
    try:
        uid = query['id']
    except:
        return bad_request_400()

    user = User.objects.filter(user_can_write_by(request.user), pk=uid)
    if user.count() < 1:
        return not_found_404()

    try:
        if 'password' in query:
            passwd_hash = make_password(query['password'])
            query['password'] = passwd_hash
        user.update(**query)
    except:
        traceback.print_exc()
        return bad_request_400()

    return ok_resp()


def lab_can_read_by(user: User) -> Q:
    if user.is_staff or user.is_superuser:
        return Q()  # can read all lab
    return Q(lab_executives=user)


def lab_can_write_by(user: User) -> Q:
    if user.is_superuser:
        return Q()  # can modify all lab
    return Q(lab_executives=user)


@require_login
def get_lab_view(request: HttpRequest):
    if 'id' in request.GET:
        lab_id = int(request.GET['id'])
        key_query = Q(pk=lab_id)
    elif 'lab_name' in request.GET:
        lab_name = request.GET['lab_name']
        key_query = Q(lab_name=lab_name)
    else:
        return bad_request_400()

    obj = Lab.objects.filter(
        key_query, lab_can_read_by(request.user)).values().first()

    if not obj:
        return not_found_404()

    return ok_resp(obj)


@require_login
def list_lab_view(request: HttpRequest):
    user = request.user
    if 'q' in request.GET:
        q = request.GET['q']
        search_query = Q(lab_name__contains=q)
    else:
        search_query = Q()

    read_perm = lab_can_read_by(user)

    labs = Lab.objects.filter(read_perm, search_query).values(
        'id', 'lab_name', 'room_count', 'active')

    return ok_resp(list(labs))


@require_login
@json_post_request
def add_lab_view(request: HttpRequest, query: dict):
    try:
        obj = Lab.objects.create(**query)
        obj.save()
    except:
        traceback.print_exc()
        return bad_request_400()
    return ok_resp()


@require_login
@json_post_request
def update_lab_view(request: HttpRequest, query: dict):
    try:
        id = query['id']
    except:
        return bad_request_400()

    obj = Lab.objects.filter(lab_can_write_by(request.user), pk=id)
    if obj.count() < 1:
        return not_found_404()

    try:
        obj.update(**query)
    except:
        traceback.print_exc()
        return bad_request_400()

    return ok_resp()


def course_can_read_by(user: User) -> Q:
    if user.is_staff or user.is_superuser:
        return Q()  # can read all course
    return Q(course_coordinators=user) | Q(groups__teaching_assistants=user)


def course_can_write_by(user: User) -> Q:
    if user.is_superuser:
        return Q()  # can modify all course
    return Q(course_coordinators=user)


@require_login
def get_course_view(request: HttpRequest):
    if 'id' in request.GET:
        id = int(request.GET['id'])
        key_query = Q(pk=id)
    elif 'course_code' in request.GET:
        course_code = request.GET['course_code']
        key_query = Q(course_code=course_code)
    else:
        return bad_request_400()

    obj = Course.objects.filter(
        key_query, course_can_read_by(request.user)).values().first()
    if not obj:
        return not_found_404()

    return ok_resp(obj)


@require_login
def list_course_view(request: HttpRequest):
    user = request.user
    if 'q' in request.GET:
        q = request.GET['q']
        search_query = Q(course_code__contains=q) | Q(title__contains=q)
    else:
        search_query = Q()

    read_perm = course_can_read_by(user)

    objs = Course.objects.filter(read_perm, search_query).values(
        'id', 'course_code', 'title')

    return ok_resp(list(objs))


@require_login
@json_post_request
def add_course_view(request: HttpRequest, query: dict):
    try:
        obj = Course.objects.create(**query)
        obj.save()
    except:
        traceback.print_exc()
        return bad_request_400()
    return ok_resp()


@require_login
@json_post_request
def update_course_view(request: HttpRequest, query: dict):
    try:
        id = query['id']
    except:
        return bad_request_400()

    obj = Course.objects.filter(course_can_write_by(request.user), pk=id)
    if obj.count() < 1:
        return not_found_404()

    try:
        obj.update(**query)
    except:
        traceback.print_exc()
        return bad_request_400()

    return ok_resp()


def group_can_read_by(user: User) -> Q:
    if user.is_staff or user.is_superuser:
        return Q()  # can read all group
    return Q(course__course_coordinators=user) | Q(lab__lab_executives=user) | Q(teaching_assistants=user)


def group_can_write_by(user: User) -> Q:
    if user.is_superuser:
        return Q()  # can modify all group
    return Q(course__course_coordinators=user) | Q(lab__lab_executives=user)


@require_login
def get_group_view(request: HttpRequest):
    if 'id' in request.GET:
        id = int(request.GET['id'])
        key_query = Q(pk=id)
    elif 'course_code' in request.GET and 'group_name' in request.GET:
        course_code = request.GET['course_code']
        group_name = request.GET['group_name']
        key_query = Q(course_code=course_code, group_name=group_name)
    else:
        return bad_request_400()

    obj = Group.objects.filter(
        key_query, group_can_read_by(request.user)).values().first()
    if not obj:
        return not_found_404()

    return ok_resp(obj)


@require_login
def list_group_view(request: HttpRequest):
    user = request.user
    query_condition = Q()
    if 'q' in request.GET:
        q = request.GET['q']
        query_condition &= Q(group_name__contains=q)
    if 'crouse_id' in request.GET:
        course_id = int(request.GET['course_id'])
        query_condition &= Q(course_id=course_id)

    read_perm = group_can_read_by(user)

    objs = Group.objects.filter(read_perm, query_condition).values()

    return ok_resp(list(objs))


@require_login
@json_post_request
def add_group_view(request: HttpRequest, query: dict):
    try:
        obj = Group.objects.create(**query)
        obj.save()
    except:
        traceback.print_exc()
        return bad_request_400()
    return ok_resp()


@require_login
@json_post_request
def update_group_view(request: HttpRequest, query: dict):
    try:
        id = query['id']
    except:
        return bad_request_400()

    obj = Group.objects.filter(group_can_write_by(request.user), pk=id)
    if obj.count() < 1:
        return not_found_404()

    try:
        obj.update(**query)
    except:
        traceback.print_exc()
        return bad_request_400()

    return ok_resp()


def session_can_read_by(user: User) -> Q:
    if user.is_staff or user.is_superuser:
        return Q()  # can read all course
    return Q(group__course__course_coordinators=user) | Q(group__lab__lab_executives=user) | Q(group__teaching_assistants=user)


def session_can_write_by(user: User) -> Q:
    if user.is_superuser:
        return Q()  # can modify all course
    return Q(group__course__course_coordinators=user) | Q(group__lab__lab_executives=user)


@require_login
def get_session_view(request: HttpRequest):
    if 'id' in request.GET:
        id = int(request.GET['id'])
        key_query = Q(pk=id)
    else:
        return bad_request_400()

    condition = key_query & session_can_read_by(request.user)

    obj = RegularSession.objects.filter(condition).values().first()
    if not obj:
        obj = SpecialSession.objects.filter(condition).values().first()
    if not obj:
        return not_found_404()

    return ok_resp(obj)


@require_login
def list_session_view(request: HttpRequest):
    query_condition = Q()

    if 'group_id' in request.GET:
        group_id = int(request.GET['group_id'])
        query_condition &= Q(group_id=group_id)

    if 'lab_id' in request.GET:
        lab_id = int(request.GET['lab_id'])
        query_condition &= Q(group__lab_id=lab_id)

    if not query_condition:
        return bad_request_400()

    include_sp, include_reg = True, True

    if 'special' in request.GET:
        special = int(request.GET.get['special'])
        if special:
            include_sp, include_reg = True, False
        else:
            include_sp, include_reg = False, True

    user = request.user
    read_perm = session_can_read_by(user)

    condition = read_perm & query_condition

    reg, sp = [], []
    if include_reg:
        reg = list(RegularSession.objects.filter(condition).values())
    if include_sp:
        sp = list(SpecialSession.objects.filter(condition).values())

    return ok_resp(reg+sp)


@require_login
@json_post_request
def add_regular_session_view(request: HttpRequest, query: dict):
    try:
        obj = RegularSession.objects.create(**query)
        obj.save()
    except:
        traceback.print_exc()
        return bad_request_400()
    return ok_resp()


@require_login
@json_post_request
def add_special_session_view(request: HttpRequest, query: dict):
    try:
        obj = SpecialSession.objects.create(**query)
        obj.save()
    except:
        traceback.print_exc()
        return bad_request_400()
    return ok_resp()


@require_login
@json_post_request
def update_session_view(request: HttpRequest, query: dict):
    try:
        id = query['id']
    except:
        return bad_request_400()

    condition = session_can_write_by(request.user) & Q(pk=id)
    obj = RegularSession.objects.filter(condition)
    if obj.count() < 1:
        obj = SpecialSession.objects.filter(condition)
    if obj.count() < 1:
        return not_found_404()

    try:
        obj.update(**query)
    except:
        traceback.print_exc()
        return bad_request_400()

    return ok_resp()


def record_can_read_by(user: User) -> Q:
    if user.is_superuser:
        return Q()  # can read all record
    return Q(user=user) | Q(session__group__teaching_assistants=user) | Q(session__group__course__course_coordinators=user) | Q(session__group__lab__lab_executives=user)


def record_can_write_by(user: User) -> Q:
    if user.is_superuser:
        return Q()  # can modify all record
    return Q(session__group__course__course_coordinators=user) | Q(session__group__lab__lab_executives=user)


@require_login
def get_record_view(request: HttpRequest):
    if 'id' in request.GET:
        id = int(request.GET['id'])
        key_query = Q(pk=id)
    else:
        return bad_request_400()

    obj = CheckInRecord.objects.filter(
        key_query, record_can_read_by(request.user)).values().first()
    if not obj:
        return not_found_404()

    return ok_resp(obj)


@require_login
def list_record_view(request: HttpRequest):
    user = request.user
    query_condition = Q()
    if 'session_id' in request.GET:
        session_id = int(request.GET['session_id'])
        query_condition &= Q(session_id=session_id)
    elif 'group_id' in request.GET:
        course_id = int(request.GET['group_id'])
        query_condition &= Q(session__group_id=group_id)
    elif 'crouse_id' in request.GET:
        course_id = int(request.GET['course_id'])
        query_condition &= Q(session__group__course_id=course_id)

    if 'user_id' in request.GET:
        user_id = int(request.GET['user_id'])
        query_condition &= Q(user_id=user_id)

    read_perm = record_can_read_by(user)

    objs = CheckInRecord.objects.filter(read_perm, query_condition).values()

    return ok_resp(list(objs))


@require_login
@json_post_request
def update_record_view(request: HttpRequest, query: dict):
    try:
        id = query['id']
        last_modify_time = datetime.fromisoformat(query['last_modify_time'])
        if not last_modify_time.tzinfo:
            return bad_request_400()
    except:
        return bad_request_400()

    obj = CheckInRecord.objects.filter(record_can_write_by(
        request.user), pk=id, last_modify_time__lte=last_modify_time)
    if obj.count() < 1:
        return not_found_404()

    try:
        obj.update(**query)
    except:
        traceback.print_exc()
        return bad_request_400()

    return ok_resp()


@require_login
def list_record_filters_view(request: HttpRequest):
    records = CheckInRecord.objects.filter(record_can_read_by(request.user))

    user_cond = (Q(attendance_records__user_id=F('id')) |
                 Q(attendance_records__session__group__teaching_assistants=F('id')) |
                 Q(attendance_records__session__group__course__course_coordinators=F('id')) |
                 Q(attendance_records__session__group__lab__lab_executives=F('id')))
    course_cond = (Q(groups__sessions__check_in_records__user_id=F('id')) |
                   Q(groups__sessions__check_in_records__session__group__teaching_assistants=F('id')) |
                   Q(groups__sessions__check_in_records__session__group__course__course_coordinators=F('id')) |
                   Q(groups__sessions__check_in_records__session__group__lab__lab_executives=F('id')))
    users = User.objects.filter(user_cond).values('id', 'username').distinct()
    courses = Course.objects.filter(
        course_cond).values('id', 'course_code', 'title').distinct()

    return ok_resp({
        'users': list(users),
        'courses': list(courses),
    })


@require_login
def records_of_lab_today_view(request: HttpRequest):
    if 'lab_id' in request.GET:
        lab_id = int(request.GET['lab_id'])
    elif 'lab_name' in request.GET:
        lab_name = str(request.GET['lab_name'])
        lab = Lab.objects.filter(lab_name=lab_name).first()
        if not lab:
            return not_found_404()
        lab_id = lab.id
    else:
        return bad_request_400()

    if not request.user.is_superuser:
        user = User.objects.filter(
            lab_executive_of=lab_id, id=request.user.id).first()
        if not user:
            return not_found_404()

    today = date.today()
    week_before = today - timedelta(days=7)
    week = Week.objects.filter(
        monday_date__lte=today, monday_date__gt=week_before).first()

    if week:
        re_sessions = RegularSession.objects.filter(
            group__lab_id=lab_id, active=True, week=week)
    else:
        re_sessions = RegularSession.objects.none()
    sp_sessions = SpecialSession.objects.filter(
        lab_id=lab_id, active=True, lab_date=today)

    all_sessions = list(re_sessions) + list(sp_sessions)

    for session in all_sessions:
        for student in session.group.students.all():
            if not student.is_active:
                continue
            try:
                CheckInRecord.objects.create(
                    user=student, session=session, user_type=CheckInRecord.STUDENT,
                    last_modify_time=datetime.utcnow(), check_in_state=CheckInRecord.ABSENT)
            except:
                traceback.print_exc()
        for ta in session.group.teaching_assistants.all():
            if not ta.is_active:
                continue
            try:
                CheckInRecord.objects.create(
                    user=ta, session=session, user_type=CheckInRecord.TA,
                    last_modify_time=datetime.utcnow(), check_in_state=CheckInRecord.ABSENT)
            except:
                traceback.print_exc()

    all_session_id = [s.id for s in all_sessions]
    records = list(CheckInRecord.objects.filter(
        session__in=all_session_id,
    ).distinct().values())
    groups = list(Group.objects.filter(
        sessions__in=all_session_id).distinct().values())

    groups_id = [g['id'] for g in groups]
    courses = list(Course.objects.filter(
        groups__in=groups_id).distinct().values())

    records_id = [r['id'] for r in records]
    users = list(User.objects.filter(
        attendance_records__in=records_id).distinct().values(*VISIBLE_USER_FIELDS))

    return ok_resp({
        'records': records,
        'sessions': list(re_sessions.values())+list(sp_sessions.values()),
        'groups': groups,
        'courses': courses,
        'users': users,
    })
