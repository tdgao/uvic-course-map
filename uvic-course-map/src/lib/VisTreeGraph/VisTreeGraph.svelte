<script lang="ts">
	import { onMount } from 'svelte';
	import { Network, type Node, type Options } from 'vis-network';
	import coursesData from './courses.json';
	import { activeCourseId } from '$lib/CourseView/CourseView';
	import { maxDownDepth, graphCourseId } from './VisTreeGraph';

	// colours
	const blue = '#65c3c8';
	const yellow = '#eeaf3a';

	let networkContainer: HTMLElement;
	let network: Network | null;

	//------------------------------------------------------------
	// 1. Extract recognized course IDs from parsedRequirements
	//------------------------------------------------------------
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
			// e.g. "CSC110" or "MATH100" or "Pre-Calculus 12"
			if (requirements.match(/^[A-Z]{2,4}\d{3}[A-Z]?$/)) {
				results.push(requirements);
			}
		}

		return results;
	}

	//------------------------------------------------------------
	// 2. Upstream traversal with maxDepth
	//------------------------------------------------------------
	function getUpstreamCourses(
		courseId: string,
		allCourses: any,
		visited = new Set<string>(),
		currentDepth = 0,
		maxDepth = Infinity
	) {
		// Stop if invalid or already visited
		if (!allCourses[courseId] || visited.has(courseId)) {
			return visited;
		}
		visited.add(courseId);

		// If we've reached the limit, do not recurse further
		if (currentDepth >= maxDepth) {
			return visited;
		}

		// Otherwise, gather prerequisites and go deeper
		const prereqIds = extractAllCourseIds(allCourses[courseId].parsedRequirements);
		for (const pId of prereqIds) {
			getUpstreamCourses(pId, allCourses, visited, currentDepth + 1, maxDepth);
		}

		return visited;
	}

	//------------------------------------------------------------
	// 3. Downstream traversal with maxDepth
	//------------------------------------------------------------
	function getDownstreamCourses(
		courseId: string,
		allCourses: any,
		visited = new Set<string>(),
		currentDepth = 0,
		maxDepth = Infinity
	) {
		if (!allCourses[courseId] || visited.has(courseId)) {
			return visited;
		}
		visited.add(courseId);

		if (currentDepth >= maxDepth) {
			return visited;
		}

		// For each course in allCourses, check if it depends on courseId
		for (const cId in allCourses) {
			const prereqIds = extractAllCourseIds(allCourses[cId].parsedRequirements);
			if (prereqIds.includes(courseId)) {
				getDownstreamCourses(cId, allCourses, visited, currentDepth + 1, maxDepth);
			}
		}
		return visited;
	}

	//------------------------------------------------------------
	// 4. Parse a single requirement into either:
	//    - { type: 'course', courseId: 'CSC110' }
	//    - { type: 'composite', label: 'CSC110 or CSC111', subCourses: [...] }
	//------------------------------------------------------------
	function parseRequirement(
		requirement: any
	):
		| { type: 'course'; courseId: string }
		| { type: 'composite'; label: string; subCourses: string[] }
		| null {
		// (A) If it's an array (e.g. [ "CSC110", "MATH100" ])
		if (Array.isArray(requirement)) {
			let subCourses: string[] = [];
			for (const item of requirement) {
				const parsedItem = parseRequirement(item);
				if (!parsedItem) continue;

				if (parsedItem.type === 'course') {
					subCourses.push(parsedItem.courseId);
				} else if (parsedItem.type === 'composite') {
					subCourses = subCourses.concat(parsedItem.subCourses);
				}
			}

			if (subCourses.length === 0) return null;
			if (subCourses.length === 1) {
				// Only one sub-course
				return { type: 'course', courseId: subCourses[0] };
			}

			return {
				type: 'composite',
				label: subCourses.join('\n'),
				subCourses
			};
		}

		// (B) If it's an object (e.g. { "Complete 1 of:": ["CSC110", "CSC111"] })
		if (typeof requirement === 'object' && requirement !== null) {
			const keys = Object.keys(requirement);
			if (keys.length === 1) {
				const key = keys[0]; // e.g. "Complete 1 of the following"
				const val = requirement[key];
				const parsedVal = parseRequirement(val);
				if (!parsedVal) return null;

				if (parsedVal.type === 'course') {
					// e.g. only one course
					return {
						type: 'composite',
						label: parsedVal.courseId,
						subCourses: [parsedVal.courseId]
					};
				} else if (parsedVal.type === 'composite') {
					// merges subCourses
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
				return {
					type: 'composite',
					label: combinedCourses.join('\n'),
					subCourses: combinedCourses
				};
			}
		}

		// (C) If it's a string (course code or plain text)
		if (typeof requirement === 'string') {
			// e.g. "CSC110", "Pre-Calculus 12"
			return { type: 'course', courseId: requirement };
		}

		// Fallback
		return null;
	}

	//------------------------------------------------------------
	// 5. Build the final Vis.js graph
	//    subCourse -> compositeNode -> parentCourse
	//------------------------------------------------------------
	let artificialNodeCount = 0;

	function buildGraphData() {
		// Example: only go 2 levels upstream, and 1 level downstream
		const maxUpDepth = 0;

		// Gather upstream, downstream
		const upstreamSet = getUpstreamCourses($graphCourseId, coursesData, new Set(), 0, maxUpDepth);
		const downstreamSet = getDownstreamCourses(
			$graphCourseId,
			coursesData,
			new Set(),
			0,
			$maxDownDepth
		);
		const combinedSet = new Set<string>([...upstreamSet, ...downstreamSet]);

		const courseIds = combinedSet;

		const nodes: Node[] = [];
		const edges: any[] = [];

		// Ensure each real course has a node
		for (const cId of courseIds) {
			//@ts-ignore
			const course = coursesData[cId];
			if (!course) continue;
			const newNode: Node = {
				id: cId,
				label: cId,
				title: course.title || cId, // e.g. CSC 110
				shape: cId === $graphCourseId ? 'circle' : 'box',
				color: blue
			};
			nodes.push(newNode);
		}

		// Parse each course's requirements, build connections
		for (const cId of courseIds) {
			//@ts-ignore
			const course = coursesData[cId];
			if (!course) continue;
			const reqArray = course.parsedRequirements;
			if (!reqArray || reqArray.length === 0) continue;

			// Each top-level requirement
			for (const block of reqArray) {
				const parsed = parseRequirement(block);
				if (!parsed) continue;

				if (parsed.type === 'course') {
					// If it's a single course
					const childId = parsed.courseId;

					// If we haven't made a node for that course, create a new one
					if (!nodes.find((n) => n.id === childId)) {
						nodes.push({
							id: childId,
							label: childId,
							shape: 'box',
							font: { size: 10, align: 'left' },
							color: yellow
						});
					}
					// Connect child -> parent
					edges.push({ from: childId, to: cId, arrows: 'to' });
				} else if (parsed.type === 'composite') {
					// Create an artificial node
					const compositeId = `composite_${++artificialNodeCount}`;
					nodes.push({
						id: compositeId,
						label: parsed.label, // e.g. "CSC110 or CSC111 or MATH122"
						shape: 'box',
						color: yellow, // yellow
						font: { size: 10, align: 'left' },
						selectable: false
					} as Node);

					// Connect composite node -> parent
					edges.push({ from: compositeId, to: cId, arrows: 'to' });

					for (const subC of parsed.subCourses) {
						edges.push({ from: subC, to: compositeId, arrows: 'to' });
					}
				}
			}
		}

		return { nodes, edges };
	}

	//------------------------------------------------------------
	// 6. onMount: gather upstream/downstream with limited depth
	//------------------------------------------------------------
	onMount(() => {
		// Build the graph
		const { nodes, edges } = buildGraphData();

		// Create the network
		const data = { nodes, edges };
		const options: Options = {
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
			},
			nodes: {
				shape: 'box',
				widthConstraint: {
					maximum: 150 // or any desired px width
				},
				labelHighlightBold: false,
				font: {
					multi: true // allow multi-line (auto-wrap)
				}
			}
		};

		network = new Network(networkContainer, data, options);

		//------------------------------------------------------------
		// 7. Add click handling to get the clicked node's ID
		//------------------------------------------------------------
		network.on('click', (params) => {
			// params.nodes is an array of node IDs
			if (params.nodes && params.nodes.length > 0) {
				const clickedNodeId = params.nodes[0];
				console.log('Clicked node:', clickedNodeId);

				activeCourseId.set(clickedNodeId);

				// If you want to do something with the course ID, you can
				// e.g. open a modal, or call a function, etc.
			}
		});
	});

	$: {
		const updatedCourseId = $graphCourseId;
		$maxDownDepth;
		if (network && updatedCourseId) {
			const data = buildGraphData();
			network.setData(data); // Update the graph data without re-creating the network
		}
	}
</script>

<!-- The container for Vis.js -->
<div class="network-container" bind:this={networkContainer}></div>

<style>
	.network-container {
		width: 100%;
		height: 100%;
		box-sizing: border-box;
	}
</style>
