<script lang="ts">
	import { activeCourse } from './CourseView';
	import courses from '../VisTreeGraph/courses.json';
	import { graphCourseId } from '$lib/VisTreeGraph/VisTreeGraph';

	$: course = $activeCourse;

	const courseIds = Object.keys(courses);
</script>

<div class="prose flex w-[500px] flex-col gap-4 p-4">
	<div class="flex flex-col gap-2">
		<h3>Map course</h3>
		<input
			type="search"
			list="all-course-ids"
			placeholder="CSC360"
			class="input input-bordered w-full max-w-xs"
			bind:value={$graphCourseId}
		/>

		<datalist id="all-course-ids">
			{#each courseIds as id}
				<option value={id}></option>
			{/each}
		</datalist>
	</div>

	{#if course}
		<div class="flex flex-col gap-0">
			<h2>
				{course.courseId}
				<br />
				{course.title}
			</h2>
			<a class="link link-primary w-max" href={course.url} target="_blank" rel="noopener noreferrer"
				>See in UVic Calendar</a
			>
		</div>

		<div class="flex flex-col gap-2">
			<h3>Prerequisites</h3>
			<div>
				{@html course.htmlRequirements?.replaceAll(
					'#/courses',
					'https://www.uvic.ca/calendar/undergrad/index.php#/courses'
				)}
			</div>
		</div>
	{:else}
		<p>Select a course to view</p>
	{/if}
</div>
