// DISCUSSIONS
// слайдер для ответов
$(function() {
	$("#replies_slider-range").slider({
		range: true,
		min: 0,
		max: 100,
		values: [0, 10],
		slide: function(event, ui) {
			$("#replies_amount").text(ui.values[0] + " - " + ui.values[1]);
		}
	});
	$("#replies_amount").text(
		$("#replies_slider-range").slider("values", 0) +
		" - " +
		$("#replies_slider-range").slider("values", 1));
	});

// слайдер для прогресса
$(function() {
	$("#progress_slider-range").slider({
		range: true,
		min: 0,
		max: 100,
		values: [50, 80],
		slide: function(event, ui) {
			$("#progress_amount").text(ui.values[0] + " - " + ui.values[1]);
		}
	});
	$("#progress_amount").text(
		$("#progress_slider-range").slider("values", 0) +
		" - " +
		$("#progress_slider-range").slider("values", 1));
	});
