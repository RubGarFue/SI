getNumUsers();
setInterval(getNumUsers, 3000);

function getNumUsers() {
    $.ajax({
        url: '/numusers',
        type: 'GET',
        success: function(result) {
            $('#num-users').html(result)
        }
    })
}
