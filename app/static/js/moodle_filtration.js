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

// ******************** Поле "Теги" ********************
// Выбор тега
$('.tag_filtration').click(function(event) {
	event.preventDefault();
	$('#tag_id_list').val([$(this).attr('tag_id')]);
	$('#search_btn').click();
});
