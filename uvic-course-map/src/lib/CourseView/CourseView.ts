import { writable, derived, type Readable } from 'svelte/store';
import coursesData from '../VisTreeGraph/courses.json';

export interface Course {
	courseId: string;
	title: string;
	pid: string;
	parsedRequirements: string;
	htmlRequirements: string | null;
	url: string;
}

export const activeCourseId = writable<string>('');

export const activeCourse: Readable<Course | null> = derived(activeCourseId, ($activeCourseId) => {
	if (!$activeCourseId) {
		return null;
	}
	// @ts-ignore
	const found = coursesData[$activeCourseId] as Course | undefined;
	return found ?? null;
});
