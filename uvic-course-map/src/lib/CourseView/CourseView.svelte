<script lang="ts">
	import { activeCourse, activeCourseId } from './CourseView';
	import courses from '../VisTreeGraph/courses.json';
	import { graphCourseId } from '$lib/VisTreeGraph/VisTreeGraph';

	$: course = $activeCourse;
</script>

{#if course}
	<!-- content here -->
	<div
		class="prose flex max-h-[60vh] min-w-[250px] flex-col gap-4 overflow-y-scroll max-lg:max-h-[30vh]"
	>
		<button
			class="btn btn-circle btn-ghost btn-sm absolute right-8 top-2 font-extrabold"
			on:click={() => ($activeCourseId = '')}
		>
			✕</button
		>
		<div class="flex flex-col gap-0">
			<h3>
				{course.courseId}
			</h3>
			<h4>
				{course.title}
			</h4>
			<a class="link link-primary w-max" href={course.url} target="_blank" rel="noopener noreferrer"
				>See in UVic Calendar</a
			>
		</div>

		<div class="flex flex-col gap-2">
			<h4>Prerequisites</h4>
			<div>
				{@html course.htmlRequirements?.replaceAll(
					'#/courses',
					`https://www.uvic.ca/calendar/undergrad/index.php#/courses`
				)}
			</div>
		</div>
	</div>
{/if}

<style>
	a {
		color: oklch(var(--p));
	}
</style>
