from dataclasses import dataclass, field
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


@dataclass
class File:
    filename: Optional[str] = None
    filepath: Optional[str] = None
    filesize: Optional[int] = None
    fileurl: Optional[str] = None
    timemodified: Optional[int] = None
    mimetype: Optional[str] = None
    isexternalfile: Optional[int] = None
    repositorytype: Optional[str] = None
    icon: Optional[str] = None


@dataclass
class Contact:
    id: int
    fullname: str


@dataclass
class CustomField:
    name: str
    shortname: str
    type: str
    valueraw: str
    value: str


@dataclass
class Filter:
    filter: str
    localstate: int
    inheritedstate: int


@dataclass
class MoodleCourse:
    id: int
    fullname: str
    displayname: str
    shortname: str
    categoryid: int
    categoryname: str
    summary: str
    summaryformat: int
    showactivitydates: int
    showcompletionconditions: int
    contacts: list[Contact] = field(default_factory=list)
    enrollmentmethods: list[str] = field(default_factory=list)
    customfields: list[CustomField] = field(default_factory=list)
    filters: list[Filter] = field(default_factory=list)
    courseformatoptions: list[CourseFormatOption] = field(default_factory=list)
    summaryfiles: list[File] = field(default_factory=list)
    overviewfiles: list[File] = field(default_factory=list)
    idnumber: Optional[str] = None
    format: Optional[str] = None
    showgrades: Optional[int] = None
    newsitems: Optional[int] = None
    startdate: Optional[int] = None
    enddate: Optional[int] = None
    maxbytes: Optional[int] = None
    showreports: Optional[int] = None
    visible: Optional[int] = None
    groupmode: Optional[int] = None
    groupmodeforce: Optional[int] = None
    defaultgroupingid: Optional[int] = None
    enablecompletion: Optional[int] = None
    completionnotify: Optional[int] = None
    lang: Optional[str] = None
    theme: Optional[str] = None
    marker: Optional[int] = None
    legacyfiles: Optional[int] = None
    calendartype: Optional[str] = None
    timecreated: Optional[int] = None
    timemodified: Optional[int] = None
    requested: Optional[int] = None
    cacherev: Optional[int] = None
    sortorder: Optional[int] = None
    courseimage: Optional[str] = None
    communicationroomname: Optional[str] = None
    communicationroomurl: Optional[str] = None


class Warning:
    item: Optional[str] = None
    itemid: Optional[int] = None
    warningcode: str
    message: str
