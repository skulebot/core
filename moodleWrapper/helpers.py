from datetime import datetime
from typing import Any, Dict, List
from MoodleAPIClient import MoodleAPIClient
from classes import CourseModule, UpdateItem


def check_course_updates(
    course_ids: List[int], since: datetime
) -> Dict[int, List[Dict[str, Any]]]:
    updates = {}
    for course_id in course_ids:
        course_updates = _check_single_course(course_id, since=since)
        if course_updates:
            updates[course_id] = course_updates
    return updates


def _check_single_course(course_id: int, since: datetime) -> List[Dict[str, Any]]:
    response = MoodleAPIClient().get_course_updates_since(
        courseid=course_id, since=since
    )
    if response.status_code != 200 or not response.data.instances:
        return []

    course_updates = []
    for instance in response.data.instances:
        for update in instance.updates:
            update_info = _get_update_info(course_id, update)
            if update_info:
                course_updates.append(update_info)

    return course_updates


def _get_update_info(course_id: int, update: UpdateItem) -> Dict[str, Any]:
    response = MoodleAPIClient().get_course_contents(courseid=course_id)
    if response.status_code != 200:
        return {}
    for section in response.data:
        for module in section.modules:
            if (
                update.itemids and module.id == update.itemids[0]
            ):  # Assuming the first itemid is the module id
                print(module)
                return {
                    "type": _determine_update_type(module),
                    "name": module.name,
                    "description": module.description,
                    "url": module.url,
                    "contents": (
                        [
                            {
                                "filename": content.filename,
                                "fileurl": content.fileurl,
                                "filesize": content.filesize,
                            }
                            for content in module.contents
                            if content.type == "file"
                        ]
                        if module.contents
                        else []
                    ),
                }
    return {}


def _determine_update_type(module: CourseModule) -> str:
    module_types = {
        "resource": "lecture",
        "assign": "assignment",
        "quiz": "quiz",
        "forum": "forum",
        "workshop": "lab",
        "book": "reading",
        "page": "page",
    }
    return module_types.get(module.modname, "other")


def parsed_categories():
    client = MoodleAPIClient()
    res = client.get_categories()
    categories = res.data
    mapper = {
        "1": 1,
        "one": 1,
        "first": 1,
        "2": 2,
        "two": 2,
        "second": 2,
        "3": 3,
        "three": 3,
        "third": 3,
        "4": 4,
        "four": 4,
        "fourth": 4,
        "5": 5,
        "five": 5,
        "fifth": 5,
    }

    categories_sorted = sorted(categories, key=lambda c: c.depth)
    parsed: dict = {}
    id_node: dict = {}
    for cat in categories_sorted:
        path = cat.path[1:].split("/")
        if len(path) == 1:
            parsed[cat.name] = {}
            parsed[cat.name]["name"] = cat.name
            parsed[cat.name]["id"] = cat.id
            parsed[cat.name]["semesters"] = []
        elif len(path) == 2:
            pass
        elif len(path) == 3:
            parent = id_node[cat.parent]
            grand = id_node[parent.parent]
            level_number: int = None
            semester_number: int = None
            for key, number in mapper.items():
                if key in parent.name.lower():
                    level_number: int = number
                if key in cat.name.lower():
                    semester_number: int = number
            number = (level_number * 2) - (semester_number % 2)
            parsed[grand.name]["semesters"].append({"number": number, "id": cat.id})

        id_node[cat.id] = cat

    return parsed


check_course_updates([3, 2], datetime(2024, 9, 8))
from datetime import datetime
from typing import Any, Dict, List
from MoodleAPIClient import MoodleAPIClient
from classes import CourseModule, UpdateItem


def check_course_updates(
    course_ids: List[int], since: datetime
) -> Dict[int, List[Dict[str, Any]]]:
    updates = {}
    for course_id in course_ids:
        course_updates = _check_single_course(course_id, since=since)
        if course_updates:
            updates[course_id] = course_updates
    return updates


def _check_single_course(course_id: int, since: datetime) -> List[Dict[str, Any]]:
    response = MoodleAPIClient().get_course_updates_since(
        courseid=course_id, since=since
    )
    if response.status_code != 200 or not response.data.instances:
        return []

    course_updates = []
    for instance in response.data.instances:
        for update in instance.updates:
            update_info = _get_update_info(course_id, update)
            if update_info:
                course_updates.append(update_info)

    return course_updates


def _get_update_info(course_id: int, update: UpdateItem) -> Dict[str, Any]:
    response = MoodleAPIClient().get_course_contents(courseid=course_id)
    if response.status_code != 200:
        return {}
    for section in response.data:
        for module in section.modules:
            if (
                update.itemids and module.id == update.itemids[0]
            ):  # Assuming the first itemid is the module id
                print(module)
                return {
                    "type": _determine_update_type(module),
                    "name": module.name,
                    "description": module.description,
                    "url": module.url,
                    "contents": (
                        [
                            {
                                "filename": content.filename,
                                "fileurl": content.fileurl,
                                "filesize": content.filesize,
                            }
                            for content in module.contents
                            if content.type == "file"
                        ]
                        if module.contents
                        else []
                    ),
                }
    return {}


def _determine_update_type(module: CourseModule) -> str:
    module_types = {
        "resource": "lecture",
        "assign": "assignment",
        "quiz": "quiz",
        "forum": "forum",
        "workshop": "lab",
        "book": "reading",
        "page": "page",
    }
    return module_types.get(module.modname, "other")


def parsed_categories():
    client = MoodleAPIClient()
    res = client.get_categories()
    categories = res.data
    mapper = {
        "1": 1,
        "one": 1,
        "first": 1,
        "2": 2,
        "two": 2,
        "second": 2,
        "3": 3,
        "three": 3,
        "third": 3,
        "4": 4,
        "four": 4,
        "fourth": 4,
        "5": 5,
        "five": 5,
        "fifth": 5,
    }

    categories_sorted = sorted(categories, key=lambda c: c.depth)
    parsed: dict = {}
    id_node: dict = {}
    for cat in categories_sorted:
        path = cat.path[1:].split("/")
        if len(path) == 1:
            parsed[cat.name] = {}
            parsed[cat.name]["name"] = cat.name
            parsed[cat.name]["id"] = cat.id
            parsed[cat.name]["semesters"] = []
        elif len(path) == 2:
            pass
        elif len(path) == 3:
            parent = id_node[cat.parent]
            grand = id_node[parent.parent]
            level_number: int = None
            semester_number: int = None
            for key, number in mapper.items():
                if key in parent.name.lower():
                    level_number: int = number
                if key in cat.name.lower():
                    semester_number: int = number
            number = (level_number * 2) - (semester_number % 2)
            parsed[grand.name]["semesters"].append({"number": number, "id": cat.id})

        id_node[cat.id] = cat

    return parsed


check_course_updates([3, 2], datetime(2024, 9, 8))
