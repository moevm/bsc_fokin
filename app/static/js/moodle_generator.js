// MOODLE GENERATOR
// нажатие на кнопку "Генерировать"
$('#gen_btn').click(function(event) {
	event.preventDefault();
	$(this).attr('disabled', 'disabled');
	$('.gen_btn_spinner').show();
	$.ajax({
		type: 'POST',
		url: $('#gen_btn').attr('href'),
		data: JSON.stringify({
			amount: $('#amount_list').val()
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
