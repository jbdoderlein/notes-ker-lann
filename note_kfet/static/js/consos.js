// Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
// SPDX-License-Identifier: GPL-3.0-or-later

// When a transaction is performed, lock the interface to prevent spam clicks.
var LOCK = false;

/**
 * Refresh the history table on the consumptions page.
 */
function refreshHistory() {
    $("#history").load("/note/consos/ #history");
    $("#most_used").load("/note/consos/ #most_used");
}

$(document).ready(function() {
    // If hash of a category in the URL, then select this category
    // else select the first one
    if (location.hash) {
        $("a[href='" + location.hash + "']").tab("show");
    } else {
        $("a[data-toggle='tab']").first().tab("show");
    }

    // When selecting a category, change URL
    $(document.body).on("click", "a[data-toggle='tab']", function() {
        location.hash = this.getAttribute("href");
    });

    // Switching in double consumptions mode should update the layout
    $("#double_conso").click(function() {
        $("#consos_list_div").removeClass('d-none');
        $("#user_select_div").attr('class', 'col-xl-4');
        $("#infos_div").attr('class', 'col-sm-5 col-xl-6');

        let note_list_obj = $("#note_list");
        if (buttons.length > 0 && note_list_obj.text().length > 0) {
            $("#consos_list").html(note_list_obj.html());
            note_list_obj.html("");

            buttons.forEach(function(button) {
                $("#conso_button_" + button.id).click(function() {
                    if (LOCK)
                        return;
                    removeNote(button, "conso_button", buttons,"consos_list")();
                });
            });
        }
    });

    $("#single_conso").click(function() {
        $("#consos_list_div").addClass('d-none');
        $("#user_select_div").attr('class', 'col-xl-7');
        $("#infos_div").attr('class', 'col-sm-5 col-md-4');

        let consos_list_obj = $("#consos_list");
        if (buttons.length > 0) {
            if (notes_display.length === 0 && consos_list_obj.text().length > 0) {
                $("#note_list").html(consos_list_obj.html());
                consos_list_obj.html("");
                buttons.forEach(function(button) {
                    $("#conso_button_" + button.id).click(function() {
                        if (LOCK)
                            return;
                        removeNote(button, "conso_button", buttons,"note_list")();
                    });
                });
            }
            else {
                buttons.length = 0;
                consos_list_obj.html("");
            }
        }
    });

    // Ensure we begin in single consumption. Fix issue with TurboLinks and BootstrapJS
    $("label[for='double_conso']").removeClass('active');

    $("#consume_all").click(consumeAll);
});

notes = [];
notes_display = [];
buttons = [];

// When the user searches an alias, we update the auto-completion
autoCompleteNote("note", "note_list", notes, notes_display,
    "alias", "note", "user_note", "profile_pic", function() {
        if (buttons.length > 0 && $("#single_conso").is(":checked")) {
            consumeAll();
            return false;
        }
        return true;
    });

/**
 * Add a transaction from a button.
 * @param dest Where the money goes
 * @param amount The price of the item
 * @param type The type of the transaction (content type id for RecurrentTransaction)
 * @param category_id The category identifier
 * @param category_name The category name
 * @param template_id The identifier of the button
 * @param template_name The name of  the button
 */
function addConso(dest, amount, type, category_id, category_name, template_id, template_name) {
    var button = null;
    buttons.forEach(function(b) {
        if (b.id === template_id) {
            b.quantity += 1;
            button = b;
        }
    });
    if (button == null) {
        button = {
            id: template_id,
            name: template_name,
            dest: dest,
            quantity: 1,
            amount: amount,
            type: type,
            category_id: category_id,
            category_name: category_name
        };
        buttons.push(button);
    }

    let dc_obj = $("#double_conso");
    if (dc_obj.is(":checked") || notes_display.length === 0) {
        let list = dc_obj.is(":checked") ? "consos_list" : "note_list";
        let html = "";
        buttons.forEach(function(button) {
            html += li("conso_button_" + button.id, button.name
                + "<span class=\"badge badge-dark badge-pill\">" + button.quantity + "</span>");
        });

        $("#" + list).html(html);

        buttons.forEach(function(button) {
            $("#conso_button_" + button.id).click(function() {
                if (LOCK)
                    return;
                removeNote(button, "conso_button", buttons, list)();
            });
        });
    }
    else
        consumeAll();
}

/**
 * Reset the page as its initial state.
 */
function reset() {
    notes_display.length = 0;
    notes.length = 0;
    buttons.length = 0;
    $("#note_list").html("");
    $("#consos_list").html("");
    $("#note").val("");
    $("#note").attr("data-original-title", "").tooltip("hide");
    $("#profile_pic").attr("src", "/static/member/img/default_picture.png");
    $("#profile_pic_link").attr("href", "#");
    refreshHistory();
    refreshBalance();
    LOCK = false;
}


/**
 * Apply all transactions: all notes in `notes` buy each item in `buttons`
 */
function consumeAll() {
    if (LOCK)
        return;

    LOCK = true;

    let error = false;

    if (notes_display.length === 0) {
        $("#note").addClass('is-invalid');
        $("#note_list").html(li("", "<strong>Ajoutez des émetteurs.</strong>", "text-danger"));
        error = true;
    }

    if (buttons.length === 0) {
        $("#consos_list").html(li("", "<strong>Ajoutez des consommations.</strong>", "text-danger"));
        error = true;
    }

    if (error) {
        LOCK = false;
        return;
    }

    notes_display.forEach(function(note_display) {
        buttons.forEach(function(button) {
            consume(note_display.note, note_display.name, button.dest, button.quantity * note_display.quantity, button.amount,
                button.name + " (" + button.category_name + ")", button.type, button.category_id, button.id);
       });
    });
}

/**
 * Create a new transaction from a button through the API.
 * @param source The note that paid the item (type: note)
 * @param source_alias The alias used for the source (type: str)
 * @param dest The note that sold the item (type: int)
 * @param quantity The quantity sold (type: int)
 * @param amount The price of one item, in cents (type: int)
 * @param reason The transaction details (type: str)
 * @param type The type of the transaction (content type id for RecurrentTransaction)
 * @param category The category id of the button (type: int)
 * @param template The button id (type: int)
 */
function consume(source, source_alias, dest, quantity, amount, reason, type, category, template) {
    $.post("/api/note/transaction/transaction/",
        {
            "csrfmiddlewaretoken": CSRF_TOKEN,
            "quantity": quantity,
            "amount": amount,
            "reason": reason,
            "valid": true,
            "polymorphic_ctype": type,
            "resourcetype": "RecurrentTransaction",
            "source": source.id,
            "source_alias": source_alias,
            "destination": dest,
            "template": template
        })
        .done(function () {
            if (!isNaN(source.balance)) {
                let newBalance = source.balance - quantity * amount;
                if (newBalance <= -5000)
                    addMsg("Attention, La transaction depuis la note " + source_alias + " a été réalisée avec " +
                        "succès, mais la note émettrice " + source_alias + " est en négatif sévère.",
                        "danger", 30000);
                else if (newBalance < 0)
                    addMsg("Attention, La transaction depuis la note " + source_alias + " a été réalisée avec " +
                        "succès, mais la note émettrice " + source_alias + " est en négatif.",
                        "warning", 30000);
                if (source.membership && source.membership.date_end < new Date().toISOString())
                    addMsg("Attention : la note émettrice " + source.name + " n'est plus adhérente.",
                        "danger", 30000);
            }
            reset();
        }).fail(function (e) {
        $.post("/api/note/transaction/transaction/",
            {
                "csrfmiddlewaretoken": CSRF_TOKEN,
                "quantity": quantity,
                "amount": amount,
                "reason": reason,
                "valid": false,
                "invalidity_reason": "Solde insuffisant",
                "polymorphic_ctype": type,
                "resourcetype": "RecurrentTransaction",
                "source": source,
                "source_alias": source_alias,
                "destination": dest,
                "template": template
            }).done(function() {
                reset();
                addMsg("La transaction n'a pas pu être validée pour cause de solde insuffisant.", "danger", 10000);
            }).fail(function () {
                reset();
                errMsg(e.responseJSON);
            });
    });
}
