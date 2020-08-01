sources = [];
sources_notes_display = [];
dests = [];
dests_notes_display = [];

function refreshHistory() {
    $("#history").load("/note/transfer/ #history");
}

function reset(refresh=true) {
    sources_notes_display.length = 0;
    sources.length = 0;
    dests_notes_display.length = 0;
    dests.length = 0;
    $("#source_note_list").html("");
    $("#dest_note_list").html("");
    let source_field = $("#source_note");
    source_field.val("");
    source_field.trigger("keyup");
    source_field.removeClass('is-invalid');
    let dest_field = $("#dest_note");
    dest_field.val("");
    dest_field.trigger("keyup");
    dest_field.removeClass('is-invalid');
    let amount_field = $("#amount");
    amount_field.val("");
    amount_field.removeClass('is-invalid');
    $("#amount-required").html("");
    let reason_field = $("#reason");
    reason_field.val("");
    reason_field.removeClass('is-invalid');
    $("#reason-required").html("");
    $("#last_name").val("");
    $("#first_name").val("");
    $("#bank").val("");
    $("#user_note").val("");
    $("#profile_pic").attr("src", "/media/pic/default.png");
    if (refresh) {
        refreshBalance();
        refreshHistory();
    }
}

$(document).ready(function() {
    /**
     * If we are in credit/debit mode, check that only one note is entered.
     * More over, get first name and last name to autocomplete fields.
     */
    function checkUniqueNote() {
        if ($("#type_credit").is(":checked") || $("#type_debit").is(":checked")) {
            let arr = $("#type_credit").is(":checked") ? dests_notes_display : sources_notes_display;

            if (arr.length === 0)
                return;

            let last = arr[arr.length - 1];
            arr.length = 0;
            arr.push(last);

            last.quantity = 1;

            if (!last.note.user) {
                $.getJSON("/api/note/note/" + last.note.id + "/?format=json", function(note) {
                    last.note.user = note.user;
                    $.getJSON("/api/user/" + last.note.user + "/", function(user) {
                        $("#last_name").val(user.last_name);
                        $("#first_name").val(user.first_name);
                    });
                });
            }
            else {
                $.getJSON("/api/user/" + last.note.user + "/", function(user) {
                    $("#last_name").val(user.last_name);
                    $("#first_name").val(user.first_name);
                });
            }
        }

        return true;
   }

    autoCompleteNote("source_note", "source_note_list", sources, sources_notes_display,
        "source_alias", "source_note", "user_note", "profile_pic", checkUniqueNote);
    autoCompleteNote("dest_note", "dest_note_list", dests, dests_notes_display,
        "dest_alias", "dest_note", "user_note", "profile_pic", checkUniqueNote);

    let source = $("#source_note");
    let dest = $("#dest_note");

    $("#type_transfer").click(function() {
        $("#source_me_div").removeClass('d-none');
        $("#source_note").removeClass('is-invalid');
        $("#dest_note").removeClass('is-invalid');
        $("#special_transaction_div").addClass('d-none');
        source.attr('disabled', false);
        $("#source_note_list").removeClass('d-none');
        dest.attr('disabled', false);
        $("#dest_note_list").removeClass('d-none');
    });

    $("#type_credit").click(function() {
        $("#source_me_div").addClass('d-none');
        $("#source_note").removeClass('is-invalid');
        $("#dest_note").removeClass('is-invalid');
        $("#special_transaction_div").removeClass('d-none');
        $("#source_note_list").addClass('d-none');
        $("#dest_note_list").removeClass('d-none');
        source.attr('disabled', true);
        source.val($("#credit_type option:selected").text());
        source.tooltip('hide');
        dest.attr('disabled', false);
        dest.val('');
        dest.tooltip('hide');

        if (dests_notes_display.length > 1) {
            $("#dest_note_list").html('');
            dests_notes_display.length = 0;
        }
    });

    $("#type_debit").click(function() {
        $("#source_me_div").addClass('d-none');
        $("#source_note").removeClass('is-invalid');
        $("#dest_note").removeClass('is-invalid');
        $("#special_transaction_div").removeClass('d-none');
        $("#source_note_list").removeClass('d-none');
        $("#dest_note_list").addClass('d-none');
        source.attr('disabled', false);
        source.val('');
        source.tooltip('hide');
        dest.attr('disabled', true);
        dest.val($("#credit_type option:selected").text());
        dest.tooltip('hide');

        if (sources_notes_display.length > 1) {
            $("#source_note_list").html('');
            sources_notes_display.length = 0;
        }
    });

        $("#credit_type").change(function() {
            let type = $("#credit_type option:selected").text();
            if ($("#type_credit").is(":checked"))
                source.val(type);
            else
                dest.val(type);
        });

    // Ensure we begin in transfer mode. Removing these lines may cause problems when reloading.
    let type_transfer = $("#type_transfer"); // Default mode
    type_transfer.removeAttr('checked');
    $("#type_credit").removeAttr('checked');
    $("#type_debit").removeAttr('checked');
    $("label[for='type_transfer']").attr('class', 'btn btn-sm btn-outline-primary');
    $("label[for='type_credit']").attr('class', 'btn btn-sm btn-outline-primary');
    $("label[for='type_debit']").attr('class', 'btn btn-sm btn-outline-primary');

    if (location.hash)
        $("#type_" + location.hash.substr(1)).click();
    else
        type_transfer.click();
    location.hash = "";

    $("#source_me").click(function() {
        // Shortcut to set the current user as the only emitter
        sources_notes_display.length = 0;
        sources.length = 0;
        $("#source_note_list").html("");

        let source_note = $("#source_note");
        source_note.focus();
        source_note.val("");
        let event = jQuery.Event("keyup");
        event.originalEvent = {charCode: 97};
        source_note.trigger(event);
        source_note.val(username);
        event = jQuery.Event("keyup");
        event.originalEvent = {charCode: 97};
        source_note.trigger(event);
        let fill_note = function() {
            if (sources.length === 0) {
                setTimeout(fill_note, 100);
                return;
            }
            event = jQuery.Event("keypress");
            event.originalEvent = {charCode: 13};
            source_note.trigger(event);

            source_note.tooltip('hide');
            source_note.val('');
            $("#dest_note").focus();
        };
        fill_note();
    });
});

$("#btn_transfer").click(function() {
    let error = false;

    let amount_field = $("#amount");
    amount_field.removeClass('is-invalid');
    $("#amount-required").html("");

    let reason_field = $("#reason");
    reason_field.removeClass('is-invalid');
    $("#reason-required").html("");

    if (!amount_field.val() || isNaN(amount_field.val()) || amount_field.val() <= 0) {
        amount_field.addClass('is-invalid');
        $("#amount-required").html("<strong>Ce champ est requis et doit comporter un nombre décimal strictement positif.</strong>");
        error = true;
    }

    if (!reason_field.val()) {
        reason_field.addClass('is-invalid');
        $("#reason-required").html("<strong>Ce champ est requis.</strong>");
        error = true;
    }

    if (error)
        return;

    let amount = 100 * amount_field.val();
    let reason = reason_field.val();

    if ($("#type_transfer").is(':checked')) {
        // We copy the arrays to ensure that transactions are well-processed even if the form is reset
        [...sources_notes_display].forEach(function (source) {
            [...dests_notes_display].forEach(function (dest) {
                $.post("/api/note/transaction/transaction/",
                    {
                        "csrfmiddlewaretoken": CSRF_TOKEN,
                        "quantity": source.quantity * dest.quantity,
                        "amount": amount,
                        "reason": reason,
                        "valid": true,
                        "polymorphic_ctype": TRANSFER_POLYMORPHIC_CTYPE,
                        "resourcetype": "Transaction",
                        "source": source.note.id,
                        "source_alias": source.name,
                        "destination": dest.note.id,
                        "destination_alias": dest.name
                    }).done(function () {
                        if (!isNaN(source.note.balance)) {
                            let newBalance = source.note.balance - source.quantity * dest.quantity * amount;
                            if (newBalance <= -5000) {
                                addMsg("Le transfert de "
                                    + pretty_money(source.quantity * dest.quantity * amount) + " de la note "
                                    + source.name + " vers la note " + dest.name + " a été fait avec succès, " +
                                    "mais la note émettrice passe en négatif sévère.", "danger", 10000);
                                reset();
                                return;
                            }
                            else if (newBalance < 0) {
                                addMsg("Le transfert de "
                                    + pretty_money(source.quantity * dest.quantity * amount) + " de la note "
                                    + source.name + " vers la note " + dest.name + " a été fait avec succès, " +
                                    "mais la note émettrice passe en négatif.", "warning", 10000);
                                reset();
                                return;
                            }
                        }
                        addMsg("Le transfert de "
                            + pretty_money(source.quantity * dest.quantity * amount) + " de la note " + source.name
                            + " vers la note " + dest.name + " a été fait avec succès !", "success", 10000);

                        reset();
                    }).fail(function () { // do it again but valid = false
                        $.post("/api/note/transaction/transaction/",
                        {
                            "csrfmiddlewaretoken": CSRF_TOKEN,
                            "quantity": source.quantity * dest.quantity,
                            "amount": amount,
                            "reason": reason,
                            "valid": false,
                            "invalidity_reason": "Solde insuffisant",
                            "polymorphic_ctype": TRANSFER_POLYMORPHIC_CTYPE,
                            "resourcetype": "Transaction",
                            "source": source.note.id,
                            "source_alias": source.name,
                            "destination": dest.note.id,
                            "destination_alias": dest.name
                        }).done(function () {
                            addMsg("Le transfert de "
                                + pretty_money(source.quantity * dest.quantity * amount) + " de la note " + source.name
                                + " vers la note " + dest.name + " a échoué : Solde insuffisant", "danger", 10000);
                        }).fail(function (err) {
                            addMsg("Le transfert de "
                                + pretty_money(source.quantity * dest.quantity * amount) + " de la note " + source.name
                                + " vers la note " + dest.name + " a échoué : " + err.responseText, "danger");
                    });
                });
            });
        });
    } else if ($("#type_credit").is(':checked') || $("#type_debit").is(':checked')) {
        let special_note = $("#credit_type").val();
        let user_note;
        let given_reason = reason;
        let source_id, dest_id;
        if ($("#type_credit").is(':checked')) {
            if (!dests_notes_display.length) {
                $("#dest_note").addClass('is-invalid');
                return;
            }

            user_note = dests_notes_display[0].note.id;
            source_id = special_note;
            dest_id = user_note;
            reason = "Crédit " + $("#credit_type option:selected").text().toLowerCase();
            if (given_reason.length > 0)
                reason += " (" + given_reason + ")";
        }
        else {
            if (!sources_notes_display.length) {
                $("#source_note").addClass('is-invalid');
                return;
            }

            user_note = sources_notes_display[0].note.id;
            source_id = user_note;
            dest_id = special_note;
            reason = "Retrait " + $("#credit_type option:selected").text().toLowerCase();
            if (given_reason.length > 0)
                reason += " (" + given_reason + ")";
        }
        $.post("/api/note/transaction/transaction/",
            {
                "csrfmiddlewaretoken": CSRF_TOKEN,
                "quantity": 1,
                "amount": amount,
                "reason": reason,
                "valid": true,
                "polymorphic_ctype": SPECIAL_TRANSFER_POLYMORPHIC_CTYPE,
                "resourcetype": "SpecialTransaction",
                "source": source_id,
                "source_alias": sources_notes_display.length ? sources_notes_display[0].name : null,
                "destination": dest_id,
                "destination_alias": dests_notes_display.length ? dests_notes_display[0].name : null,
                "last_name": $("#last_name").val(),
                "first_name": $("#first_name").val(),
                "bank": $("#bank").val()
            }).done(function () {
                addMsg("Le crédit/retrait a bien été effectué !", "success", 10000);
                reset();
            }).fail(function (err) {
                addMsg("Le crédit/retrait a échoué : " + JSON.parse(err.responseText)["detail"],
                    "danger", 10000);
        });
    }
});
