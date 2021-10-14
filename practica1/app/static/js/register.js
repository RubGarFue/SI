$('#form-register-table').submit(function() {
    var username = document.getElementById('username');
    var password = document.getElementById('password');
    var password_confirm = document.getElementById('password_confirm');
    var email = document.getElementById('email');
    var credit_card = document.getElementById('credit_card');
    var direction = document.getElementById('direction');

    return true; // return false to cancel form action
});