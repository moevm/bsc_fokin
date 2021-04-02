// обновление обсуждений | курсов
$('.update_btn').click(function(event) {
	event.preventDefault();
	$(this).attr('disabled', 'disabled');
	// спиннер
	$('.update_btn_spinner').show();
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		dataType: "json",
		success: function(data) {
			location.href = data.redirect_url;
		},
		error: function() {
			location.reload();
		}
	});
});
