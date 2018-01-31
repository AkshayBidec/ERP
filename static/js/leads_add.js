$(document).ready(function () {
    $('a.close').click(function (event) {
        event.preventDefault();
        $('.popup').hide("slow");
    });
});