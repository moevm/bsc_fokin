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
	var url = '?' +
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
	$.ajax({
		type: 'GET',
		url: url,
	});
});

// нажатие на кнопки 1, 7 и 30 дней
$('.day_filtration').click(function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		url: '/get_date_interval/',
		data: JSON.stringify({
			day_count: event.target.getAttribute('day_count')
		}),
		contentType: "application/json",
		dataType: "json",
		success: function(data) {
			$('#date_from').val(data.date_from);
			$('#date_to').val(data.date_to);
		}
	});
});

// импорт фильтра
$('#import_btn').click(function(event) {
	event.preventDefault();
	location.href = '/moodle/filtration_set/import/' + $('#filtration_preset').val() + '/?redirect=' + $('#import_btn').attr('redirect');
});

// экспорт фильтра
$('#export_btn').click(function(event) {
	event.preventDefault();
	var url = '/moodle/filtration_set/export/?' +
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
		'tag_ids[]=' + $('#tag_id_list').val().join('&tag_ids[]=') + '&' +
		'title=' + $('#filtration_set_title').val() + '&' +
		'redirect=' + $('#export_btn').attr('redirect')
		$.ajax({
			type: 'GET',
			url: url,
		});
});
