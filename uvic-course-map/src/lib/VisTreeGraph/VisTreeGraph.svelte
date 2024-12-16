<script lang="ts">
	import coursesData from './courses.json';
	import { onMount } from 'svelte';
	import { Network } from 'vis-network';

	let networkContainer: HTMLElement;

	// Helper function to extract all course IDs from parsedRequirements
	// This function will recursively search for strings that look like course IDs
	function extractPrereqCourses(requirements: any): string[] {
		let prereqs: string[] = [];

		if (Array.isArray(requirements)) {
			// If it's an array, check each item
			for (const item of requirements) {
				if (typeof item === 'string') {
					// Check if it looks like a course code (e.g., CSC349A, CSC110)
					if (item.match(/^[A-Z]{2,4}\d{3}[A-Z]?$/)) {
						prereqs.push(item);
					}
				} else if (typeof item === 'object' && item !== null) {
					// Recursively process nested objects/arrays
					prereqs = prereqs.concat(extractPrereqCourses(item));
				}
			}
		} else if (typeof requirements === 'object' && requirements !== null) {
			// If it's an object, iterate through its values
			for (const key in requirements) {
				const val = requirements[key];
				prereqs = prereqs.concat(extractPrereqCourses(val));
			}
		}

		return prereqs;
	}

	// Build nodes and edges from the coursesData
	function buildGraphData(courses: any) {
		const nodes = [];
		const edges = [];

		// Create a node for each course
		for (const courseId in courses) {
			const course = courses[courseId];
			nodes.push({ id: courseId, label: courseId + '\n' + course.title });
		}

		// Create edges based on prerequisites
		for (const courseId in courses) {
			const course = courses[courseId];
			const prereqs = extractPrereqCourses(course.parsedRequirements);

			// For each prereq course, create an edge from prereq to this course
			// Only add the edge if the prereq is also a known courseId in coursesData.
			for (const p of prereqs) {
				if (courses[p]) {
					edges.push({ from: p, to: courseId });
				} else {
					// If prereq isn't found in our courses, you can ignore or add it as a standalone node
					// For simplicity, let's ignore unknown prereqs not in coursesData
				}
			}
		}

		return { nodes, edges };
	}

	onMount(() => {
		const filtered = Object.fromEntries(
			Object.entries(coursesData).filter(([key]) => key.startsWith('CSC'))
		);
		const { nodes, edges } = buildGraphData(filtered);

		const data = {
			nodes,
			edges
		};

		const options = {
			layout: {
				hierarchical: {
					enabled: true,
					direction: 'UD', // top-to-bottom or 'LR' left-to-right
					sortMethod: 'directed',
					levelSeparation: 200, // Increase this for more vertical space between levels
					nodeSpacing: 250 // Increase this for more horizontal space between nodes on the same level
				}
			},
			physics: {
				enabled: false // Disable physics to keep nodes in a stable layout
			},
			interaction: {
				dragNodes: false, // Optional: prevent moving nodes
				zoomView: true
			}
		};

		new Network(networkContainer, data, options);
	});
</script>

<div class="network-container" bind:this={networkContainer}></div>

<style>
	.network-container {
		width: 100%;
		height: 100vh;
		border: 1px solid #ccc;
		box-sizing: border-box;
	}
</style>
