


$(document).ready(function () {

    $('#form_url').validate({
        submitHandler: function (form) {
            $.ajax({
                type: "POST",
                url: form.action,
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({target: form.input_url.value}),
                dataType: "json",
                success: function (data_server) {
                    $('#quiettitle').find('h2').html(data_server.title);
                    var parsed_html = $.parseHTML(data_server.content);
                    $(parsed_html).find("a").attr("href", function (idx, old_val) {
                        return window.location.pathname + "?" + $.param({target: old_val});
                    });
                    $('#quietcontent').html('').append(parsed_html);

                    window.history.pushState(data_server.h, data_server.h, "#"+data_server.h);
                },
                error: function (xhr_obj) {
                    $('#input_url').val('');
                    $('#quiettitle').find('h2').html('');
                    $('#quietcontent').html('');

                }

            });
            return false;
        }
    });

    function hashchange(h0) {
        $.ajax({
            type: "POST",
            url: $('#form_url').attr('action'),
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({h: h0}),
            dataType: "json",
            success: function (data_server) {
                $('#input_url').val(data_server.url);

                $('#quiettitle').find('h2').html(data_server.title);
                var parsed_html = $.parseHTML(data_server.content);
                $(parsed_html).find("a").attr("href", function (idx, old_val) {
                    return window.location.pathname + "?" + $.param({target: old_val});
                });
                $('#quietcontent').html('').append(parsed_html);
            },
            error: function (xhr_obj) {
                $('#input_url').val('');
                $('#quiettitle').find('h2').html('');
                $('#quietcontent').html('');
            }

        });
    }

    if (location.hash.length > 1) {
        hashchange(location.hash.substr(1));
    }

    window.onhashchange = function () {
        hashchange(location.hash.substr(1));
    }

});
