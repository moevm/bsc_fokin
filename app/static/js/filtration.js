// DISCUSSIONS
// слайдер для ответов
$(function() {
	$("#replies_slider-range").slider({
		range: true,
		min: 0,
		max: 100,
		values: [$('#replies_range').attr('replies_from'), $('#replies_range').attr('replies_to')],
		slide: function(event, ui) {
			$("#replies_range").text(ui.values[0] + " - " + ui.values[1]);
		}
	});
	$("#replies_range").text(
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
		values: [$('#progress_range').attr('progress_from'), $('#progress_range').attr('progress_to')],
		slide: function(event, ui) {
			$("#progress_range").text(ui.values[0] + " - " + ui.values[1]);
		}
	});
	$("#progress_range").text(
		$("#progress_slider-range").slider("values", 0) +
		" - " +
		$("#progress_slider-range").slider("values", 1));
	});

// нажатие на кнопку "Поиск"
$('#search_button').click(function(event) {
	event.preventDefault();
	var url = '/moodle/discussions/' + $('#search_button').attr('page') + '/?' +
		'date[from]=' + $('#date_from').val() + '&' +
		'date[to]=' +  $('#date_to').val() + '&' +
		'date[order]=' + $('#date_order').val() + '&' +
		'replies[from]=' + $("#replies_slider-range").slider('values', 0) + '&' +
		'replies[to]=' + $("#replies_slider-range").slider('values', 1) + '&' +
		'replies[order]=' + $('#replies_order').val() + '&' +
		'progress[from]=' + $("#progress_slider-range").slider('values', 0) + '&' +
		'progress[to]=' + $("#progress_slider-range").slider('values', 1) + '&' +
		'progress[order]=' + $('#progress_order').val() + '&' +
		'course_ids[]=' + $('#course_id_list').val().join('&course_ids[]=') + '&' +
		'tag_ids[]=' + $('#tag_id_list').val().join('&tag_ids[]=')
	location.href = url;
	});