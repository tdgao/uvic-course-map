import asyncio
import copy
import aiohttp
import time
import json
from bs4 import BeautifulSoup
import os

# Maximum number of concurrent requests
CONCURRENT_REQUESTS = 10
COURSE_CATALOG_JSON = "kuali-course-catalog.json"


async def fetch_course_data(session, sem, course_id):
    url = f"https://uvic.kuali.co/api/v1/catalog/course/byId/667b0a5143034a001c39ffe8/{course_id}"
    headers = {"User-Agent": "Mozilla/5.0"}  # Generic User-Agent
    async with sem:
        for attempt in range(3):  # Retry up to 3 times
            try:
                print(
                    f"Fetching data for {course_id} (attempt {attempt + 1})...",
                    flush=True,
                )
                async with session.get(url, headers=headers, timeout=10) as response:
                    response.raise_for_status()  # Raise exception for HTTP errors
                    html_content = await response.text()
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


async def fetch_course(session, sem, course_id):
    html_content = await fetch_course_data(session, sem, course_id)

    return html_content


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


async def main():
    start_time = time.time()
    print("Script started.", flush=True)

    courses_list = []
    with open(COURSE_CATALOG_JSON, "r", encoding="utf-8") as jsonfile:
        courses_list = json.load(jsonfile)

    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        tasks = []

        count = 0
        for course in courses_list:
            tasks.append(fetch_course(session, sem, course["id"]))
            count += 1
            if count > 10:
                break

        # Process tasks concurrently with progress indication
        total_tasks = len(tasks)
        completed_tasks = 0

        for future in asyncio.as_completed(tasks):
            response = await future
            completed_tasks += 1
            print(f"Completed {completed_tasks}/{total_tasks} tasks.", flush=True)
            response_json = json.loads(response)
            if response_json:
                prereqs = response_json.get("preAndCorequisites", None)
                if prereqs:
                    print(prereqs)
                    container = BeautifulSoup(prereqs, "html.parser")
                    print(get_requirements(container.find(top_ul)))

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
