<script lang="ts">
	import { onMount } from 'svelte';
	import { Network } from 'vis-network';

	let networkContainer: HTMLElement;

	onMount(() => {
		const nodes = [
			{ id: 1, label: 'Node 1' },
			{ id: 2, label: 'Node 2' },
			{ id: 3, label: 'Node 3' },
			{ id: 4, label: 'Node 4' },
			{ id: 5, label: 'Node 5' }
		];

		const edges = [
			{ from: 1, to: 3 },
			{ from: 1, to: 2 },
			{ from: 2, to: 4 },
			{ from: 2, to: 5 }
		];

		const data = { nodes, edges };

		const options = {
			physics: {
				enabled: true,
				barnesHut: {
					gravitationalConstant: -8000,
					springLength: 250
				}
			},
			interaction: {
				dragNodes: true,
				dragView: true,
				zoomView: true
			}
		};

		new Network(networkContainer, data, options);
	});
</script>

<div class="network-container" bind:this={networkContainer}></div>

<style>
	/* Make sure the container has a size */
	.network-container {
		width: 500px;
		height: 500px;
		border: 1px solid #ccc;
		box-sizing: border-box;
	}
</style>
