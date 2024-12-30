import { writable } from 'svelte/store';

export const graphCourseId = writable('SENG265');
export const maxDownDepth = writable<number>(1);
