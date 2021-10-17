$('#form-register-table').submit(function() {
    var username = $('#username').val();
    var password = $('#password').val();
    var password2 = $('#password2').val();

    var reg = new RegExp("^([a-zA-Z]*)$");
    if (!reg.test(username)) {
        alert('El nombre de usuario solo puede contener caracteres alfabéticos');
        return false;
    }

    if (username.length < 6) {
        alert('El nombre de usuario debe tener como mínimo 6 caracteres');
        return false;
    }

    if (password.length < 8) {
        alert('La contraseña debe tener como mínimo 8 caracteres');
        return false;
    }

    if (password != password2) {
        alert('Las contraseñas no coinciden');
        return false;
    }

    return true;
});