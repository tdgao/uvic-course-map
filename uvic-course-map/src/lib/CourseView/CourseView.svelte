<script lang="ts">
	import { activeCourse } from './CourseView';

	$: course = $activeCourse;
</script>

<div class="w-[500px] p-4">
	{#if course}
		<h1>{course.courseId}, {course.title}</h1>
		<p>{@html course.htmlRequirements}</p>
	{:else}
		<p>Select a course to view</p>
	{/if}
</div>
