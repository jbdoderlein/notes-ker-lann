$(document).ready(function () {
    $(".autocomplete").keyup(function(e) {
        let target = $("#" + e.target.id);
        let prefix = target.attr("id");
        let api_url = target.attr("api_url");
        let api_url_suffix = target.attr("api_url_suffix");
        if (!api_url_suffix)
            api_url_suffix = "";
        let name_field = target.attr("name_field");
        if (!name_field)
            name_field = "name";
        let input = target.val();

        $.getJSON(api_url + "?format=json&search=^" + input + api_url_suffix, function(objects) {
            let html = "";

            objects.results.forEach(function (obj) {
                html += li(prefix + "_" + obj.id, obj[name_field]);
            });

            $("#" + prefix + "_list").html(html);

            objects.results.forEach(function (obj) {
                $("#" + prefix + "_" + obj.id).click(function() {
                    target.val(obj[name_field]);
                    $("#" + prefix + "_pk").val(obj.id);
                });

                if (input === obj[name_field])
                    $("#" + prefix + "_pk").val(obj.id);
            });
        });
    });
});