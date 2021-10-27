$("#btn_edit_profile").on("click", function () {
    var Toast = Swal.mixin({
        toast: true,
        position: 'center',
        showConfirmButton: false,
        timer: 3000
    });

    var username = $("#username").val();
    var firstname = $("#firs_name").val();
    var lastname = $("#last_name").val();
    var email = $("#email").val()
    var github =$("#github").val()
    var myreg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
    var myregUname = /^[a-zA-Z0-9]+$/i;

    if (!myreg.test(email)) {
        Toast.fire({
            icon: 'info',
            title: 'The email format is not valid!'
        });
    }
    else if (!myregUname.test(username)) {
        Toast.fire({
            icon: 'info',
            title: 'The username format is not valid!'
        });
    } else {
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        $.ajax({
            url: "/author/editProfile/",
            type: "POST",
            headers: {'X-CSRFToken': csrftoken},
            data: {
                username: $("#username").val(),
                firstname: $("#firstname").val(),
                email: $("#email").val(),
                lastname:$("#lastname").val(),
                github:$("#github").val()
            },
            success: function (da) {
                var data = eval(da)
                var code = data[0].code
                var msg = data[0].msg
                if (code == "200") {
                    Toast.fire({
                        icon: 'success',
                        title: 'Register Successfully.'
                    });
                    window.location.href = '/author/authors/'
                } else {
                    Toast.fire({
                        icon: 'error',
                        title: msg
                    });
                }
            }
        })
    }


})

