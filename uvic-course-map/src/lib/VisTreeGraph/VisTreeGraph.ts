import { writable } from 'svelte/store';

export const graphCourseId = writable('CSC320');
export const maxDownDepth = writable<number>(1);
