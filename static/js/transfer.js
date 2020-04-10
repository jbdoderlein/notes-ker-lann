sources = [];
sources_notes_display = [];
dests = [];
dests_notes_display = [];

function refreshHistory() {
    $("#history").load("/note/transfer/ #history");
}

function reset() {
    sources_notes_display.length = 0;
    sources.length = 0;
    dests_notes_display.length = 0;
    dests.length = 0;
    $("#source_note_list").html("");
    $("#dest_note_list").html("");
    $("#amount").val("");
    $("#reason").val("");
    $("#last_name").val("");
    $("#first_name").val("");
    $("#bank").val("");
    $("#user_note").val("");
    $("#profile_pic").attr("src", "/media/pic/default.png");
    refreshBalance();
    refreshHistory();
}

$(document).ready(function() {
    /**
     * If we are in credit/debit mode, check that only one note is entered.
     * More over, get first name and last name to autocomplete fields.
     */
    function checkUniqueNote() {
        if ($("#type_credit").is(":checked") || $("#type_debit").is(":checked")) {
            let arr = $("#type_credit").is(":checked") ? dests_notes_display : sources_notes_display;

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


    // Ensure we begin in gift mode. Removing these lines may cause problems when reloading.
    let type_gift = $("#type_gift"); // Default mode
    type_gift.removeAttr('checked');
    $("#type_transfer").removeAttr('checked');
    $("#type_credit").removeAttr('checked');
    $("#type_debit").removeAttr('checked');
    $("label[for='type_gift']").attr('class', 'btn btn-sm btn-outline-primary');
    $("label[for='type_transfer']").attr('class', 'btn btn-sm btn-outline-primary');
    $("label[for='type_credit']").attr('class', 'btn btn-sm btn-outline-primary');
    $("label[for='type_debit']").attr('class', 'btn btn-sm btn-outline-primary');

    if (location.hash)
        $("#type_" + location.hash.substr(1)).click();
    else
        type_gift.click();
    location.hash = "";
});

$("#btn_transfer").click(function() {
    if ($("#type_gift").is(':checked')) {
        dests_notes_display.forEach(function (dest) {
            $.post("/api/note/transaction/transaction/",
                {
                    "csrfmiddlewaretoken": CSRF_TOKEN,
                    "quantity": dest.quantity,
                    "amount": 100 * $("#amount").val(),
                    "reason": $("#reason").val(),
                    "valid": true,
                    "polymorphic_ctype": TRANSFER_POLYMORPHIC_CTYPE,
                    "resourcetype": "Transaction",
                    "source": user_id,
                    "destination": dest.note.id,
                    "destination_alias": dest.name
                }).done(function () {
                    addMsg("Le transfert de "
                        + pretty_money(dest.quantity * 100 * $("#amount").val()) + " de votre note "
                        + " vers la note " + dest.name + " a été fait avec succès !", "success");

                    reset();
                }).fail(function () { // do it again but valid = false
                    $.post("/api/note/transaction/transaction/",
                    {
                        "csrfmiddlewaretoken": CSRF_TOKEN,
                        "quantity": dest.quantity,
                        "amount": 100 * $("#amount").val(),
                        "reason": $("#reason").val(),
                        "valid": false,
                        "invalidity_reason": "Solde insuffisant",
                        "polymorphic_ctype": TRANSFER_POLYMORPHIC_CTYPE,
                        "resourcetype": "Transaction",
                        "source": user_id,
                        "destination": dest.note.id,
                        "destination_alias": dest.name
                    }).done(function () {
                        addMsg("Le transfert de "
                            + pretty_money(dest.quantity * 100 * $("#amount").val()) + " de votre note "
                            + " vers la note " + dest.name + " a échoué : Solde insuffisant", "danger");

                        reset();
                    }).fail(function (err) {
                        addMsg("Le transfert de "
                            + pretty_money(dest.quantity * 100 * $("#amount").val()) + " de votre note "
                            + " vers la note " + dest.name + " a échoué : " + err.responseText, "danger");

                    reset();
                });
            });
        });
    }
    else if ($("#type_transfer").is(':checked')) {
        sources_notes_display.forEach(function (source) {
            dests_notes_display.forEach(function (dest) {
                $.post("/api/note/transaction/transaction/",
                    {
                        "csrfmiddlewaretoken": CSRF_TOKEN,
                        "quantity": source.quantity * dest.quantity,
                        "amount": 100 * $("#amount").val(),
                        "reason": $("#reason").val(),
                        "valid": true,
                        "polymorphic_ctype": TRANSFER_POLYMORPHIC_CTYPE,
                        "resourcetype": "Transaction",
                        "source": source.note.id,
                        "source_alias": source.name,
                        "destination": dest.note.id,
                        "destination_alias": dest.name
                    }).done(function () {
                        addMsg("Le transfert de "
                            + pretty_money(source.quantity * dest.quantity * 100 * $("#amount").val()) + " de la note " + source.name
                            + " vers la note " + dest.name + " a été fait avec succès !", "success");

                        reset();
                    }).fail(function (err) { // do it again but valid = false
                        $.post("/api/note/transaction/transaction/",
                        {
                            "csrfmiddlewaretoken": CSRF_TOKEN,
                            "quantity": source.quantity * dest.quantity,
                            "amount": 100 * $("#amount").val(),
                            "reason": $("#reason").val(),
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
                                + pretty_money(source.quantity * dest.quantity * 100 * $("#amount").val()) + " de la note " + source.name
                                + " vers la note " + dest.name + " a échoué : Solde insuffisant", "danger");

                            reset();
                        }).fail(function (err) {
                            addMsg("Le transfert de "
                                + pretty_money(source.quantity * dest.quantity * 100 * $("#amount").val()) + " de la note " + source.name
                                + " vers la note " + dest.name + " a échoué : " + err.responseText, "danger");

                            reset();
                    });
                });
            });
        });
    } else if ($("#type_credit").is(':checked') || $("#type_debit").is(':checked')) {
        let special_note = $("#credit_type").val();
        let user_note;
        let given_reason = $("#reason").val();
        let source, dest, reason;
        if ($("#type_credit").is(':checked')) {
            user_note = dests_notes_display[0].note.id;
            source = special_note;
            dest = user_note;
            reason = "Crédit " + $("#credit_type option:selected").text().toLowerCase();
            if (given_reason.length > 0)
                reason += " (" + given_reason + ")";
        }
        else {
            user_note = sources_notes_display[0].note.id;
            source = user_note;
            dest = special_note;
            reason = "Retrait " + $("#credit_type option:selected").text().toLowerCase();
            if (given_reason.length > 0)
                reason += " (" + given_reason + ")";
        }
        $.post("/api/note/transaction/transaction/",
            {
                "csrfmiddlewaretoken": CSRF_TOKEN,
                "quantity": 1,
                "amount": 100 * $("#amount").val(),
                "reason": reason,
                "valid": true,
                "polymorphic_ctype": SPECIAL_TRANSFER_POLYMORPHIC_CTYPE,
                "resourcetype": "SpecialTransaction",
                "source": source,
                "source_alias": source.name,
                "destination": dest,
                "destination_alias": dest.name,
                "last_name": $("#last_name").val(),
                "first_name": $("#first_name").val(),
                "bank": $("#bank").val()
            }).done(function () {
                addMsg("Le crédit/retrait a bien été effectué !", "success");
                reset();
            }).fail(function (err) {
                addMsg("Le crédit/retrait a échoué : " + err.responseText, "danger");
                reset();
        });
    }
});
