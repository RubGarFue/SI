$('#form-login-table').submit(function() {
    var username = $('#username').val();

    var reg = new RegExp("^([a-zA-Z]*)$");
    if (!reg.test(username)) {
        alert('El nombre de usuario solo puede contener caracteres alfabéticos');
        return false;
    }

    if (username.length < 6) {
        alert('El nombre de usuario debe tener como mínimo 6 caracteres');
        return false;
    }

    // store cookie
    document.cookie = username

    return true;
});

$(document).ready(function() {
    if (document.cookie != '') {
        $("#username").val(document.cookie)
    }
})