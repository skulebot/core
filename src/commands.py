from sqlalchemy import select
from sqlalchemy.orm import Session
from telegram import CallbackQuery, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler

from moodleWrapper.helpers import parsed_categories
from moodleWrapper.MoodleAPIClient import client
from src import constants, messages, queries
from src.customcontext import CustomContext
from src.messages import bold
from src.models import (
    Course,
    Program,
    ProgramSemester,
    ProgramSemesterCourse,
    RoleName,
    Semester,
    Status,
)
from src.utils import build_menu, roles, session

# ------------------------------- Callbacks ---------------------------


@roles(RoleName.USER)
@session
async def list_enrollments(
    update: Update, context: CustomContext, session: Session
) -> None:
    """Runs with Message.text `/enrollments`. This is an entry point to
    `constans.ENROLLMENT_` conversation"""

    URLPREFIX = constants.ENROLLMENT_

    query: None | CallbackQuery = None
    if update.callback_query:
        query = update.callback_query
        await query.answer()

    enrollments = queries.user_enrollments(session, user_id=context.user_data["id"])
    most_recent_year = queries.academic_year(session, most_recent=True)
    most_recent_enrollment_year = enrollments[0].academic_year if enrollments else None

    menu = []
    if most_recent_year and most_recent_enrollment_year != most_recent_year:
        menu.append(
            context.buttons.new_enrollment(
                most_recent_year,
                f"{URLPREFIX}/{constants.ENROLLMENTS}"
                f"/{constants.ADD}?year_id={most_recent_year.id}",
            ),
        )

    menu += context.buttons.enrollments_list(
        enrollments, f"{URLPREFIX}/{constants.ENROLLMENTS}"
    )
    keyboard = build_menu(menu, 1)
    reply_markup = InlineKeyboardMarkup(keyboard)
    _ = context.gettext

    message = _("Your enrollments")

    if query:
        await query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_markdown_v2(message, reply_markup=reply_markup)


@roles(RoleName.STUDENT)
@session
async def user_course_list(update: Update, context: CustomContext, session: Session):
    """Runs with Message.text `/courses`. This is an entry point to
    `constans.COURSES_` conversation"""

    URLPREFIX = constants.COURSES_

    query: None | CallbackQuery = None

    if update.callback_query:
        query = update.callback_query
        await query.answer()

    enrollment = queries.user_most_recent_enrollment(
        session, user_id=context.user_data["id"]
    )

    user_courses = queries.user_courses(
        session,
        program_id=enrollment.program.id,
        semester_id=enrollment.semester.id,
        user_id=context.user_data["id"],
        sort_attr=(
            Course.ar_name if context.language_code == constants.AR else Course.en_name
        ),
    )

    url = f"{URLPREFIX}/{constants.ENROLLMENTS}/{enrollment.id}/{constants.COURSES}"
    menu = context.buttons.courses_list(
        user_courses,
        url=url,
    )
    has_optional_courses = queries.has_optional_courses(
        session,
        program_id=enrollment.program.id,
        semester_id=enrollment.semester.id,
    )
    menu = (
        [*menu, context.buttons.optional_courses(f"{url}/{constants.OPTIONAL}")]
        if has_optional_courses
        else menu
    )
    keyboard = build_menu(menu, 1)
    reply_markup = InlineKeyboardMarkup(keyboard)
    _ = context.gettext
    message = _("Courses") + "\n\n"
    if not queries.all_have_editors(
        session,
        course_ids=[u.id for u in user_courses],
        academic_year=enrollment.academic_year,
    ):
        message += _("No editor warning {}").format(constants.COMMANDS.editor1.command)
    if query:
        await query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_html(message, reply_markup=reply_markup)


@roles([RoleName.STUDENT, RoleName.ROOT])
async def settings(update: Update, context: CustomContext):
    """Runs with Message.text `/settings`. This is an entry point to
    `constans.SETTINGS_` conversation"""

    query: None | CallbackQuery = None

    if update.callback_query:
        query = update.callback_query
        await query.answer()

    URLPREFIX = constants.SETTINGS_

    menu = [
        context.buttons.notifications(f"{URLPREFIX}/{constants.NOTIFICATIONS}"),
        context.buttons.language(f"{URLPREFIX}/{constants.LANGUAGE}"),
    ]
    keyboard = build_menu(menu, 2)

    _ = context.gettext
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = _("t-symbol") + " ⚙️ " + bold(_("Bot Settings"))
    if query:
        await query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_html(message, reply_markup=reply_markup)


@roles(RoleName.ROOT)
@session
async def request_list(update: Update, context: CustomContext, session: Session):
    """Runs with Message.text `/pending`. This is an entry point to
    `constans.REQUEST_MANAGEMENT_` conversation"""

    query: None | CallbackQuery = None

    if update.callback_query:
        query = update.callback_query
        await query.answer()

    URLPREFIX = constants.REQUEST_MANAGEMENT_

    requests = queries.access_requests(session, status=Status.PENDING)
    menu = await context.buttons.access_requests_list_chat_name(
        requests, url=f"{URLPREFIX}/{constants.ACCESSREQUSTS}", context=context
    )

    keyboard = build_menu(
        menu,
        1,
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    _ = context.gettext
    message = _("Pending access requests")

    if query:
        await query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)


@roles(RoleName.USER)
@session
async def help(update: Update, context: CustomContext, session: Session) -> None:
    """Runs with Message.text `/help`."""

    user = queries.user(session, user_id=context.user_data["id"])
    user_roles = {r.name for r in user.roles}
    message = messages.help(user_roles, language_code=context.language_code)

    await update.message.reply_html(message)


@roles(RoleName.USER)
@session
async def initialize_categories(
    update: Update, context: CustomContext, session: Session
) -> None:
    session.query(ProgramSemesterCourse).delete()
    session.query(ProgramSemester).delete()
    session.query(Program).delete()
    session.query(Course).delete()
    session.flush()
    categories: dict[str, list[dict]] = parsed_categories()
    # TODO: Check if we've already done the initialization before
    for category in categories.values():
        semesters = category["semesters"]
        name = category["name"]
        moodle_id = category["id"]
        program = Program(name, name, 10, True, moodle_id)
        session.add(program)
        session.flush()
        for semester in semesters:
            sem = session.scalar(
                select(Semester).where(Semester.number == semester["number"])
            )
            program_semester = ProgramSemester(
                program=program,
                semester=sem,
                moodle_id=semester["id"],
                available=True,
            )
            session.add(program_semester)
            session.flush()
            courses = client.get_courses_by_field(
                "category", program_semester.moodle_id
            ).data["courses"]
            for c in courses:
                course = Course(en_name=c.fullname, ar_name=c.fullname)
                session.add(course)
                session.flush()
                psm = ProgramSemesterCourse(
                    program_id=program_semester.program.id,
                    semester_id=program_semester.semester_id,
                    course_id=course.id,
                )
                session.add(psm)
                session.flush()

    session.flush()
    await update.message.reply_text("Initialized with moodle successfully.")


# ------------------------------- CommandHandlers ---------------------------

cmd = constants.COMMANDS
handlers = [
    CommandHandler(cmd.enrollments1.command, list_enrollments),
    CommandHandler(cmd.courses.command, user_course_list),
    CommandHandler(cmd.settings.command, settings),
    CommandHandler(cmd.pending.command, request_list),
    CommandHandler(cmd.initialize.command, initialize_categories),
    CommandHandler(["help", "start"], help),
]
