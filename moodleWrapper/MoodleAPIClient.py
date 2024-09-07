import os
import requests
from dotenv import load_dotenv
from dataclasses import dataclass, fields
from typing import Optional, Dict, Any,List, Union

from classes import Category , Course

@dataclass
class MoodleAPIResponse:
    status_code: int
    data: Any

class MoodleAPIClient:
    def __init__(self, server_url: Optional[str] = None, token: Optional[str] = None):
        # Load environment variables if .env file exists
        if os.path.exists('.env'):
            load_dotenv()

        self.server_url = server_url or os.getenv('MOODLE_SERVER_URL')
        self.token = token or os.getenv('MOODLE_TOKEN')

        if not self.server_url or not self.token:
            raise ValueError("Moodle server URL and token must be provided either in .env file or as constructor arguments")

        self.session = requests.Session()
        self.session.params = {'wstoken': self.token, 'moodlewsrestformat': 'json'}

    def _request(self, function: str, params: Optional[Dict[str, Any]] = None) -> MoodleAPIResponse:
        url = f"{self.server_url}/webservice/rest/server.php"
        data = {'wsfunction': function, **params} if params else {'wsfunction': function}
        
        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            return MoodleAPIResponse(status_code=response.status_code, data=response.json())
        except requests.RequestException as e:
            # Handle network-related errors
            return MoodleAPIResponse(status_code=getattr(e.response, 'status_code', None), data={'error': str(e)})

    def get_site_info(self) -> MoodleAPIResponse:
        """
        Retrieve site information to verify authentication.
        """
        return self._request('core_webservice_get_site_info')
    
    def get_categories(self, 
                       id: Optional[int] = None, 
                       ids: Optional[Union[str, List[int]]] = None, 
                       name: Optional[str] = None, 
                       parent: Optional[int] = None, 
                       idnumber: Optional[str] = None) -> MoodleAPIResponse:
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
            criteria.append({'key': 'id', 'value': id})
        if ids is not None:
            if isinstance(ids, list):
                ids = ','.join(map(str, ids))
            criteria.append({'key': 'ids', 'value': ids})
        if name is not None:
            criteria.append({'key': 'name', 'value': name})
        if parent is not None:
            criteria.append({'key': 'parent', 'value': parent})
        if idnumber is not None:
            criteria.append({'key': 'idnumber', 'value': idnumber})

        params = {'criteria': criteria} if criteria else {}
        response = self._request('core_course_get_categories', params)
        
        # Parse the response into MoodleCategory objects
        try:
            if response.status_code == 200:
                response.data = [Category(**category) for category in response.data]
        
            return response
        except any as e:
            return MoodleAPIResponse(status_code=500, data={'error': str(e)})
    def _parse_courses(self, courses_data: List[Dict[str, Any]]) -> List[Course]:
        parsed_courses = []
        course_fields = {f.name for f in fields(Course)}
        
        for course_data in courses_data:
            try:
                # Filter out fields not in MoodleCourse
                filtered_data = {k: v for k, v in course_data.items() if k in course_fields}
                parsed_courses.append(Course(**filtered_data))
            except (KeyError, TypeError) as e:
                raise ValueError(f"Error parsing course data: {str(e)}. Course data: {filtered_data}")
        return parsed_courses


    def get_courses(self, ids: Optional[List[int]] = None) -> MoodleAPIResponse:
        """
        Retrieve courses.
        
        :param ids: Optional list of course IDs. If not provided, returns all courses.
        :return: MoodleAPIResponse containing course data.
        """
        params = {'options': {'ids': ids}} if ids else {}
        response = self._request('core_course_get_courses', params)
        
        if response.status_code == 200:
            try:
                response.data = self._parse_courses(response.data)
            except ValueError as e:
                response.error = str(e)
                print(str(e))
                response.data = None
        
        return response
    def get_courses_by_field(self, field: str, value: Any) -> MoodleAPIResponse:
        """
        Retrieve courses by a specific field.
        
        :param field: The field to filter by (e.g., 'category', 'ids', 'shortname', etc.)
        :param value: The value to filter for.
        :return: MoodleAPIResponse containing course data.
        """
        params = {'field': field, 'value': value}
        return self._request('core_course_get_courses_by_field', params)
 

client = MoodleAPIClient()
response = client.get_courses()
print(f"Status Code: {response.status_code}")
print(f"Data: {response.data}")