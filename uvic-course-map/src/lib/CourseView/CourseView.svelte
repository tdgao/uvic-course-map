<script lang="ts">
	import { activeCourse } from './CourseView';
	import courses from '../VisTreeGraph/courses.json';
	import { graphCourseId } from '$lib/VisTreeGraph/VisTreeGraph';

	$: course = $activeCourse;

	const courseIds = Object.keys(courses);

	function sanitize(str: string) {
		return str.replace(/\W+/g, '').toUpperCase();
	}

	// Use Levenshtein Distance :O
	function levenshtein(a: string, b: string): number {
		const an = a.length;
		const bn = b.length;
		if (an === 0) return bn;
		if (bn === 0) return an;

		const matrix: number[][] = [];

		for (let i = 0; i <= bn; i++) {
			matrix[i] = [i];
		}
		for (let j = 0; j <= an; j++) {
			matrix[0][j] = j;
		}

		for (let i = 1; i <= bn; i++) {
			for (let j = 1; j <= an; j++) {
				if (b.charAt(i - 1) === a.charAt(j - 1)) {
					matrix[i][j] = matrix[i - 1][j - 1];
				} else {
					matrix[i][j] = Math.min(
						matrix[i - 1][j - 1] + 1,
						matrix[i][j - 1] + 1,
						matrix[i - 1][j] + 1
					);
				}
			}
		}

		return matrix[bn][an];
	}

	function getClosestCourseId(input: string, courseIds: string[]): string {
		const sanitizedInput = sanitize(input);

		let bestId = courseIds[0];
		let bestDistance = Infinity;

		for (const cId of courseIds) {
			const distance = levenshtein(sanitizedInput, sanitize(cId));
			if (distance < bestDistance) {
				bestDistance = distance;
				bestId = cId;
			}
		}

		return bestId; // the closest match
	}

	let searchCourseId = $graphCourseId;

	const searchCourseOnChange = () => {
		const matchedId = getClosestCourseId(searchCourseId, courseIds);
		graphCourseId.set(matchedId);
		searchCourseId = matchedId;
	};
</script>

<div class="prose flex w-[500px] flex-col gap-4 p-4">
	<div class="flex flex-col gap-2">
		<h3>Map course</h3>
		<input
			type="search"
			list="all-course-ids"
			placeholder="CSC360"
			class="input input-bordered w-full max-w-xs"
			bind:value={searchCourseId}
			onchange={searchCourseOnChange}
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
			</h2>
			<h3>
				{course.title}
			</h3>
			<a class="link link-primary w-max" href={course.url} target="_blank" rel="noopener noreferrer"
				>See in UVic Calendar</a
			>
		</div>

		<div class="flex flex-col gap-2">
			<h3>Prerequisites</h3>
			<div>
				{@html course.htmlRequirements?.replaceAll(
					'#/courses',
					`https://www.uvic.ca/calendar/undergrad/index.php#/courses`
				)}
			</div>
		</div>
	{:else}
		<p>Select a course to view</p>
	{/if}
</div>

<style>
	a {
		color: oklch(var(--p));
	}
</style>
