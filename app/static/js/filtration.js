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

// нажатие на кнопки 1, 7 и 30 дней
$('.day_filtration').click(function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		url: '/get_date_interval/',
		data: JSON.stringify({
			day_count: $(this).attr('day_count')
		}),
		contentType: "application/json",
		dataType: "json",
		success: function(data) {
			$('#date_from').val(data.date_from);
			$('#date_to').val(data.date_to);
		}
	});
});

// обновление обсуждений
$('.update_btn').click(function(event) {
	event.preventDefault();
	$(this).attr('disabled', 'disabled');
	$('.update_btn_spinner').show();
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		dataType: "json",
		success: function(data) {
			location.href = data.redirect_url;
		}
	});
});

// нажатие на кнопку "Поиск"
$('#search_btn').click(function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		url: '/moodle/filtration_set/search/?redirect_url=' + $('#search_btn').attr('redirect_url'),
		data: JSON.stringify({
			date_from: $('#date_from').val(),
			date_to: $('#date_to').val(),
			date_order: $('#date_order').val(),
			replies_from: $("#replies_slider-range").slider('values', 0),
			replies_to: $("#replies_slider-range").slider('values', 1),
			replies_order: $('#replies_order').val(),
			progress_from: $("#progress_slider-range").slider('values', 0),
			progress_to: $("#progress_slider-range").slider('values', 1),
			progress_order: $('#progress_order').val(),
			course_id_list: $('#course_id_list').val(),
			tag_id_list: $('#tag_id_list').val(),
			author_id: $('#remove_author').attr('author_id'),
			post_status: $('#remove_status').attr('post_status')
		}),
		contentType: "application/json",
		dataType: "json",
		success: function(data) {
			location.href = data.redirect_url;
		}
	});
});

// импорт фильтра
$('#import_btn').click(function(event) {
	event.preventDefault();
	url = '/moodle/filtration_set/import/' + $('#filtration_preset').val() + '/?redirect_url=' + $('#import_btn').attr('redirect_url');
	$.ajax({
		type: 'GET',
		url: url,
		dataType: "json",
		success: function(data) {
			location.href = data.redirect_url;
		}
	});
});

// экспорт фильтра
$('#export_btn').click(function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		url: '/moodle/filtration_set/export/?redirect_url=' + $('#export_btn').attr('redirect_url'),
		data: JSON.stringify({
			date_from: $('#date_from').val(),
			date_to: $('#date_to').val(),
			date_order: $('#date_order').val(),
			replies_from: $("#replies_slider-range").slider('values', 0),
			replies_to: $("#replies_slider-range").slider('values', 1),
			replies_order: $('#replies_order').val(),
			progress_from: $("#progress_slider-range").slider('values', 0),
			progress_to: $("#progress_slider-range").slider('values', 1),
			progress_order: $('#progress_order').val(),
			course_id_list: $('#course_id_list').val(),
			tag_id_list: $('#tag_id_list').val(),
			author_id: $('#remove_author').attr('author_id'),
			post_status: $('#remove_status').attr('post_status'),
			title: $('#filtration_set_title').val(),
		}),
		contentType: "application/json",
		dataType: "json",
		success: function(data) {
			location.href = data.redirect_url;
		}
	});
});

// нажатие на кнопки фильтра по автору
$('.author_filtration').click(function(event) {
	event.preventDefault();
	$('#remove_author').attr('author_id', $(this).attr('author_id'));
	$('#search_btn').click();
});

// нажатие на кнопку удаления фильтра по автору
$('#remove_author').click(function(event) {
	event.preventDefault();
	$('#remove_author').attr('author_id', 0);
	$('#search_btn').click();
});

// нажатие на кнопки фильтра по курсу
$('.course_filtration').click(function(event) {
	event.preventDefault();
	$('#course_id_list').val([$(this).attr('course_id')]);
	$('#search_btn').click();
});

// нажатие на кнопки фильтра по тегу
$('.tag_filtration').click(function(event) {
	event.preventDefault();
	$('#tag_id_list').val([$(this).attr('tag_id')]);
	$('#search_btn').click();
});

// нажатие на кнопки фильтра по статусу
$('.post_status').click(function(event) {
	event.preventDefault();
	$('#remove_status').attr('post_status', $(this).attr('post_status'));
	$('#search_btn').click();
});

// нажатие на кнопку удаления фильтра по статусу
$('#remove_status').click(function(event) {
	event.preventDefault();
	$('#remove_status').attr('post_status', 'all');
	$('#search_btn').click();
});

// нажатие на кнопки смены статуса
$('.update_post_status').click(function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		url: $(this).attr('href'),
		data: JSON.stringify({
			post_status: $(this).attr('post_status'),
		}),
		contentType: "application/json",
		dataType: "json",
		success: function(data) {
			location.href = data.redirect_url;
		}
	});
});
