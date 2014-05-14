$(document).ready(function () {

    $('input').each(function () {

        $(this).on('focus', function () {
            $(this).parent('.css').addClass('labelTop');
            $(this).parent('.css').addClass('active');
        });

        $(this).on('blur', function () {
            if ($(this).val().length == 0) {
                $(this).parent('.css').removeClass('active');
                $(this).parent('.css').removeClass('labelTop');
            } else {
                $(this).parent('.css').removeClass('active');
            }
        });

        if ($(this).val() != '') $(this).parent('.css').addClass('labelTop');

    });
    $("#submit").bind("mouseover", function () {
        if ($("#d5").val() == "") {
            $("#usernameDiv")
                .animate({
                "left": "-10px"
            }, 50)
                .animate({
                "left": "10px"
            }, 50)
                .animate({
                "left": "-5px"
            }, 50)
                .animate({
                "left": "5px"
            }, 50)
                .animate({
                "left": "0"
            }, 50);
        }
        if ($("#d6").val() == "") {
            $("#passwordDiv")
                .animate({
                "left": "10px"
            }, 50)
                .animate({
                "left": "-10px"
            }, 50)
                .animate({
                "left": "5px"
            }, 50)
                .animate({
                "left": "-5px"
            }, 50)
                .animate({
                "left": "0"
            }, 50);
        }
    });

});