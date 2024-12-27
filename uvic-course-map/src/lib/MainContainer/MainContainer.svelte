<div class="container flex gap-1">
	<slot name="left"></slot>

	<div class="h-full w-[1px] border"></div>

	<div class="flex h-full w-full">
		<slot name="right"></slot>
	</div>
</div>

<style>
	.container {
		width: 100vw;
		height: 100vh;
	}
</style>
