import asyncio
import copy
import aiohttp
import time
import json
from bs4 import BeautifulSoup
import sys


# Maximum number of concurrent requests
CONCURRENT_REQUESTS = 10
COURSE_CATALOG_JSON = "kuali-course-catalog.json"  # retrieved from https://uvic.kuali.co/api/v1/catalog/courses/65eb47906641d7001c157bc4/
OUTPUT_JSON = "courses.json"  # output file for parsed courses
test_mode = False


def get_requirements(ul):
    if ul == None:
        return []
    requirements = []

    # all_top_ul = ul.find_all(top_ul)
    # print(len(ul.find_parents("ul")) == 0)

    for li in ul.find_all(["li", "div"], recursive=False):
        nested_ul = li.find("ul")
        if nested_ul:
            # title (complete all of the following, complete all of, compete 1 of)
            li_title = copy.copy(li)
            li_title.find("ul").decompose()

            nested_req = {li_title.get_text(): get_requirements(nested_ul)}
            requirements.append(nested_req)
        else:
            if (
                li
            ):  # if req has link, will return linked text (BIO123 instead of BIO123 - some description)
                if li.find("a"):
                    requirements.append(li.find("a").get_text())
                else:
                    requirements.append(li.get_text())

    return requirements


def top_ul(tag):
    return len(tag.find_parents("ul")) == 0 and tag.name == "ul"


# format is in the following:
# 	"CSC299": {
# 		"courseId": "CSC299",
# 		"title": "Undergraduate Directed Project",
# 		"pid": "rk29yO6XE",
# 		"parsedRequirements": [
# 			{
# 				"Complete  all  of the following": [
# 					{
# 						"Complete  2  of the following": [
# 							{ "Earn a minimum grade of B+ in each of the following: ": ["CSC115"] },
# 							{ "Earn a minimum grade of B+ in each of the following: ": ["CSC226"] },
# 							{ "Earn a minimum grade of B+ in each of the following: ": ["CSC230"] },
# 							{ "Earn a minimum grade of B+ in each of the following: ": ["SENG265"] }
# 						]
# 					},
# 					"permission of the department."
# 				]
# 			}
# 		],
# 		"htmlRequirements": "<div><div><div><ul><li><span>Complete <!-- -->all<!-- --> of the following</span><ul><div><span></span><li><span>Complete <!-- -->2<!-- --> of the following</span><ul><li data-test=\"ruleView-A.1\"><div data-test=\"ruleView-A.1-result\">Earn a minimum grade of <span>B+</span> in each of the following: <div><ul style=\"margin-top:5px;margin-bottom:5px\"><li><span><a href=\"#/courses/view/5cbdf4e567a5c324003b0bb6\" target=\"_blank\">CSC115</a> <!-- -->- <!-- -->Fundamentals of Programming II<!-- --> <span style=\"margin-left:5px\">(1.5)</span></span></li></ul></div></div></li><li data-test=\"ruleView-A.2\"><div data-test=\"ruleView-A.2-result\">Earn a minimum grade of <span>B+</span> in each of the following: <div><ul style=\"margin-top:5px;margin-bottom:5px\"><li><span><a href=\"#/courses/view/5cbdf4eb67a5c324003b0bc0\" target=\"_blank\">CSC226</a> <!-- -->- <!-- -->Algorithms and Data Structures II<!-- --> <span style=\"margin-left:5px\">(1.5)</span></span></li></ul></div></div></li><li data-test=\"ruleView-A.3\"><div data-test=\"ruleView-A.3-result\">Earn a minimum grade of <span>B+</span> in each of the following: <div><ul style=\"margin-top:5px;margin-bottom:5px\"><li><span><a href=\"#/courses/view/5cbdf4ec67a5c324003b0bc3\" target=\"_blank\">CSC230</a> <!-- -->- <!-- -->Introduction to Computer Architecture<!-- --> <span style=\"margin-left:5px\">(1.5)</span></span></li></ul></div></div></li><li data-test=\"ruleView-A.4\"><div data-test=\"ruleView-A.4-result\">Earn a minimum grade of <span>B+</span> in each of the following: <div><ul style=\"margin-top:5px;margin-bottom:5px\"><li><span><a href=\"#/courses/view/5cbdf65404ce072400156009\" target=\"_blank\">SENG265</a> <!-- -->- <!-- -->Software Development Methods<!-- --> <span style=\"margin-left:5px\">(1.5)</span></span></li></ul></div></div></li></ul></li></div><li data-test=\"ruleView-B\"><div data-test=\"ruleView-B-result\"><div>permission of the department.</div></div></li></ul></li></ul></div></div></div>",
# 		"url": "https://www.uvic.ca/calendar/undergrad/index.php#/courses/rk29yO6XE"
# 	},
def transform_course_data(original_json):
    course_key = original_json.get("__catalogCourseId", "UNKNOWN_COURSE")
    prereqs = original_json.get("preAndCorequisites", None)
    transformed = {
        "courseId": course_key,
        "title": original_json.get("title", ""),
        "pid": original_json.get("pid", ""),
        "parsedRequirements": (
            get_requirements(BeautifulSoup(prereqs, "html.parser").find(top_ul))
            if prereqs
            else []
        ),
        "htmlRequirements": original_json.get("preAndCorequisites", ""),
        "url": f"https://www.uvic.ca/calendar/undergrad/index.php#/courses/{original_json.get('pid','')}",
    }

    return {course_key: transformed}


async def fetch_course_data(session, sem, course_id):
    url = f"https://uvic.kuali.co/api/v1/catalog/course/byId/667b0a5143034a001c39ffe8/{course_id}"
    headers = {"User-Agent": "Mozilla/5.0"}  # Generic User-Agent
    async with sem:
        for attempt in range(3):  # Retry up to 3 times
            try:
                if test_mode or attempt > 1:
                    print(
                        f"Fetching data for {course_id} (attempt {attempt + 1})...",
                        flush=True,
                    )
                async with session.get(url, headers=headers, timeout=10) as response:
                    response.raise_for_status()  # Raise exception for HTTP errors
                    html_content = await response.text()
                    if test_mode or attempt > 1:
                        print(f"Successfully fetched data for {course_id}.", flush=True)
                    return html_content
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                wait_time = 2**attempt
                print(
                    f"Attempt {attempt + 1} failed for {course_id}: {e}. Retrying in {wait_time} seconds...",
                    flush=True,
                )
                await asyncio.sleep(wait_time)
        print(f"Failed to fetch data for {course_id} after 3 attempts.", flush=True)
        return None


async def main():
    global test_mode
    start_time = time.time()
    print("Script started.", flush=True)

    if len(sys.argv) > 1 and sys.argv[1] == "-test":
        print("Entering test mode\n")
        test_mode = True

    all_courses_parsed = {}  # the final courses json
    courses_list = []
    with open(COURSE_CATALOG_JSON, "r", encoding="utf-8") as jsonfile:
        courses_list = json.load(jsonfile)

    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for count, course in enumerate(courses_list):
            tasks.append(fetch_course_data(session, sem, course["id"]))

            # for testing
            if test_mode and count > 100:
                break

        # Process tasks concurrently with progress indication
        total_tasks = len(tasks)
        completed_tasks = 0

        for future in asyncio.as_completed(tasks):
            response = await future
            completed_tasks += 1
            if test_mode:
                print(f"Completed {completed_tasks}/{total_tasks} tasks.", flush=True)

            # Handle response and get parsed course data
            response_json = json.loads(response)
            if response_json:
                course_reqs = transform_course_data(response_json)
                all_courses_parsed = {**all_courses_parsed, **course_reqs}

    # Writing to courses.json
    with open(OUTPUT_JSON, "w") as outfile:
        outfile.write(json.dumps(all_courses_parsed))

    end_time = time.time()
    total_time = end_time - start_time
    hours, rem = divmod(total_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print(
        "Script execution time: {:0>2}:{:0>2}:{:05.2f}".format(
            int(hours), int(minutes), seconds
        ),
        flush=True,
    )
    print("Script finished.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
