# UVic Course Map

This tool helps you see which courses require a specific prerequisite, making it easier to plan your courses.

## Features

- Enter a course to see all subsequent courses that list it as a prerequisite.
- Click on courses in the graph for more details.

## Motivation

I often found it hard to determine which courses I might miss out on if I skipped a prerequisite. The UVic academic calendar lists prerequisites but doesn't show the courses that depend on them. This tool fills that gap, simplifying course planning.

## Live Application

Try it out here: [UVic Course Map](https://uvic-course-map.vercel.app)

## Repository Structure

- **Web App**: Located in the `uvic-course-map` directory, built with Svelte.
- **Course Data Scraper**: Found in the `scraper` directory, a Python script that scrapes course information from the uvic academic calendar.

## Note

This tool isn't thoroughly tested; please verify important information independently.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve this tool.
