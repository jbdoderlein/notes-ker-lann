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
        target.addClass("is-invalid");
        target.removeClass("is-valid");
        $("#" + prefix + "_reset").removeClass("d-none");

        $.getJSON(api_url + (api_url.includes("?") ? "&" : "?") + "format=json&search=^" + input + api_url_suffix, function(objects) {
            let html = "";

            objects.results.forEach(function (obj) {
                html += li(prefix + "_" + obj.id, obj[name_field]);
            });

            let results_list = $("#" + prefix + "_list");
            results_list.html(html);

            objects.results.forEach(function (obj) {
                $("#" + prefix + "_" + obj.id).click(function() {
                    target.val(obj[name_field]);
                    $("#" + prefix + "_pk").val(obj.id);

                    results_list.html("");
                    target.removeClass("is-invalid");
                    target.addClass("is-valid");

                    if (typeof autocompleted != 'undefined')
                        autocompleted(obj, prefix)
                });

                if (input === obj[name_field])
                    $("#" + prefix + "_pk").val(obj.id);
            });

            if (results_list.children().length === 1 && e.originalEvent.keyCode >= 32) {
                results_list.children().first().trigger("click");
            }
        });
    });

    $(".autocomplete-reset").click(function() {
        let name = $(this).attr("id").replace("_reset", "");
        $("#" + name + "_pk").val("");
        $("#" + name).val("");
        $("#" + name + "_list").html("");
        $(this).addClass("d-none");
    });
});