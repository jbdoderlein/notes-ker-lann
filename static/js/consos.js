// Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Refresh the history table on the consumptions page.
 */
function refreshHistory() {
    $("#history").load("/note/consos/ #history");
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
});

let notes = [];
let notes_display = [];
let buttons = [];

// When the user searches an alias, we update the auto-completion
autoCompleteNote("note", "alias_matched", "note_list", notes, notes_display,
    "alias", "note", "user_note", "profile_pic");

/**
 * Add a transaction from a button.
 * @param dest Where the money goes
 * @param amount The price of the item
 * @param type The type of the transaction (content type id for TemplateTransaction)
 * @param category_id The category identifier
 * @param category_name The category name
 * @param template_id The identifier of the button
 * @param template_name The name of  the button
 */
function addConso(dest, amount, type, category_id, category_name, template_id, template_name) {
    var button = null;
    buttons.forEach(function(b) {
        if (b[5] === template_id) {
            b[1] += 1;
            button = b;
        }
    });
    if (button == null)
        buttons.push([dest, 1, amount, type, category_id, category_name, template_id, template_name]);

    // TODO Only in simple consumption mode
    if (notes.length > 0)
        consumeAll();
}

/**
 * Apply all transactions: all notes in `notes` buy each item in `buttons`
 */
function consumeAll() {
    notes_display.forEach(function(note_display) {
        buttons.forEach(function(button) {
            consume(note_display[1], button[0], button[1] * note_display[3], button[2],
                button[7] + " (" + button[5] + ")", button[3], button[4], button[6]);
       });
    });
}

/**
 * Create a new transaction from a button through the API.
 * @param source The note that paid the item (type: int)
 * @param dest The note that sold the item (type: int)
 * @param quantity The quantity sold (type: int)
 * @param amount The price of one item, in cents (type: int)
 * @param reason The transaction details (type: str)
 * @param type The type of the transaction (content type id for TemplateTransaction)
 * @param category The category id of the button (type: int)
 * @param template The button id (type: int)
 */
function consume(source, dest, quantity, amount, reason, type, category, template) {
    $.post("/api/note/transaction/transaction/",
        {
            "csrfmiddlewaretoken": CSRF_TOKEN,
            "quantity": quantity,
            "amount": amount,
            "reason": reason,
            "valid": true,
            "polymorphic_ctype": type,
            "resourcetype": "TemplateTransaction",
            "source": source,
            "destination": dest,
            "category": category,
            "template": template
        }, function() {
            notes_display.length = 0;
            notes.length = 0;
            buttons.length = 0;
            $("#note_list").html("");
            $("#alias_matched").html("");
            displayNote(null, "");
            refreshHistory();
            refreshBalance();
        });
}
