$("#btnregister").on("click", function () {
    var Toast = Swal.mixin({
        toast: true,
        position: 'center',
        showConfirmButton: false,
        timer: 3000
    });
    if (!$("#agreeTerms").is(":checked")) {
        Toast.fire({
            icon: 'info',
            title: 'Please agree user term.'
        });
    } else {
        var pwd1 = $("#pwd").val();
        var pwd2 = $("#pwd2").val();
        var email = $("#email").val()
        var myreg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
        var myregUname = /^[a-z0-9]+$/i;
        if (pwd1 != pwd2) {
            Toast.fire({
                icon: 'info',
                title: 'The two passwords do not match.'
            });
        }
        else if (pwd1.length<6) {
            Toast.fire({
                icon: 'info',
                title: 'The password must be at least 6 characters long'
            });
        }
        else if (!myreg.test(email)){
            Toast.fire({
                icon: 'info',
                title: 'The email format is not valid!'
            });
        } else {
            var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
            $.ajax({
                url: "/author/register/",
                type: "POST",
                headers: {'X-CSRFToken': csrftoken},
                data: {
                    user_name: $("#user_name").val(),
                    pwd: $("#pwd").val(),
                    email: $("#email").val(),
                    user_fname:$("#user_fname").val(),
                    user_lname:$("#user_lname").val()
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
                        window.location.href = '/author/login'
                    } else {
                        Toast.fire({
                            icon: 'error',
                            title: msg
                        });
                    }
                }
            })
        }

    }

})

