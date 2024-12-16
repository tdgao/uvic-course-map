Prereq scraper documentation:

- It gets all the pre and co-reqs for every course and put it into a giant json.
- To do this, it uses the kuali end point at `https://uvic.kuali.co/api/v1/catalog/course/byId/667b0a5143034a001c39ffe8/{course_id}`
- Each course id is found from the course catalog json. (retrieved from https://uvic.kuali.co/api/v1/catalog/courses/65eb47906641d7001c157bc4/)

