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
    $("#source_alias_matched").html("");
    $("#dest_alias_matched").html("");
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
    autoCompleteNote("source_note", "source_alias_matched", "source_note_list", sources, sources_notes_display,
        "source_alias", "source_note", "user_note", "profile_pic");
    autoCompleteNote("dest_note", "dest_alias_matched", "dest_note_list", dests, dests_notes_display,
        "dest_alias", "dest_note", "user_note", "profile_pic", function() {
            if ($("#type_credit").is(":checked") || $("#type_debit").is(":checked")) {
                let last = dests_notes_display[dests_notes_display.length - 1];
                dests_notes_display.length = 0;
                dests_notes_display.push(last);

                last.quantity = 1;

                $.getJSON("/api/user/" + last.note.user + "/", function(user) {
                    $("#last_name").val(user.last_name);
                    $("#first_name").val(user.first_name);
                });
            }

            return true;
       });


    // Ensure we begin in gift mode. Removing these lines may cause problems when reloading.
    $("#type_gift").prop('checked', 'true');
    $("#type_transfer").removeAttr('checked');
    $("#type_credit").removeAttr('checked');
    $("#type_debit").removeAttr('checked');
    $("label[for='type_transfer']").attr('class', 'btn btn-sm btn-outline-primary');
    $("label[for='type_credit']").attr('class', 'btn btn-sm btn-outline-primary');
    $("label[for='type_debit']").attr('class', 'btn btn-sm btn-outline-primary');
});

$("#transfer").click(function() {
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
                    "destination": dest.id
                }, function () {
                    addMsg("Le transfert de "
                        + pretty_money(dest.quantity * 100 * $("#amount").val()) + " de votre note "
                        + " vers la note " + dest.name + " a été fait avec succès !", "success");

                    reset();
                }).fail(function (err) {
                    addMsg("Le transfert de "
                        + pretty_money(dest.quantity * 100 * $("#amount").val()) + " de votre note "
                        + " vers la note " + dest.name + " a échoué : " + err.responseText, "danger");

                reset();
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
                        "source": source.id,
                        "destination": dest.id
                    }, function () {
                        addMsg("Le transfert de "
                            + pretty_money(source.quantity * dest.quantity * 100 * $("#amount").val()) + " de la note " + source.name
                            + " vers la note " + dest.name + " a été fait avec succès !", "success");

                        reset();
                    }).fail(function (err) {
                        addMsg("Le transfert de "
                            + pretty_money(source.quantity * dest.quantity * 100 * $("#amount").val()) + " de la note " + source.name
                            + " vers la note " + dest.name + " a échoué : " + err.responseText, "danger");

                        reset();
                });
            });
        });
    } else if ($("#type_credit").is(':checked') || $("#type_debit").is(':checked')) {
        let special_note = $("#credit_type").val();
        let user_note = dests_notes_display[0].id;
        let given_reason = $("#reason").val();
        let source, dest, reason;
        if ($("#type_credit").is(':checked')) {
            source = special_note;
            dest = user_note;
            reason = "Crédit " + $("#credit_type option:selected").text().toLowerCase();
            if (given_reason.length > 0)
                reason += " (" + given_reason + ")";
        }
        else {
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
                "destination": dest,
                "last_name": $("#last_name").val(),
                "first_name": $("#first_name").val(),
                "bank": $("#bank").val()
            }, function () {
                addMsg("Le crédit/retrait a bien été effectué !", "success");
                reset();
            }).fail(function (err) {
                addMsg("Le crédit/transfert a échoué : " + err.responseText, "danger");
                reset();
        });
    }
});