<script lang="ts">
	import { activeCourse, activeCourseId } from './CourseView';

	$: course = $activeCourse;
</script>

{#if course}
	<!-- content here -->
	<div
		class="prose flex max-h-[60vh] min-w-[250px] flex-col gap-4 overflow-auto max-lg:max-h-[30vh]"
	>
		<button
			class="btn btn-ghost btn-sm absolute right-6 top-2 font-bold"
			on:click={() => ($activeCourseId = '')}
		>
			Close</button
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
{:else}
	<p class="text-md text-neutral opacity-70">
		<span class="max-md:hidden">Click</span>
		<span class="md:hidden">Tap</span>
		on a course to see details
	</p>
{/if}
