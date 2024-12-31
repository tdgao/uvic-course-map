<script lang="ts">
	let modal: HTMLDialogElement;
</script>

<button class="btn btn-xs" on:click={() => modal.showModal()}>How to use?</button>

<dialog id="my_modal_1" class="modal" bind:this={modal}>
	<div class="modal-box">
		<h3 class="text-lg font-bold">Hello!</h3>
		<div class="flex flex-col gap-2 py-4">
			<p>
				This tool shows which courses depend on a specified prerequisite. It helps identify courses
				you cannot take if the prerequisite is skipped.
			</p>

			<br />

			<p><strong>How to Use</strong></p>
			<ul>
				<li>- Enter a course ID in the top left to generate a dependency map.</li>
				<li>- Click any course node to view detailed information.</li>
			</ul>

			<p>
				The courses higher in the graph represent the prerequisites that are required for the course
				connected below.
			</p>
		</div>

		<div class="modal-action">
			<form method="dialog">
				<!-- if there is a button in form, it will close the modal -->
				<button class="btn">Done</button>
			</form>
		</div>
	</div>
</dialog>
