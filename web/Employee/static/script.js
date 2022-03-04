function createUser(role){
    var username = document.getElementById("username").value
    var password = document.getElementById("password").value
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/user/"+username, true);
    xhttp.onload = function() {
        if(xhttp.status == 200){
            document.querySelector('#error_msg').innerHTML = "Username Already Exists."
            document.querySelector('#error').style.visibility = "visible";
            document.getElementById("username").focus()
        }
        else{
            if(validate_password(password) == false){
                document.querySelector('#error_msg').innerHTML = "Password must contain at least one number, one lowercase and one uppercase letter"
                document.querySelector('#error').style.visibility = "visible";
                document.getElementById("password").focus()
                }
            else if(document.getElementById('confirm_password').value != password){
                document.querySelector('#error_msg').innerHTML = "Passwords do not match."
                document.querySelector('#error').style.visibility = "visible";
                document.getElementById("confirm_password").focus()
                }
            else{
                var user = {
                    "username": username,
                    "password": password,
                    "role": "employee"
                    }
                xhttp.open("POST", "/user", true);
                xhttp.setRequestHeader('Content-Type', 'application/json')
                xhttp.onload = function() {
                if(xhttp.status === 200){
                    data = JSON.parse(xhttp.responseText)
                    if(role == 'employee'){
                        document.cookie = username;
                        var href= document.querySelector('#form_register').getAttribute('action');
                        href = "/register"
                        window.location.href = href;
                    }
                    else{
                        register_new_user(data.user_id);
                    }
                    }};
            xhttp.send(JSON.stringify(user));
            }
        }
    }
    xhttp.send();
    return false;
}


function register(){
    var new_user = document.cookie
    var first_name = document.getElementById("first_name").value
    var last_name = document.getElementById("last_name").value
    var email = document.getElementById("email").value
    var phone_no = document.getElementById("phone_no").value
    var dob = document.getElementById("dob").value
    var address = document.getElementById("address").value
    if(validate_phone_no(phone_no) == false){
        document.querySelector('#error_msg').innerHTML = "Phone Number should be of 10 digits."
        document.querySelector('#error').style.visibility = "visible";
        document.getElementById("phone_no").focus()
        return false;
    }
    else{
          var detail = {
            "first_name" : first_name,
            "last_name" : last_name,
            "email" : email,
            "phone_no" : phone_no,
            "dob": dob,
            "address" : address
            }
        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/user/"+new_user, true);
        xhttp.onload = function() {
        if(xhttp.status === 200){
            data = JSON.parse(xhttp.responseText)
            xhttp.open('POST',"/employee/"+data.user_id, true)
            xhttp.setRequestHeader('Content-Type', 'application/json')
            xhttp.onload = function() {
            if(xhttp.status === 200){
                data = JSON.parse(xhttp.responseText)
            }};
            xhttp.send(JSON.stringify(detail));
        }};
        xhttp.send();
        return true;
    }
}


function login(){
    var attempted_user=document.getElementById("user_name").value
    var attempted_pass= document.getElementById("pass").value
    var http = new XMLHttpRequest();
    http.onload = function() {
    if(http.status === 200){
        var data = JSON.parse(http.responseText)
        if(data.key == 1){
            document.cookie = data.token
            var href= document.querySelector('#form').getAttribute('action');
            href = "/logging_in"
            window.location.href = href;
            }
        else{
            document.querySelector('#error_msg').innerHTML = "Username or Password is incorrect"
            document.querySelector('#error').style.visibility = "visible";
        }
    }};
    http.open("GET", '/user/authenticate', true)
    http.setRequestHeader("Authorization", "Basic " + btoa(attempted_user + ":" + attempted_pass));
    http.send();
    return false;
}


function search_result(){
    var tag = document.querySelector('#text').value
    var href= document.querySelector('#form0').getAttribute('action');
    href = "/search/"+tag;
    window.location.href = href;
    return false;
}


function view(user_id){
    var href = document.querySelector('#form1').getAttribute('action');
    href = "/employee_detail/"+user_id;
    window.location.href = href;
    return false;
}

function delete_user(user_id){
    var href = document.querySelector('#form2').getAttribute('action');
    var http = new XMLHttpRequest();
    http.onreadystatechange = function() {
    if(http.status === 200){
        http.onreadystatechange = function() {
        if(http.status === 200){
        }};
        http.open("DELETE", '/user/'+user_id, true)
        http.setRequestHeader('Content-Type', 'application/json')
        http.setRequestHeader('x-access-token', document.cookie );
        http.send();
    }};
    http.open("DELETE", '/employee/'+user_id, true)
    http.setRequestHeader('Content-Type', 'application/json')
    http.setRequestHeader('x-access-token', document.cookie );
    if(confirm("Are you sure you want to delete the employee details along with his credentials?")){
        http.send();
    }
    href = "/employee_master";
    setTimeout(function(){
            window.location.href = href;
            }, 500);
    return false;
}


function edit_details(user_id){
    var fname = document.getElementById('fname').value;
    var lname = document.getElementById('lname').value;
    var email = document.getElementById('email').value;
    var phone_no = document.getElementById('phone_no').value;
    var dob = document.getElementById('dob').value;
    var address = document.getElementById('address').value;
    var detail = {
        "first_name" : fname,
        "last_name" : lname,
        "email" : email,
        "phone_no" : phone_no,
        "dob": dob,
        "address" : address
    }
    var http = new XMLHttpRequest();
    http.onload = function() {
    if(http.status === 200){
        data = JSON.parse(http.responseText)
    }};
    http.open("PATCH", '/employee/'+user_id, true)
    http.setRequestHeader("Content-Type", "application/json");
    http.setRequestHeader('x-access-token', document.cookie );
    http.send(JSON.stringify(detail));
    var href = document.querySelector('#form3').getAttribute('action');
    href = "/employee_detail/"+user_id;
    setTimeout(function(){
            window.location.href = href;
            }, 500);
    return false;
}

 function register_new_user(user_id){
    var first_name = document.getElementById("fname").value
    var last_name = document.getElementById("lname").value
    var email = document.getElementById("email").value
    var phone_no = document.getElementById("phone_no").value
    var dob = document.getElementById("dob").value
    var address = document.getElementById("address").value
    var detail = {
    "first_name" : first_name,
    "last_name" : last_name,
    "email" : email,
    "phone_no" : phone_no,
    "dob": dob,
    "address" : address
    }
    var xhttp = new XMLHttpRequest();
    xhttp.open('POST',"/employee/"+data.user_id, true)
    xhttp.setRequestHeader('Content-Type', 'application/json')
    xhttp.onload = function() {
    if(xhttp.status === 200){
        data = JSON.parse(xhttp.responseText)
    }};
    xhttp.send(JSON.stringify(detail));
    var href = document.querySelector('#form4').getAttribute('action');
    href = "/employee_master";
    setTimeout(function(){
        window.location.href = href;
        }, 500);
    return true;
    }


function closeButton(){
    document.querySelector('#error').style.visibility = "hidden";
}

function validate_password(password){
    var re = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}/;
    return re.test(password);
}

function validate_phone_no(phone_no){
     var no = /^\d{10}$/
     return no.test(phone_no)
}