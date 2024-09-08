from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    id: int
    name: str
    description: str
    descriptionformat: int
    parent: int
    sortorder: int
    coursecount: int
    depth: int
    path: str
    # Optional fields
    idnumber: Optional[str] = None
    visible: Optional[int] = None
    visibleold: Optional[int] = None
    timemodified: Optional[int] = None
    theme: Optional[str] = None


@dataclass
class CourseFormatOption:
    name: str
    value: str


@dataclass
class Course:
    id: int
    shortname: str
    categoryid: int
    fullname: str
    displayname: str
    summary: str
    summaryformat: int
    format: str
    startdate: int
    enddate: int
    showactivitydates: int
    showcompletionconditions: int
    numsections: Optional[int] = None
    maxbytes: Optional[int] = None
    showreports: Optional[int] = None
    visible: Optional[int] = None
    hiddensections: Optional[int] = None
    groupmode: Optional[int] = None
    groupmodeforce: Optional[int] = None
    defaultgroupingid: Optional[int] = None
    timecreated: Optional[int] = None
    timemodified: Optional[int] = None
    enablecompletion: Optional[int] = None
    completionnotify: Optional[int] = None
    lang: Optional[str] = None
    categorysortorder: Optional[int] = None
    forcetheme: Optional[str] = None
    showgrades: Optional[int] = None
    newsitems: Optional[int] = None
    idnumber: Optional[str] = None
