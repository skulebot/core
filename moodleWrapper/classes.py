from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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


@dataclass
class UpdateItem:
    name: str
    timeupdated: Optional[int] = None
    itemids: Optional[List[int]] = None


@dataclass
class Instance:
    contextlevel: str
    id: int
    updates: List[UpdateItem]


@dataclass
class CourseUpdatesResponse:
    instances: List[Instance]
    warnings: Optional[List[Warning]] = None


@dataclass
class AssignmentFile:
    filename: str
    filepath: str
    filesize: int
    fileurl: str
    timemodified: int
    mimetype: Optional[str] = None


@dataclass
class AssignmentConfig:
    plugin: str
    subtype: str
    name: str
    value: str


@dataclass
class Assignment:
    id: int
    cmid: int
    course: int
    name: str
    nosubmissions: int
    submissiondrafts: int
    sendnotifications: int
    sendlatenotifications: int
    sendstudentnotifications: int
    duedate: int
    allowsubmissionsfromdate: int
    grade: int
    timemodified: int
    completionsubmit: int
    cutoffdate: int
    gradingduedate: int
    teamsubmission: int
    requireallteammemberssubmit: int
    teamsubmissiongroupingid: int
    blindmarking: int
    hidegrader: int
    revealidentities: int
    attemptreopenmethod: str
    maxattempts: int
    markinganonymous: int
    markingworkflow: int
    markingallocation: int
    requiresubmissionstatement: int
    preventsubmissionnotingroup: int
    configs: List[AssignmentConfig]
    intro: Optional[str] = None
    introfiles: Optional[AssignmentFile] = None
    introformat: Optional[int] = None
    timelimit: Optional[int] = None
    submissionattachments: Optional[int] = None
    introattachments: Optional[List[AssignmentFile]] = None


@dataclass
class CourseAssignments:
    id: int
    fullname: str
    shortname: str
    timemodified: int
    assignments: List[Assignment]


@dataclass
class AssignmentsResponse:
    courses: List[CourseAssignments]
    warnings: Optional[List[Dict[str, Any]]] = None


@dataclass
class ContentTag:
    id: int
    name: str
    rawname: str
    isstandard: int
    tagcollid: int
    taginstanceid: int
    taginstancecontextid: int
    itemid: int
    ordering: int
    flag: int
    viewurl: Optional[str] = None


@dataclass
class ModuleContent:
    type: str
    filename: str
    filepath: str
    filesize: int
    timemodified: int
    timecreated: int
    sortorder: int
    userid: int
    author: str
    license: str
    mimetype: Optional[str] = None
    fileurl: Optional[str] = None
    content: Optional[str] = None
    isexternalfile: Optional[int] = None
    repositorytype: Optional[str] = None
    tags: Optional[List[ContentTag]] = None


@dataclass
class ModuleCompletionData:
    state: int
    timecompleted: int
    overrideby: int
    valueused: int
    hascompletion: int
    isautomatic: int
    istrackeduser: int
    uservisible: int
    details: List[Dict[str, Any]]
    isoverallcomplete: Optional[int] = None


@dataclass
class ModuleDate:
    label: str
    timestamp: int
    relativeto: Optional[int] = None
    dataid: Optional[str] = None


@dataclass
class CourseModule:
    id: int
    name: str
    instance: Optional[int]
    modname: str
    modplural: str
    modicon: str
    indent: int
    purpose: str
    branded: int
    visible: Optional[int]
    visibleoncoursepage: Optional[int]
    uservisible: Optional[int]
    url: Optional[str] = None
    onclick: Optional[str] = None
    afterlink: Optional[str] = None
    activitybadge: Optional[str] = None
    contextid: Optional[int] = None
    groupmode: Optional[int] = None
    description: Optional[str] = None
    availabilityinfo: Optional[str] = None
    availability: Optional[str] = None
    downloadcontent: Optional[int] = None
    noviewlink: Optional[int] = None
    customdata: Optional[str] = None
    completion: Optional[int] = None
    completiondata: Optional[ModuleCompletionData] = None
    contents: Optional[List[ModuleContent]] = None
    contentsinfo: Optional[Dict[str, Any]] = None
    dates: Optional[List[ModuleDate]] = None


@dataclass
class CourseSection:
    id: int
    name: str

    summary: str
    summaryformat: int
    section: Optional[int]
    visible: Optional[int]
    hiddenbynumsections: Optional[int]
    uservisible: Optional[int]
    modules: List[CourseModule]
    availabilityinfo: Optional[str] = None
