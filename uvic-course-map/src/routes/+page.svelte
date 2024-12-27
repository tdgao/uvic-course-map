<script lang="ts">
	import CourseView from './../lib/CourseView/CourseView.svelte';
	import MainContainer from '$lib/MainContainer/MainContainer.svelte';
	import VisTreeGraph from '$lib/VisTreeGraph/VisTreeGraph.svelte';

	let course_view_id: string = 'seng371';
</script>

<MainContainer>
	<div slot="left">
		{#if course_view_id}
			<CourseView />
		{/if}
	</div>

	<VisTreeGraph slot="right" />
</MainContainer>
