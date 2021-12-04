$("#btn_edit_profile").on("click", function () {
    var Toast = Swal.mixin({
        toast: false,
        position: 'center',
        showConfirmButton: false,
        timer: 3000
    });

    var username = $("#username").val();
    var firstname = $("#first_name").val();
    var lastname = $("#last_name").val();
    var email = $("#email").val()
    var github =$("#github").val()

    var myreg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
    var myregUname = /^[a-zA-Z0-9_-]+$/;
    var myregName = /^[a-zA-Z0-9]+$/;
    var myregPass = /^[a-zA-Z0-9_*#-]+$/;
    var myregGithub = /github.com/;

    if (github.length>0 && !myregGithub.test(github)){
        Toast.fire({
            target: document.getElementById('profile_info_editor'),
            icon: 'info',
            title: 'please check your github link'
        });
    }

    else if (firstname.length>20){
        Toast.fire({
            target: document.getElementById('profile_info_editor'),
            icon: 'info',
            title: 'The first name should be at most 20 characters long'
        });
    }

    else if (lastname.length>20){
        Toast.fire({
            target: document.getElementById('profile_info_editor'),

            icon: 'info',
            title: 'The last name should be at most 20 characters long'
        });
    }

    else if (username.length>20){
        Toast.fire({
            target: document.getElementById('profile_info_editor'),

            icon: 'info',
            title: 'The displayname should be at most 20 characters long'
        });
    }
    else if (!myreg.test(email)) {
        Toast.fire({
            target: document.getElementById('profile_info_editor'),

            icon: 'info',
            title: 'The email format is not valid!'
        });
    }
    else if (!myregUname.test(username)) {
        Toast.fire({
            target: document.getElementById('profile_info_editor'),
            title: 'The username(displayname) can only be alphanumerical'
        });
    }
    else if (!myregName.test(firstname) || !myregName.test(lastname)){
        Toast.fire({
                        target: document.getElementById('profile_info_editor'),

            title: 'The Name Area can only be alphabetical(A-Z a-z)'
        });
    }


    else {
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        $.ajax({
            url: "/editProfile/",
            type: "POST",
            headers: {'X-CSRFToken': csrftoken},
            data: {
                username: $("#username").val(),
                firstname: $("#first_name").val(),
                email: $("#email").val(),
                lastname:$("#last_name").val(),
                github:$("#github").val()
            },
            success: function (da) {
                var data = eval(da)
                var code = data[0].code
                var msg = data[0].msg
                if (code == "200") {
                    Toast.fire({
                        target: document.getElementById('profile_info_editor'),

                        icon: 'success',
                        title: 'Update Profile Successfully.'
                    });
                    window.location.href = '/editProfile/'
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

