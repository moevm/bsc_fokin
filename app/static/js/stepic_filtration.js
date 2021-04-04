// слайдер для репутации
$(function() {
	$("#reputation_slider-range").slider({
		range: true,
		min: 0,
		max: 100000,
		values: [$('#reputation_range').attr('reputation_from'), $('#reputation_range').attr('reputation_to')],
		slide: function(event, ui) {
			$("#reputation_range").text(ui.values[0] + " - " + ui.values[1]);
		}
	});
	$("#reputation_range").text(
		$("#reputation_slider-range").slider("values", 0) +
		" - " +
		$("#reputation_slider-range").slider("values", 1));
	});

// нажатие на кнопку "Поиск"
$('#search_btn').click(function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		url: '/filtration/search/?redirect_url=' + $('#search_btn').attr('redirect_url'),
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
			reputation_from: $("#reputation_slider-range").slider('values', 0),
			reputation_to: $("#reputation_slider-range").slider('values', 1),
			reputation_order: $('#reputation_order').val(),
			course_id_list: $('#course_id_list').val(),
			author_id: $('#remove_author').attr('author_id'),
			comment_status: $('#remove_status').attr('comment_status')
		}),
		contentType: "application/json",
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
		url: '/filtration/export_set/?redirect_url=' + $('#export_btn').attr('redirect_url'),
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
			reputation_from: $("#reputation_slider-range").slider('values', 0),
			reputation_to: $("#reputation_slider-range").slider('values', 1),
			reputation_order: $('#reputation_order').val(),
			course_id_list: $('#course_id_list').val(),
			author_id: $('#remove_author').attr('author_id'),
			comment_status: $('#remove_status').attr('comment_status'),
			title: $('#filtration_set_title').val(),
		}),
		contentType: "application/json",
		dataType: "json",
		success: function(data) {
			location.href = data.redirect_url;
		}
	});
});

// ******************** Поле "Статус" ********************
// Выбор статуса
$('.comment_status').click(function(event) {
	event.preventDefault();
	$('#remove_status').attr('comment_status', $(this).attr('comment_status'));
	$('#search_btn').click();
});

// Удаление статуса
$('#remove_status').click(function(event) {
	event.preventDefault();
	$('#remove_status').attr('comment_status', 'all');
	$('#search_btn').click();
});

// Смена статуса
$('.update_comment_status').click(function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		url: $(this).attr('href'),
		data: JSON.stringify({
			comment_status: $(this).attr('comment_status'),
		}),
		contentType: "application/json",
		dataType: "json",
		success: function(data) {
			location.href = data.redirect_url;
		},
		error: function() {
			location.reload();
		}
	});
});
