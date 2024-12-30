<script lang="ts">
	import GraphCourseSearch from './../lib/GraphCourseSearch/GraphCourseSearch.svelte';
	import CourseView from './../lib/CourseView/CourseView.svelte';
	import MainContainer from '$lib/MainContainer/MainContainer.svelte';
	import VisTreeGraph from '$lib/VisTreeGraph/VisTreeGraph.svelte';
	import IslandContainer from '$lib/IslandContainer.svelte';
</script>

<MainContainer>
	<svelte:fragment>
		<div class="absolute left-0 top-0 z-0 h-full w-full">
			<VisTreeGraph />
		</div>

		<div class="absolute left-0 top-0 m-4">
			<IslandContainer>
				<GraphCourseSearch />
			</IslandContainer>
		</div>

		<div class="absolute bottom-0 left-0 m-4">
			<IslandContainer>
				<CourseView />
			</IslandContainer>
		</div>
	</svelte:fragment>
</MainContainer>
