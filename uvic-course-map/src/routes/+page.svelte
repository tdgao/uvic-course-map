<script lang="ts">
	import GraphCourseSearch from './../lib/GraphCourseSearch/GraphCourseSearch.svelte';
	import CourseView from './../lib/CourseView/CourseView.svelte';
	import MainContainer from '$lib/MainContainer/MainContainer.svelte';
	import VisTreeGraph from '$lib/VisTreeGraph/VisTreeGraph.svelte';
	import IslandContainer from '$lib/IslandContainer.svelte';
	import HowToUseModal from '$lib/HowToUseModal.svelte';
</script>

<MainContainer>
	<svelte:fragment>
		<div class="absolute left-0 top-0 z-0 h-full w-full">
			<VisTreeGraph />
		</div>

		<div class="m- absolute left-0 top-0 w-full p-4">
			<div class="flex flex-wrap items-start justify-between gap-2">
				<GraphCourseSearch />
				<div class="flex gap-2">
					<!-- Open the modal using ID.showModal() method -->
					<HowToUseModal />
					<a
						class="link font-mono"
						href="https://github.com/tdgao/uvic-course-map"
						target="_blank"
						rel="noopener noreferrer"
					>
						Github
					</a>
				</div>
			</div>
		</div>

		<div class="absolute bottom-0 left-0 p-4">
			<IslandContainer>
				<CourseView />
			</IslandContainer>
		</div>
	</svelte:fragment>
</MainContainer>
