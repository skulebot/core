from moodleWrapper.MoodleAPIClient import MoodleAPIClient


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
