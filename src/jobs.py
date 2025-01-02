import contextlib
import datetime
import re
from typing import Union
from zoneinfo import ZoneInfo

from babel.dates import format_timedelta
from sqlalchemy import and_, select
from sqlalchemy.orm import Session as SessionType
from telegram import InlineKeyboardMarkup, InputFile
from telegram.error import Forbidden

from moodleWrapper.classes import CourseModule, CourseSection
from moodleWrapper.MoodleAPIClient import client
from src import constants, queries
from src.buttons import ar_buttons, en_buttons
from src.customcontext import CustomContext
from src.database import Session
from src.models import Assignment
from src.models.course import Course
from src.models.enrollment import Enrollment
from src.models.file import File
from src.models.material import (
    HasNumber,
    Lecture,
    Material,
    MaterialType,
    Reference,
    RefFilesMixin,
    SingleFile,
    get_material_class,
)
from src.models.program_semester import ProgramSemester
from src.models.program_semester_course import ProgramSemesterCourse
from src.models.user import User
from src.utils import user_locale


def remove_job_if_exists(name: str, context: CustomContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def deadline_reminder(context: CustomContext):
    job = context.job
    await context.bot.send_message(
        job.chat_id,
        text=context.gettext("Started assignment deadline reminders"),
        disable_notification=True,
    )
    current_time = datetime.datetime.now(datetime.UTC)
    with Session.begin() as session:
        assignments: list[Assignment] = session.scalars(
            select(Assignment).where(
                Assignment.published,
                Assignment.deadline is not None,
                Assignment.deadline > current_time,
                and_(
                    and_(
                        Assignment.deadline
                        >= current_time + datetime.timedelta(hours=36),
                        Assignment.deadline
                        < current_time + datetime.timedelta(hours=48),
                    ),
                ),
            )
        ).all()
        when = 2
        for i, assignment in enumerate(assignments):
            academic_year_id = assignment.academic_year_id
            users: list[User] = session.scalars(
                select(User)
                .select_from(Assignment)
                .join(Course)
                .join(ProgramSemesterCourse)
                .join(
                    ProgramSemester,
                    and_(
                        ProgramSemester.program_id == ProgramSemesterCourse.program_id,
                        ProgramSemester.semester_id
                        == ProgramSemesterCourse.semester_id,
                    ),
                )
                .join(Enrollment, Enrollment.program_semester_id == ProgramSemester.id)
                .join(User, Enrollment.user_id == User.id)
                .where(
                    Assignment.id == assignment.id,
                    Enrollment.academic_year_id == academic_year_id,
                )
                .group_by(User)
            ).all()
            zone = ZoneInfo("Africa/Khartoum")
            delta = assignment.deadline.astimezone(zone) - datetime.datetime.now(zone)
            session.expunge(assignment)
            for ii, user in enumerate(users):
                JOBNAME = f"REMIND_{user.telegram_id}_{assignment.id}"
                session.expunge(user)
                is_last = i == len(assignments) - 1 and ii == len(users) - 1
                remove_job_if_exists(JOBNAME, context)
                context.job_queue.run_once(
                    send_reminder,
                    when=when,
                    name=JOBNAME,
                    data={
                        "user": user,
                        "assignment": assignment,
                        "delta": delta,
                        "is_last": is_last,
                    },
                    chat_id=job.chat_id,
                    user_id=job.user_id,
                )
                when += 2.5
        if len(assignments) == 0:
            await context.bot.send_message(
                job.chat_id,
                text=context.gettext("Done! No reminders to send"),
                disable_notification=True,
            )


async def send_reminder(context: CustomContext) -> None:
    """Send the notification message."""
    job = context.job

    user: User = job.data["user"]
    assignment: Assignment = job.data["assignment"]
    delta: datetime.timedelta = job.data["delta"]
    is_last: bool = job.data["is_last"]

    # Get language for user to be notified
    translation = user_locale(user.language_code)
    gettext = translation.gettext

    seconds = delta.total_seconds()
    days = seconds // (24 * 60 * 60)
    hours = (seconds // (60 * 60)) % 24
    parts = [
        format_timedelta(
            datetime.timedelta(days=days),
            granularity="days",
            format="long",
            threshold=1,
            locale=user.language_code,
        ),
        format_timedelta(
            datetime.timedelta(hours=hours),
            granularity="hours",
            format="long",
            threshold=1,
            locale=user.language_code,
        ),
    ]

    buttons = ar_buttons if user.language_code == constants.AR else en_buttons

    with Session.begin() as session:
        session.add_all([assignment, user])
        course_name = assignment.course.get_name(user.language_code)
        assignment_title = gettext(assignment.type) + f" {assignment.number}"
        remaining = gettext("time remaining {} {}").format(*parts)

        with contextlib.suppress(Forbidden):
            message = (
                "⏰ "
                + gettext("Reminder")
                + "\n\n"
                + gettext("{} of {} is due in {}").format(
                    assignment_title, course_name, remaining
                )
            )

            keyboard = [
                [
                    buttons.show_more(
                        f"{constants.REMINDER_}/{assignment.type}/{assignment.id}",
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                user.chat_id, text=message, reply_markup=reply_markup
            )

    _ = context.gettext
    if is_last:
        await context.bot.send_message(
            job.chat_id, text=_("Done sending reminders"), disable_notification=True
        )


async def get_class_name(name: str):
    for type_ in MaterialType:
        if type_ in name.lower():
            return type_
    return None


async def handle_module(
    session: SessionType,
    module: CourseModule,
    material: Union[Material, list[Material]],
    context: CustomContext,
):
    job = context.job
    exists = session.scalar(select(File).where(File.moodle_id == module.id))
    if exists:
        return False
    for content in module.contents:
        file_url = content.fileurl + f"&token={client.token}"
        data = client.session.get(file_url).content
        input_file = InputFile(data, content.filename)
        mimetype = re.sub("/.*", "", input_file.mimetype)

        type_ = None
        message = None
        file_id = None
        timeout = 60 * 10
        if mimetype == "video":
            type_ = "video"
            message = await context.bot.send_video(
                job.chat_id, input_file, write_timeout=timeout, read_timeout=timeout
            )
            file_id, name = message.video.file_id, message.video.file_name
        elif mimetype == "image":
            type_ = "photo"
            message = await context.bot.send_photo(
                job.chat_id, input_file, write_timeout=timeout, read_timeout=timeout
            )
            file_id, name = message.photo[0].file_id, message.photo[0].file_id
        else:
            type_ = "document"
            message = await context.bot.send_document(
                job.chat_id, input_file, write_timeout=timeout, read_timeout=timeout
            )
            file_id, name = message.document.file_id, message.document.file_name
        if message and file_id and name and type_:
            f = File(
                name=name,
                telegram_id=file_id,
                type=type_,
                moodle_id=module.id,
                uploader=session.get(User, context.user_data["id"]),
            )
            if isinstance(material, RefFilesMixin):
                material.files.append(f)
            if isinstance(material, SingleFile):
                material.file = f
            await message.delete()
    return True


async def handle_numbered(
    session: SessionType,
    section: CourseSection,
    material_c: Lecture,
    course_id: int,
    context: CustomContext,
):
    year = queries.academic_year(session, most_recent=True)
    name = section.name
    reg = re.compile(r"\d+")
    m = reg.search(name)
    if m is None:
        return
    number = m.group()

    material = material_c(
        course_id=course_id,
        academic_year_id=year.id,
        number=number,
        published=True,
        moodle_id=section.id,
    )

    success = False
    for module in section.modules:
        await handle_module(session, module, material, context)
    if success:
        session.add(material)


async def handle_single_file(
    session: SessionType,
    section: CourseSection,
    material_c: Reference,
    course_id: int,
    context: CustomContext,
):
    year = queries.academic_year(session, most_recent=True)
    for module in section.modules:
        material = material_c(
            course_id=course_id,
            academic_year_id=year.id,
            published=True,
            moodle_id=section.id,
        )
        success = await handle_module(session, module, material, context)

        if success:
            session.add(material)


async def moodel_sync(context: CustomContext):
    with Session.begin() as session:
        courses = session.scalars(select(Course)).all()
        for course in courses:
            res = client.get_course_contents(course.moodle_id)
            sections: CourseSection = res.data
            for section in sections:
                name: str = section.name
                if name == "General":
                    continue
                type_ = await get_class_name(name)
                if type_ is None:
                    continue
                exists = session.scalar(
                    select(Material).filter(Material.moodle_id == section.id)
                )
                if exists:
                    continue
                material_c = get_material_class(type_)
                if issubclass(material_c, HasNumber) and material_c != Assignment:
                    await handle_numbered(
                        session, section, material_c, course.id, context
                    )
                    continue
                if issubclass(material_c, SingleFile):
                    await handle_single_file(
                        session, section, material_c, course.id, context
                    )
                    continue
