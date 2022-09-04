CREATE DATABASE lab_attendance_system_db IF NOT EXISTS DEFAULT CHARACTER SET utf8mb4;
USE lab_attendance_system_db;

CREATE TABLE week_tb IF NOT EXISTS (
    id INTEGER PRIMARY KEY,
    monday_date DATE NOT NULL
);

CREATE TABLE user_tb IF NOT EXISTS (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(16) NOT NULL,
    passwd_hash CHAR(64) NOT NULL,
    fullname VARCHAR(128) NOT NULL,
    email VARCHAR(128) NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT 0,
    is_ta BOOLEAN NOT NULL DEFAULT 0,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT 1,
    UNIQUE INDEX username_index(username)
);

CREATE TABLE lab_tb IF NOT EXISTS (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    lab_name VARCHAR(16) NOT NULL,
    room_count INTEGER NOT NULL CHECK room_count > 0,
    active BOOLEAN NOT NULL DEFAULT 1,
    UNIQUE INDEX lab_name_index(lab_name)
);

CREATE TABLE course_tb IF NOT EXISTS (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course_code VARCHAR(32) NOT NULL UNIQUE,
    title VARCHAR(128) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT 1,
    INDEX course_code_index(course_code)
);

CREATE TABLE group_tb IF NOT EXISTS (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course_id INTEGER NOT NULL FOREIGN KEY REFERENCES course_tb(id),
    group_name VARCHAR(16) NOT NULL,
    lab_id INTEGER NOT NULL FOREIGN KEY REFERENCES lab_tb(id),
    lab_room INTEGER NOT NULL CHECK lab_room > 0,
    day_of_week INTEGER NOT NULL CHECK day_of_week BETWEEN 1 AND 7,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    active BOOLEAN NOT NULL DEFAULT 1,
    UNIQUE INDEX course_group_index(course_id, group_name),
    INDEX (lab_id, day_of_week),
    CHECK start_time < end_time
);

CREATE TABLE session_info_tb IF NOT EXISTS (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    group_id INTEGER NOT NULL FOREIGN KEY REFERENCES group_tb(id),
    check_in_ddl_mins INTEGER NOT NULL,
    allow_late_check_in BOOLEAN NOT NULL DEFAULT 1,
    compulsory BOOLEAN NOT NULL DEFAULT 1,
    active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE regular_session_tb IF NOT EXISTS (
    id INTEGER NOT NULL FOREIGN KEY REFERENCES session_info_tb(id),
    week INTEGER NOT NULL FOREIGN KEY REFERENCES week_tb(week_no),
    CONSTRAINT one_session_per_week UNIQUE (id, week)
);

CREATE TABLE special_session_tb IF NOT EXISTS (
    id INTEGER NOT NULL FOREIGN KEY REFERENCES session_info_tb(id),
    lab_id INTEGER NOT NULL FOREIGN KEY REFERENCES lab_tb(id),
    lab_room INTEGER NOT NULL CHECK lab_room > 0,
    lab_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    CHECK start_time < end_time,
    INDEX (lab_id, lab_date)
);

CREATE TABLE course_coordinator_tb IF NOT EXISTS (
    course_id INTEGER NOT NULL FOREIGN KEY REFERENCES course_tb(id),
    user_id  INTEGER NOT NULL FOREIGN KEY REFERENCES user_tb(id),
    PRIMARY KEY (course_id, user_id),
    INDEX (user_id)
);

CREATE TABLE lab_executive_tb IF NOT EXISTS (
    lab_id INTEGER NOT NULL FOREIGN KEY REFERENCES lab_tb(id),
    user_id  INTEGER NOT NULL FOREIGN KEY REFERENCES user_tb(id),
    PRIMARY KEY (lab_id, user_id),
    INDEX (user_id)
);

CREATE TABLE student_tb IF NOT EXISTS (
    group_id INTEGER NOT NULL FOREIGN KEY REFERENCES group_tb(id),
    user_id  INTEGER NOT NULL FOREIGN KEY REFERENCES user_tb(id),
    seat_no INTEGER NOT NULL CHECK >= 0,
    pc_id VARCHAR(16) DEFAULT NULL,
    PRIMARY KEY (group_id, user_id),
    INDEX (user_id)
);

CREATE TABLE make_up_tb IF NOT EXISTS (
    id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_id  INTEGER NOT NULL FOREIGN KEY REFERENCES user_tb(id),
    original_session_id INTEGER NOT NULL FOREIGN KEY REFERENCES session_info_tb(id),
    make_up_session_id INTEGER NOT NULL FOREIGN KEY REFERENCES session_info_tb(id),
    UNIQUE (original_session, user_id),
    INDEX (make_up_session_id)
);

CREATE TABLE teaching_assistant_tb IF NOT EXISTS (
    group_id INTEGER NOT NULL FOREIGN KEY REFERENCES group_tb(id),
    user_id  INTEGER NOT NULL FOREIGN KEY REFERENCES user_tb(id),
    PRIMARY KEY (group_id, user_id),
    INDEX (user_id)
);

CREATE TABLE history_tb IF NOT EXISTS (
    id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    session_id INTEGER NOT NULL FOREIGN KEY REFERENCES session_tb(id),
    user_id INTEGER NOT NULL FOREIGN KEY REFERENCES user_tb(id),
    user_type ENUM("student", "ta") NOT NULL,
    checked_in_state ENUM("absent", "late", "attended") NOT NULL DEFAULT "absent",
    check_in_time DATETIME,
    last_modify_time DATETIME NOT NULL DEFAULT NOW(),
    remark VARCHAR(256)
);