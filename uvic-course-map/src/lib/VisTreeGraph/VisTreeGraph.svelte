<script lang="ts">
	import { onMount } from 'svelte';
	import { Network } from 'vis-network';
	import coursesData from './courses.json';

	let networkContainer: HTMLElement;
	let targetCourseId = 'CSC115'; // for demonstration

	//------------------------------------------------------------------
	// 1. Upstream: gather all prerequisites (ancestors)
	//------------------------------------------------------------------
	function getUpstreamCourses(courseId: string, allCourses: any, visited = new Set<string>()) {
		if (!allCourses[courseId] || visited.has(courseId)) {
			return visited;
		}
		visited.add(courseId);

		const prereqIds = extractAllCourseIds(allCourses[courseId].parsedRequirements);
		for (const pId of prereqIds) {
			getUpstreamCourses(pId, allCourses, visited);
		}
		return visited;
	}

	//------------------------------------------------------------------
	// 2. Downstream: gather all courses that depend on `courseId`
	//------------------------------------------------------------------
	function getDownstreamCourses(courseId: string, allCourses: any, visited = new Set<string>()) {
		if (!allCourses[courseId] || visited.has(courseId)) {
			return visited;
		}
		visited.add(courseId);

		for (const cId in allCourses) {
			const prereqIds = extractAllCourseIds(allCourses[cId].parsedRequirements);
			if (prereqIds.includes(courseId)) {
				getDownstreamCourses(cId, allCourses, visited);
			}
		}
		return visited;
	}

	//------------------------------------------------------------------
	// 3. Extract all recognized course IDs from the raw `parsedRequirements`
	//------------------------------------------------------------------
	function extractAllCourseIds(requirements: any): string[] {
		if (!requirements) return [];
		let results: string[] = [];

		if (Array.isArray(requirements)) {
			for (const item of requirements) {
				results = results.concat(extractAllCourseIds(item));
			}
		} else if (typeof requirements === 'object') {
			for (const key of Object.keys(requirements)) {
				const val = requirements[key];
				results = results.concat(extractAllCourseIds(val));
			}
		} else if (typeof requirements === 'string') {
			// If it matches standard pattern like CSC110\nMATH100
			if (requirements.match(/^[A-Z]{2,4}\d{3}[A-Z]?$/)) {
				results.push(requirements);
			}
		}
		return results;
	}

	//------------------------------------------------------------------
	// 4. Parse each requirement into a "composite" block:
	//    {
	//      type: 'composite',
	//      label: 'CSC110\nCSC111\n...',
	//      subCourses: ['CSC110', 'CSC111', ...]
	//    }
	//
	//   \na single course block:
	//    {
	//      type: 'course',
	//      courseId: 'CSC110'
	//    }
	//------------------------------------------------------------------
	function parseRequirement(
		requirement: any
	):
		| { type: 'course'; courseId: string }
		| { type: 'composite'; label: string; subCourses: string[] }
		| null {
		/**
		 * If requirement is an object like:
		 * { "Complete 1 of the following": [ "CSC110", "CSC111" ] }
		 * => we gather subCourses = ["CSC110", "CSC111"]
		 * => label = "CSC110\nCSC111"
		 * => return { type: 'composite', label, subCourses }
		 *
		 * If requirement is a string like "CSC110" => { type: 'course', courseId: 'CSC110' }
		 */

		// (A) If array, combine them all into one composite
		if (Array.isArray(requirement)) {
			// E.g. [ "CSC110", "MATH100" ]
			let subCourses: string[] = [];
			for (const item of requirement) {
				const parsedItem = parseRequirement(item);
				if (!parsedItem) continue;

				if (parsedItem.type === 'course') {
					subCourses.push(parsedItem.courseId);
				} else if (parsedItem.type === 'composite') {
					// e.g. sub-composite => merge them
					subCourses = subCourses.concat(parsedItem.subCourses);
				}
			}
			if (subCourses.length === 0) return null;
			if (subCourses.length === 1) {
				// If only one sub-course, no need for 'or' label
				return { type: 'course', courseId: subCourses[0] };
			}
			const label = subCourses.join('\n');
			return { type: 'composite', label, subCourses };
		}

		// (B) If object with a key like "Complete 1 of the following"
		if (typeof requirement === 'object' && requirement !== null) {
			const keys = Object.keys(requirement);
			if (keys.length === 1) {
				// e.g. "Complete 1 of the following": [ "CSC110", "CSC111" ]
				const key = keys[0];
				const val = requirement[key];
				// parse the subrequirements
				const parsedVal = parseRequirement(val); // might be course\ncomposite
				if (!parsedVal) return null;

				if (parsedVal.type === 'course') {
					// if the sub is just one course
					return {
						type: 'composite',
						label: parsedVal.courseId,
						subCourses: [parsedVal.courseId]
					};
				} else if (parsedVal.type === 'composite') {
					// use the same subCourses, but rename the label
					return {
						type: 'composite',
						label: parsedVal.subCourses.join('\n'),
						subCourses: parsedVal.subCourses
					};
				}
			} else {
				// If multiple keys, combine them all
				let combinedCourses: string[] = [];
				for (const k of keys) {
					const subVal = requirement[k];
					const parsedVal = parseRequirement(subVal);
					if (!parsedVal) continue;

					if (parsedVal.type === 'course') {
						combinedCourses.push(parsedVal.courseId);
					} else if (parsedVal.type === 'composite') {
						combinedCourses = combinedCourses.concat(parsedVal.subCourses);
					}
				}
				if (combinedCourses.length === 0) return null;
				if (combinedCourses.length === 1) {
					return { type: 'course', courseId: combinedCourses[0] };
				}
				const label = combinedCourses.join('\n');
				return { type: 'composite', label, subCourses: combinedCourses };
			}
		}

		// (C) If a string like "CSC110"
		if (typeof requirement === 'string') {
			// If it's a recognized course code
			if (requirement.match(/^[A-Z]{2,4}\d{3}[A-Z]?$/)) {
				return { type: 'course', courseId: requirement };
			} else {
				// Some non-standard string, treat it like a "course"
				return { type: 'course', courseId: requirement };
			}
		}

		// Fallback
		return null;
	}

	//------------------------------------------------------------------
	// 5. Build the Vis.js graph: subCourse -> composite -> main course
	//------------------------------------------------------------------
	let artificialNodeCount = 0;

	function buildGraphData(courseIds: Set<string>, allCourses: any) {
		const nodes: any[] = [];
		const edges: any[] = [];

		// Make sure each real course in the set has a node
		for (const cId of courseIds) {
			const c = allCourses[cId];
			if (!c) continue;
			nodes.push({
				id: cId,
				label: cId,
				title: c.title || cId,
				shape: 'ellipse',
				color: '#97C2FC'
			});
		}

		// For each course, parse its requirements
		for (const cId of courseIds) {
			const c = allCourses[cId];
			if (!c) continue;
			const reqArray = c.parsedRequirements;
			if (!reqArray || reqArray.length === 0) continue;

			// We can have multiple top-level blocks, e.g.
			// [
			//   { "Complete 1 of the following": [... ] },
			//   { "Complete 2 of the following": [... ] }
			// ]
			for (const block of reqArray) {
				const parsed = parseRequirement(block);
				if (!parsed) continue;

				// If it's a single course, connect directly:
				if (parsed.type === 'course') {
					const childId = parsed.courseId;
					// If child course doesn't exist in nodes, add it
					if (!nodes.find((n) => n.id === childId)) {
						nodes.push({
							id: childId,
							label: childId,
							shape: 'ellipse',
							color: '#DDD'
						});
					}
					edges.push({ from: childId, to: cId, arrows: 'to' });
				}
				// If it's a composite => create the composite node,
				// then connect each subCourse -> composite -> cId
				else if (parsed.type === 'composite') {
					const compositeId = `composite_${++artificialNodeCount}`;
					nodes.push({
						id: compositeId,
						label: parsed.label, // e.g. "CSC110\nCSC111"
						shape: 'box',
						color: '#FFC107',
						font: { size: 10 }
					});

					// Connect composite node -> parent course
					edges.push({
						from: compositeId,
						to: cId,
						arrows: 'to'
					});

					// For each subCourse in parsed.subCourses,
					// connect subCourse -> composite node
					for (const subC of parsed.subCourses) {
						// If subC doesn't exist as a node, add it
						if (!nodes.find((n) => n.id === subC)) {
							nodes.push({
								id: subC,
								label: subC,
								shape: 'ellipse',
								color: '#DDD'
							});
						}
						edges.push({
							from: subC,
							to: compositeId,
							arrows: 'to'
						});
					}
				}
			}
		}

		return { nodes, edges };
	}

	//------------------------------------------------------------------
	// 6. onMount -> gather upstream + downstream, build the network
	//------------------------------------------------------------------
	onMount(() => {
		const upstreamSet = getUpstreamCourses(targetCourseId, coursesData);
		const downstreamSet = getDownstreamCourses(targetCourseId, coursesData);
		const combinedSet = new Set<string>([...upstreamSet, ...downstreamSet]);

		const { nodes, edges } = buildGraphData(combinedSet, coursesData);

		const data = { nodes, edges };
		const options = {
			layout: {
				hierarchical: {
					enabled: true,
					direction: 'UD',
					sortMethod: 'directed',
					levelSeparation: 150,
					nodeSpacing: 150
				}
			},
			physics: { enabled: false },
			interaction: {
				dragNodes: false,
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
