


$(document).ready(function () {

    // formulaire de l'UI principale quiet-reading
    $('#form_url').validate({
        submitHandler: function (form) {
            $('#quiettitle').find('h2').html('');
            $('#quietcontent').html('');
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
                    $('#quietcontent').append(parsed_html);

                    window.history.pushState(data_server.h, data_server.h, "#"+data_server.h);
                },
                error: function (xhr_obj) {
                    $('#input_url').val('');
                }

            });
            return false;
        }
    });

    function hashchange(h0) {
        var f = $('#form_url');
        if (f) {
            $('#quiettitle').find('h2').html('');
            $('#quietcontent').html('');
            $.ajax({
                type: "POST",
                url: f.attr('action'),
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
                    $('#quietcontent').append(parsed_html);
                },
                error: function (xhr_obj) {
                    $('#input_url').val('');
                }

            });
        }
    }

    if (location.hash.length > 1) {
        hashchange(location.hash.substr(1));
    }

    window.onhashchange = function () {
        hashchange(location.hash.substr(1));
    };

    // formulaire OpenCalais
    $('#form_calais').validate({
        submitHandler: function (form) {
            $('#quiettitle').find('h2').html('');
            $('#entities').html('');
            $.ajax({
                type: "POST",
                url: form.action,
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({target: form.input_url.value}),
                dataType: "json",
                success: function (data_server) {
                    $('#quiettitle').find('h2').html(data_server.title);
                    var entities_html = '';
                    $.each(data_server.entities, function(entity_type, entities) {
                        entities_html += "<tr><td>" + entity_type + "</td><td>" + entities.join(", ") + "</td>\n";
                    });
                    entities_html += "<tr><td>SocialTags</td><td>" + data_server.social_tags.join(", ") + "</td>\n";
                    entities_html += "<tr><td>Topics</td><td>" + data_server.topics.join(", ") + "</td>\n";

                    $('#entities').html(entities_html);

                },
                error: function (xhr_obj) {
                    alert(JSON.stringify(xhr_obj));
                }

            });
            return false;
        }
    });

});
