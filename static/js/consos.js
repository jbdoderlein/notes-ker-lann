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

let old_pattern = null;
let notes = [];
let notes_display = [];
let buttons = [];

// When the user clicks on the search field, it is immediately cleared
let note_obj = $("#note");
note_obj.click(function() {
    note_obj.val("");
});

function li(id, text) {
    return "<li class=\"list-group-item py-1 d-flex justify-content-between align-items-center\"" +
                " id=\"" + id + "\">" + text + "</li>\n";
}

/**
 * Render note name and picture
 * @param note The note to render
 * @param alias The alias to be displayed
 * @param user_note_field
 * @param profile_pic_field
 */
function displayNote(note, alias, user_note_field=null, profile_pic_field=null) {
    let img = note == null ? null : note.display_image;
    if (img == null)
        img = '/media/pic/default.png';
    if (note !== null && alias !== note.name)
        alias += " (aka. " + note.name + ")";
    if (note !== null && user_note_field !== null)
        $("#" + user_note_field).text(alias + " : " + pretty_money(note.balance));
    if (profile_pic_field != null)
        $("#" + profile_pic_field).attr('src', img);
}

function remove_conso(c, obj, note_prefix="note") {
    return (function() {
        let new_notes_display = [];
        let html = "";
        notes_display.forEach(function (disp) {
            if (disp[3] > 1 || disp[1] !== c[1]) {
                disp[3] -= disp[1] === c[1] ? 1 : 0;
                new_notes_display = new_notes_display.concat([disp]);
                html += li(note_prefix + "_" + disp[1], disp[0]
                    + "<span class=\"badge badge-dark badge-pill\">" + disp[3] + "</span>");
            }
        });
        $("#note_list").html(html);
        notes_display.forEach(function (disp) {
            obj = $("#" + note_prefix + "_" + disp[1]);
            obj.click(remove_conso(disp, obj, note_prefix));
            obj.hover(function() {
                displayNote(disp[2], disp[0]);
            });
        });
        notes_display = new_notes_display;
    });
}


function autoCompleteNote(field_id, alias_matched_id, alias_prefix="alias", note_prefix="note",
                          user_note_field=null, profile_pic_field=null) {
    let field = $("#" + field_id);
    field.keyup(function() {
        let pattern = field.val();
        // If the pattern is not modified, or if the field is empty, we don't query the API
        if (pattern === old_pattern || pattern === "")
            return;

        old_pattern = pattern;

        notes = [];
        let aliases_matched_obj = $("#" + alias_matched_id);
        let aliases_matched_html = "";
        getMatchedNotes(pattern, function(note, alias) {
            aliases_matched_html += li("alias_" + alias.normalized_name, alias.name);
            note.alias = alias;
            notes = notes.concat([note]);
        });

        aliases_matched_obj.html(aliases_matched_html);

        notes.forEach(function (note) {
            let alias = note.alias;
            let alias_obj = $("#" + alias_prefix + "_" + alias.normalized_name);
            alias_obj.hover(function() {
                displayNote(note, alias.name, user_note_field, profile_pic_field);
            });

            alias_obj.click(function() {
                field.val("");
                var disp = null;
                notes_display.forEach(function(d) {
                    if (d[1] === note.id) {
                        d[3] += 1;
                        disp = d;
                    }
                });
                if (disp == null)
                    notes_display = notes_display.concat([[alias.name, note.id, note, 1]]);
                let note_list = $("#note_list");
                let html = "";
                notes_display.forEach(function(disp) {
                   html += li("note_" + disp[1], disp[0]
                        + "<span class=\"badge badge-dark badge-pill\">" + disp[3] + "</span>");
                });

                note_list.html(html);

                notes_display.forEach(function(disp) {
                    let line_obj = $("#" + note_prefix + "_" + disp[1]);
                    line_obj.hover(function() {
                        displayNote(disp[2], disp[0], user_note_field, profile_pic_field);
                    });

                    line_obj.click(remove_conso(disp, note_prefix));
                });
            });
        });
    });
}


// When the user searches an alias, we update the auto-completion
autoCompleteNote("note", "alias_matched", "alias", "note",
    "user_note", "profile_pic");

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
        buttons = buttons.concat([[dest, 1, amount, type, category_id, category_name, template_id, template_name]]);

    // TODO Only in simple consumption mode
    if (notes.length > 0)
        consumeAll();
}

/**
 * Apply all transactions: all notes in `notes` buy each item in `buttons`
 */
function consumeAll() {
    notes.forEach(function(note) {
        buttons.forEach(function(button) {
            consume(note.id, button[0], button[1], button[2], button[7] + " (" + button[5] + ")",
                button[3], button[4], button[6]);
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
            notes_display = [];
            notes = [];
            buttons = [];
            old_pattern = null;
            $("#note_list").html("");
            $("#alias_matched").html("");
            displayNote(null, "");
            refreshHistory();
            refreshBalance();
        });
}
