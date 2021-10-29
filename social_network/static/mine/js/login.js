if (top.location != this.location) {

    top.location.replace('/author/login/');
}

$("#btnlogin").on("click", function () {
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    var Toast = Swal.mixin({
        toast: true,
        position: 'center',
        showConfirmButton: false,
        timer: 3000
    });
    var remember = $('#remember').is(':checked');
    $.ajax({
        url: "/author/login/",
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        data: {
            user_name: $("#user_name").val(),
            pwd: $("#pwd").val(),
            remember: remember
        },
        success: function (da) {
            var data = eval(da)
            var code = data[0].code
            var msg = data[0].msg
            if (code == "200") {
                Toast.fire({
                    icon: 'success',
                    title: 'Login Success.'
                })
                window.location.href = '/author/myStream/'
            } else {
                Toast.fire({
                    code: code,
                    icon: 'info',
                    title: msg
                })
            }
        }
    })
})
