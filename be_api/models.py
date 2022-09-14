from django.db import models
from django.db.models import F, Q
from django.contrib.auth.models import User


class Week(models.Model):
    monday_date = models.DateField()

    def __str__(self):
        return 'week '+str(self.id)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_ta = models.BooleanField(default=False)


class Lab(models.Model):
    lab_name = models.CharField(max_length=16, unique=True)
    room_count = models.IntegerField()
    lab_executives = models.ManyToManyField(
        User, related_name='lab_executive_of')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.lab_name

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(room_count__gt=0),
                                   name='positive_lab_room_count',
                                   violation_error_message='room number should be greater than 0'),
        ]


class Course(models.Model):
    course_code = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=128)
    course_coordinators = models.ManyToManyField(
        User, related_name='course_coordinator_of')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.course_code


class Group(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='groups')
    group_name = models.CharField(max_length=16)
    lab = models.ForeignKey(
        Lab, on_delete=models.PROTECT, related_name='groups')
    lab_room = models.IntegerField()
    day_of_week = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    students = models.ManyToManyField(User, related_name='student_of')
    teaching_assistants = models.ManyToManyField(
        User, related_name='teaching_assistant_of')

    def __str__(self):
        return f'{self.course.course_code} {self.group_name}'

    active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['lab', 'day_of_week']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['course', 'group_name'],
                                    name='unique_group_of_course',
                                    violation_error_message='a course cannot have two group with the same name'),
            models.CheckConstraint(check=Q(start_time__lt=F('end_time')),
                                   name='group_start_before_end',
                                   violation_error_message='start time must be earlier than end time'),
            models.CheckConstraint(check=Q(lab_room__gt=0),
                                   name='group_valid_room_number',
                                   violation_error_message='invalid lab room number'),
            models.CheckConstraint(check=Q(lab_room__gte=1, lab_room__lte=7),
                                   name='group_valid_day_of_week',
                                   violation_error_message='day of week must be 1~7'),
        ]


class BaseSession(models.Model):
    group = models.ForeignKey(
        Group, on_delete=models.PROTECT, related_name='sessions')
    check_in_ddl_mins = models.IntegerField()
    allow_late_check_in = models.BooleanField(default=True)
    compulsory = models.BooleanField(default=True)
    make_up_students = models.ManyToManyField(
        User,
        related_name='sessions_to_make_up',
        through='MakeUpSession',
        through_fields=('original_session', 'student')
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.group.course.course_code} {self.group.group_name} {self.id}'

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(check_in_ddl_mins__gt=0),
                                   name='positive_deadline_minutes',
                                   violation_error_message='check in deadline should be greater than 0 minutes'),
        ]


class RegularSession(BaseSession):
    week = models.ForeignKey(
        Week, on_delete=models.PROTECT, related_name='sessions')

    def __str__(self):
        return f'{self.group.course.course_code} {self.group.group_name} week {self.week.id}'


class SpecialSession(BaseSession):
    lab = models.ForeignKey(Lab, on_delete=models.PROTECT,
                            related_name='sp_sessions')
    lab_room = models.IntegerField()
    lab_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.group.course.course_code} {self.group.group_name} sp {self.lab_date}'

    class Meta:
        indexes = [
            models.Index(fields=['lab', 'lab_date']),
        ]
        constraints = [
            models.CheckConstraint(check=Q(start_time__lt=F('end_time')),
                                   name='sp_session_start_before_end',
                                   violation_error_message='start time must be earlier than end time'),
            models.CheckConstraint(check=Q(lab_room__gt=0),
                                   name='sp_session_valid_room_number',
                                   violation_error_message='invalid lab room number'),
        ]


class MakeUpSession(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='make_up_sessions')
    original_session = models.ForeignKey(
        BaseSession, on_delete=models.PROTECT, related_name='original_sessions_of')
    make_up_session = models.ForeignKey(
        BaseSession, on_delete=models.PROTECT, related_name='make_up_session_of')


class CheckInRecord(models.Model):
    STUDENT = 0
    TA = 1
    USER_TYPE_CHOICES = [(STUDENT, 'student'), (TA, 'TA')]

    ABSENT = 0
    LATE = 1
    ATTENDED = 2
    CHECK_IN_STATE_CHOICES = [
        (ABSENT, 'absent'), (LATE, 'late'), (ATTENDED, 'attended')
    ]

    session = models.ForeignKey(
        BaseSession, on_delete=models.PROTECT, related_name='check_in_records')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='attendance_records')
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES)
    check_in_state = models.IntegerField(choices=CHECK_IN_STATE_CHOICES)
    check_in_time = models.DateTimeField(null=True)
    last_modify_time = models.DateTimeField()
    remark = models.CharField(max_length=256, blank=True)
