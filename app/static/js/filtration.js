// нажатие на кнопки 1, 7 и 30 дней
$('.day_filtration').click(function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		url: '/filtration/get_date_interval/',
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

// импорт фильтра
$('#import_btn').click(function(event) {
	event.preventDefault();
	url = '/filtration/import_set/' + $('#filtration_preset').val() + '/?redirect_url=' + $('#import_btn').attr('redirect_url');
	$.ajax({
		type: 'GET',
		url: url,
		dataType: "json",
		success: function(data) {
			location.href = data.redirect_url;
		}
	});
});

// ******************** Поле "Автор" ********************
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

// ******************** Поле "Курсы" ********************
// Выбор курса
$('.course_filtration').click(function(event) {
	event.preventDefault();
	$('#course_id_list').val([$(this).attr('course_id')]);
	$('#search_btn').click();
});

// ******************** Поле "Статус" ********************
// Выбор статуса
$('.post_status').click(function(event) {
	event.preventDefault();
	$('#remove_status').attr('post_status', $(this).attr('post_status'));
	$('#search_btn').click();
});

// Удаление статуса
$('#remove_status').click(function(event) {
	event.preventDefault();
	$('#remove_status').attr('post_status', 'all');
	$('#search_btn').click();
});

// Смена статуса
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
		},
		error: function() {
			location.reload();
		}
	});
});
