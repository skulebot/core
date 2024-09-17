import os
import urllib.parse
from dataclasses import dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Optional, Union

import requests
from dotenv import load_dotenv

from classes import (
    Assignment,
    AssignmentConfig,
    AssignmentFile,
    AssignmentsResponse,
    Category,
    Contact,
    Course,
    CourseAssignments,
    CourseFormatOption,
    CourseModule,
    CourseSection,
    CourseUpdatesResponse,
    CustomField,
    File,
    Filter,
    Instance,
    ModuleCompletionData,
    ModuleContent,
    ModuleDate,
    MoodleCourse,
    UpdateItem,
)


@dataclass
class MoodleAPIResponse:
    status_code: int
    data: Union[list[Assignment], list[CourseSection], list[Category], any]


class MoodleAPIClient:
    def __init__(self, server_url: Optional[str] = None, token: Optional[str] = None):
        # Load environment variables if .env file exists

        if Path.exists(Path(".", ".env")):
            load_dotenv()

        self.server_url = server_url or os.getenv("MOODLE_SERVER_URL")
        self.token = token or os.getenv("MOODLE_TOKEN")

        if not self.server_url or not self.token:
            raise ValueError(
                "Moodle server URL and token must be provided either in .env file or as"
                " constructor arguments"
            )

        self.session = requests.Session()
        self.session.params = {"wstoken": self.token, "moodlewsrestformat": "json"}

    def _format_params(self, params: dict[str, Any]) -> str:
        """
        Format parameters according to Moodle's API expectations.
        """

        def encode_param(key, value, prefix=""):
            if isinstance(value, list):
                return "&".join(
                    encode_param(f"{key}[{i}]", v, prefix) for i, v in enumerate(value)
                )
            if isinstance(value, dict):
                return "&".join(
                    encode_param(f"{key}[{k}]", v, prefix) for k, v in value.items()
                )
            return f"{prefix}{key}={urllib.parse.quote(str(value))}"

        return "&".join(encode_param(k, v) for k, v in params.items())

    def _request(
        self, function: str, params: Optional[dict[str, Any]] = None
    ) -> MoodleAPIResponse:
        url = f"{self.server_url}/webservice/rest/server.php"
        data = (
            {"wsfunction": function, **params} if params else {"wsfunction": function}
        )
        formatted_params = self._format_params(data)
        full_url = f"{url}?{formatted_params}"
        try:
            response = self.session.get(full_url)
            response.raise_for_status()
            return MoodleAPIResponse(
                status_code=response.status_code, data=response.json()
            )
        except requests.RequestException as e:
            # Handle network-related errors
            return MoodleAPIResponse(
                status_code=getattr(e.response, "status_code", None),
                data={"error": str(e)},
            )

    def _parse_courses_field(
        self, courses_data: list[dict[str, Any]]
    ) -> list[MoodleCourse]:
        parsed_courses = []
        for course_data in courses_data:
            try:
                # Handle nested structures
                course_data["summaryfiles"] = [
                    File(**f) for f in course_data.get("summaryfiles", [])
                ]
                course_data["overviewfiles"] = [
                    File(**f) for f in course_data.get("overviewfiles", [])
                ]
                course_data["contacts"] = [
                    Contact(**c) for c in course_data.get("contacts", [])
                ]
                course_data["customfields"] = [
                    CustomField(**f) for f in course_data.get("customfields", [])
                ]
                course_data["filters"] = [
                    Filter(**f) for f in course_data.get("filters", [])
                ]
                course_data["courseformatoptions"] = [
                    CourseFormatOption(**o)
                    for o in course_data.get("courseformatoptions", [])
                ]

                parsed_courses.append(MoodleCourse(**course_data))
            except (KeyError, TypeError) as e:
                raise ValueError(
                    f"Error parsing course data: {e!s}. Course data: {course_data}"
                ) from None
        return parsed_courses

    def get_site_info(self) -> MoodleAPIResponse:
        """
        Retrieve site information to verify authentication.
        """
        return self._request("core_webservice_get_site_info")

    def _parse_courses(self, courses_data: list[dict[str, Any]]) -> list[Course]:
        parsed_courses = []
        course_fields = {f.name for f in fields(Course)}
        for course_data in courses_data:
            try:
                # Filter out fields not in MoodleCourse
                filtered_data = {
                    k: v for k, v in course_data.items() if k in course_fields
                }
                parsed_courses.append(Course(**filtered_data))
            except (KeyError, TypeError) as e:
                raise ValueError(
                    f"Error parsing course data: {e!s}. Course data: {filtered_data}"
                ) from None
        return parsed_courses

    def get_categories(
        self,
        id: Optional[int] = None,
        ids: Optional[Union[str, list[int]]] = None,
        name: Optional[str] = None,
        parent: Optional[int] = None,
        idnumber: Optional[str] = None,
    ) -> MoodleAPIResponse:
        """
        Retrieve course categories.

        :param id: The category id (int)
        :param ids: Category ids separated by commas (string) or a list of integers
        :param name: The category name (string)
        :param parent: The parent category id (int)
        :param idnumber: Category idnumber (string)
        :return: MoodleAPIResponse containing category data.
        """
        criteria = []
        if id is not None:
            criteria.append({"key": "id", "value": id})
        if ids is not None:
            if isinstance(ids, list):
                ids = ",".join(map(str, ids))
            criteria.append({"key": "ids", "value": ids})
        if name is not None:
            criteria.append({"key": "name", "value": name})
        if parent is not None:
            criteria.append({"key": "parent", "value": parent})
        if idnumber is not None:
            criteria.append({"key": "idnumber", "value": idnumber})

        params = {"criteria": criteria} if criteria else {}
        response = self._request("core_course_get_categories", params)

        # Parse the response into MoodleCategory objects
        try:
            if response.status_code == 200:
                response.data = [Category(**category) for category in response.data]

            return response
        except any as e:
            return MoodleAPIResponse(status_code=500, data={"error": str(e)})

    def get_courses(self, ids: Optional[list[int]] = None) -> MoodleAPIResponse:
        """
        Retrieve courses.

        :param ids: Optional list of course IDs. If not provided, returns all courses.
        :return: MoodleAPIResponse containing course data.
        """
        params = {}
        if ids:
            params["ids"] = ids

        response = self._request("core_course_get_courses", params)

        if response.status_code == 200:
            try:
                response.data = self._parse_courses(response.data)
            except ValueError as e:
                response.error = str(e)
                response.data = None

        return response

    def get_courses_by_field(
        self,
        field: Literal["id", "ids", "shortname", "idnumber", "category"],
        value: Any = "",
    ) -> MoodleAPIResponse:
        """
        Retrieve courses by a specific field.

        :param field: The field to search. Can be left empty for all courses or:
                      id: course id
                      ids: comma separated course ids
                      shortname: course short name
                      idnumber: course id number
                      category: category id the course belongs to
        :param value: The value to search for in the specified field.
        :return: MoodleAPIResponse containing course data.
        """
        params = {"field": field, "value": value}
        response = self._request("core_course_get_courses_by_field", params)

        if response.status_code == 200 and "courses" in response.data:
            try:
                response.data["courses"] = self._parse_courses_field(
                    response.data["courses"]
                )
            except ValueError as e:
                response.error = f"Error parsing course data: {e!s}"
                response.data = None

        return response

    def get_course_updates_since(
        self,
        courseid: int,
        since: Optional[datetime] = None,
        filter: Optional[
            list[
                Literal[
                    "gradeitems",
                    "outcomes",
                    "comments",
                    "ratings",
                    "completion",
                    "fileareas",
                    "configuration",
                ]
            ]
        ] = None,
    ) -> MoodleAPIResponse:
        """
        Retrieve updates in a course since a specific time.

        :param courseid: The ID of the course to check for updates.
        :param since: A datetime object representing the time since when to check
                      for updates. If None, it will check for all updates.
        :param filter: A list of areas to filter the updates by.
                       Possible values: 'configuration', 'fileareas',
                       'completion', 'gradeitems', 'reset'
        :return: MoodleAPIResponse containing course update data.
        """
        params = {"courseid": courseid, "since": int(since.timestamp()) if since else 0}

        if filter:
            params["filter"] = filter

        response = self._request("core_course_get_updates_since", params)
        print(response.data)
        try:
            if response.status_code == 200:
                instances = []
                for instance_data in response.data.get("instances", []):
                    updates = [
                        UpdateItem(**update)
                        for update in instance_data.get("updates", [])
                    ]
                    instances.append(
                        Instance(
                            contextlevel=instance_data["contextlevel"],
                            id=instance_data["id"],
                            updates=updates,
                        )
                    )

                warnings = [Warning(**w) for w in response.data.get("warnings", [])]

                course_updates = CourseUpdatesResponse(
                    instances=instances, warnings=warnings
                )
                response.data = course_updates
            return response
        except Exception as e:
            return MoodleAPIResponse(status_code=500, data={"error": str(e)})

    def get_assignments(
        self,
        courseids: Optional[list[int]] = None,
        capabilities: Optional[list[str]] = None,
        includenotenrolledcourses: int = 0,
    ) -> MoodleAPIResponse:
        """
        Returns the courses and assignments for the users capability.

        :param courseids: Optional list of course ids. If empty returns all the courses
                          the user is enrolled in.
        :param capabilities: Optional list of capabilities used to filter courses.
        :param includenotenrolledcourses: Whether to return courses that the user can
                                          see even if is not enrolled in. This requires
                                          the parameter courseids to not be empty.
        :return: MoodleAPIResponse containing assignments data.
        """
        params = {"includenotenrolledcourses": includenotenrolledcourses}

        if courseids:
            params["courseids"] = courseids

        if capabilities:
            params["capabilities"] = capabilities

        response = self._request("mod_assign_get_assignments", params)
        try:
            if response.status_code == 200:
                courses = []
                for course_data in response.data.get("courses", []):
                    assignments = []
                    for assign_data in course_data.get("assignments", []):
                        configs = [
                            AssignmentConfig(**config)
                            for config in assign_data.get("configs", [])
                        ]
                        intro_attachments = [
                            AssignmentFile(**file)
                            for file in assign_data.get("introattachments", [])
                        ]
                        assignment = Assignment(
                            **{
                                k: v
                                for k, v in assign_data.items()
                                if k not in ("configs", "introattachments")
                            },
                            configs=configs,
                            introattachments=intro_attachments,
                        )
                        assignments.append(assignment)

                    course = CourseAssignments(
                        id=course_data["id"],
                        fullname=course_data["fullname"],
                        shortname=course_data["shortname"],
                        timemodified=course_data["timemodified"],
                        assignments=assignments,
                    )
                    courses.append(course)

                assignments_response = AssignmentsResponse(
                    courses=courses, warnings=response.data.get("warnings")
                )
                response.data = assignments_response
            return response
        except Exception as e:
            return MoodleAPIResponse(status_code=500, data={"error": str(e)})

    def get_course_contents(
        self,
        courseid: int,
        excludemodules: Optional[bool] = None,
        excludecontents: Optional[bool] = None,
        includestealthmodules: Optional[bool] = None,
        sectionid: Optional[int] = None,
        sectionnumber: Optional[str] = None,
        cmid: Optional[int] = None,
        modname: Optional[str] = None,
        modid: Optional[int] = None,
    ) -> MoodleAPIResponse:
        """
        Retrieve contents of a course.

        :param courseid: ID of the course to get contents from.
        :param options: List of options to customize the content retrieval.
                        Each option is a dict with 'name' and 'value' keys.
        :return: MoodleAPIResponse containing course content data.
        """
        params = {"courseid": courseid}
        options = []
        if excludemodules:
            options.append({"name": "excludemodules", "value": excludemodules})
        if excludecontents:
            options.append({"name": "excludecontents", "value": excludecontents})
        if includestealthmodules:
            options.append(
                {"name": "includestealthmodules", "value": includestealthmodules}
            )
        if modid:
            options.append({"name": "modid", "value": modid})
        if modname:
            options.append({"name": "modname", "value": modname})
        if sectionnumber:
            options.append({"name": "sectionnumber", "value": sectionnumber})
        if sectionid:
            options.append({"name": "sectionid", "value": sectionid})
        if cmid:
            options.append({"name": "cmid", "value": cmid})
        params["options"] = options if options else []

        response = self._request("core_course_get_contents", params)

        try:
            if response.status_code == 200:
                course_sections = []
                for section_data in response.data:
                    modules = []
                    for module_data in section_data.get("modules", []):
                        module_contents = [
                            ModuleContent(**content)
                            for content in module_data.get("contents", [])
                        ]
                        completion_data = (
                            ModuleCompletionData(**module_data["completiondata"])
                            if "completiondata" in module_data
                            else None
                        )
                        dates = [
                            ModuleDate(**date) for date in module_data.get("dates", [])
                        ]

                        module = CourseModule(
                            **{
                                k: v
                                for k, v in module_data.items()
                                if k not in ["contents", "completiondata", "dates"]
                            },
                            contents=module_contents,
                            completiondata=completion_data,
                            dates=dates,
                        )
                        modules.append(module)

                    section = CourseSection(
                        **{k: v for k, v in section_data.items() if k != "modules"},
                        modules=modules,
                    )
                    course_sections.append(section)

                response.data = course_sections
            return response
        except Exception as e:
            return MoodleAPIResponse(status_code=500, data={"error": str(e)})


client = MoodleAPIClient()
response = client.get_course_contents(courseid=2)
