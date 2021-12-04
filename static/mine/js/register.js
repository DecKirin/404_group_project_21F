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
        var uname = $("#user_name").val();
        var fname = $("#user_fname").val();
        var lname = $("#user_lname").val();
        var pwd1 = $("#pwd").val();
        var pwd2 = $("#pwd2").val();
        var email = $("#email").val();
        var github = $("#github").val();

        var myreg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
        var myregUname = /^[a-zA-Z0-9_-]+$/;
        var myregName = /^[a-zA-Z0-9]+$/;
        var myregPass = /^[a-zA-Z0-9_*#-]+$/;
        var myregGithub = /github.com/;

        if (pwd1 != pwd2) {
            Toast.fire({
                icon: 'info',
                title: 'The two passwords do not match.'
            });
        }
        else if (github.length>0 && !myregGithub.test(github)){
            Toast.fire({
                icon: 'info',
                title: 'please check your github link'
            });

        }
        else if (pwd1.length<6) {
            Toast.fire({
                icon: 'info',
                title: 'The password must be at least 6 characters long'
            });
        }

        else if (pwd1.length>20){
            Toast.fire({
                icon: 'info',
                title: 'The password must be at most 20 characters long'
            });
        }
        else if (fname.length>20){
            Toast.fire({
                icon: 'info',
                title: 'The first name should be at most 20 characters long'
            });
        }

        else if (lname.length>20){
            Toast.fire({
                icon: 'info',
                title: 'The last name should be at most 20 characters long'
            });
        }

        else if (uname.length>20){
            Toast.fire({
                icon: 'info',
                title: 'The displayname should be at most 20 characters long'
            });
        }
        else if (!myreg.test(email)){
            Toast.fire({
                icon: 'info',
                title: 'The email format is not valid!'
            });
        }
        else if (!myregPass.test(pwd1)){
            Toast.fire({
                icon: 'info',
                title: 'The password should only contain alphabet, number ,underscore(_), dash(-) and star(*)'
            });
        }
        else if (!myregUname.test(uname)) {
            Toast.fire({
                icon: 'info',
                title: 'The username(displayname) can only be alphanumerical'
            });
        }
        else if (!myregName.test(fname) || !myregName.test(lname)){
            Toast.fire({
                icon: 'info',
                title: 'The Name Area can only be alphabetical(A-Z a-z)'
            });
        }

        else{
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
                    user_lname:$("#user_lname").val(),
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

