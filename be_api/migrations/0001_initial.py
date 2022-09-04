# Generated by Django 4.1 on 2022-09-04 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_ddl_mins', models.IntegerField()),
                ('allow_late_check_in', models.BooleanField(default=True)),
                ('compulsory', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CheckInRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.IntegerField(choices=[(0, 'student'), (1, 'TA')])),
                ('check_in_state', models.IntegerField(choices=[(0, 'absent'), (1, 'late'), (2, 'attended')])),
                ('check_in_time', models.DateTimeField(null=True)),
                ('last_modify_time', models.DateTimeField()),
                ('remark', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=32, unique=True)),
                ('title', models.CharField(max_length=128)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=16)),
                ('lab_room', models.IntegerField()),
                ('day_of_week', models.IntegerField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lab_name', models.CharField(max_length=16, unique=True)),
                ('room_count', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='MakeUpSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=16, unique=True)),
                ('passwd_hash', models.CharField(max_length=64)),
                ('fullname', models.CharField(max_length=128)),
                ('email', models.CharField(max_length=128)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_ta', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Week',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monday_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='RegularSession',
            fields=[
                ('basesession_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='be_api.basesession')),
            ],
            bases=('be_api.basesession',),
        ),
        migrations.CreateModel(
            name='SpecialSession',
            fields=[
                ('basesession_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='be_api.basesession')),
                ('lab_room', models.IntegerField()),
                ('lab_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
            bases=('be_api.basesession',),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['username'], name='be_api_user_usernam_bb6324_idx'),
        ),
        migrations.AddField(
            model_name='makeupsession',
            name='make_up_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='make_up_session_of', to='be_api.basesession'),
        ),
        migrations.AddField(
            model_name='makeupsession',
            name='original_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='original_sessions_of', to='be_api.basesession'),
        ),
        migrations.AddField(
            model_name='makeupsession',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='make_up_sessions', to='be_api.user'),
        ),
        migrations.AddField(
            model_name='lab',
            name='lab_executives',
            field=models.ManyToManyField(related_name='lab_executive_of', to='be_api.user'),
        ),
        migrations.AddField(
            model_name='group',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='groups', to='be_api.course'),
        ),
        migrations.AddField(
            model_name='group',
            name='lab',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='groups', to='be_api.lab'),
        ),
        migrations.AddField(
            model_name='group',
            name='students',
            field=models.ManyToManyField(related_name='student_of', to='be_api.user'),
        ),
        migrations.AddField(
            model_name='group',
            name='teaching_assistants',
            field=models.ManyToManyField(related_name='teaching_assistant_of', to='be_api.user'),
        ),
        migrations.AddField(
            model_name='course',
            name='course_coordinators',
            field=models.ManyToManyField(related_name='course_coordinator_of', to='be_api.user'),
        ),
        migrations.AddField(
            model_name='checkinrecord',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='check_in_records', to='be_api.basesession'),
        ),
        migrations.AddField(
            model_name='checkinrecord',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attendance_records', to='be_api.basesession'),
        ),
        migrations.AddField(
            model_name='basesession',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sessions', to='be_api.group'),
        ),
        migrations.AddField(
            model_name='basesession',
            name='make_up_students',
            field=models.ManyToManyField(related_name='sessions_to_make_up', through='be_api.MakeUpSession', to='be_api.user'),
        ),
        migrations.AddField(
            model_name='specialsession',
            name='lab',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sp_sessions', to='be_api.lab'),
        ),
        migrations.AddField(
            model_name='regularsession',
            name='week',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sessions', to='be_api.week'),
        ),
        migrations.AddConstraint(
            model_name='lab',
            constraint=models.CheckConstraint(check=models.Q(('room_count__gt', 0)), name='positive_lab_room_count', violation_error_message='room number should be greater than 0'),
        ),
        migrations.AddIndex(
            model_name='group',
            index=models.Index(fields=['lab', 'day_of_week'], name='be_api_grou_lab_id_18a3a1_idx'),
        ),
        migrations.AddConstraint(
            model_name='group',
            constraint=models.UniqueConstraint(fields=('course', 'group_name'), name='unique_group_of_course', violation_error_message='a course cannot have two group with the same name'),
        ),
        migrations.AddConstraint(
            model_name='group',
            constraint=models.CheckConstraint(check=models.Q(('start_time__lt', models.F('end_time'))), name='group_start_before_end', violation_error_message='start time must be earlier than end time'),
        ),
        migrations.AddConstraint(
            model_name='group',
            constraint=models.CheckConstraint(check=models.Q(('lab_room__gt', 0)), name='group_valid_room_number', violation_error_message='invalid lab room number'),
        ),
        migrations.AddConstraint(
            model_name='group',
            constraint=models.CheckConstraint(check=models.Q(('lab_room__gte', 1), ('lab_room__lte', 7)), name='group_valid_day_of_week', violation_error_message='day of week must be 1~7'),
        ),
        migrations.AddConstraint(
            model_name='basesession',
            constraint=models.CheckConstraint(check=models.Q(('check_in_ddl_mins__gt', 0)), name='positive_deadline_minutes', violation_error_message='check in deadline should be greater than 0 minutes'),
        ),
        migrations.AddIndex(
            model_name='specialsession',
            index=models.Index(fields=['lab', 'lab_date'], name='be_api_spec_lab_id_b74a31_idx'),
        ),
        migrations.AddConstraint(
            model_name='specialsession',
            constraint=models.CheckConstraint(check=models.Q(('start_time__lt', models.F('end_time'))), name='sp_session_start_before_end', violation_error_message='start time must be earlier than end time'),
        ),
        migrations.AddConstraint(
            model_name='specialsession',
            constraint=models.CheckConstraint(check=models.Q(('lab_room__gt', 0)), name='sp_session_valid_room_number', violation_error_message='invalid lab room number'),
        ),
    ]