// Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
// SPDX-License-Identifier: GPL-3.0-or-later


/**
 * Convert balance in cents to a human readable amount
 * @param value the balance, in cents
 * @returns {string}
 */
function pretty_money(value) {
    if (value % 100 === 0)
        return (value < 0 ? "- " : "") + Math.floor(Math.abs(value) / 100) + " €";
    else
        return (value < 0 ? "- " : "") + Math.floor(Math.abs(value) / 100) + "."
            + (Math.abs(value) % 100 < 10 ? "0" : "") + (Math.abs(value) % 100) + " €";
}

/**
 * Add a message on the top of the page.
 * @param msg The message to display
 * @param alert_type The type of the alert. Choices: info, success, warning, danger
 * @param timeout The delay (in millis) after that the message is auto-closed. If negative, then it is ignored.
 */
function addMsg(msg, alert_type, timeout=-1) {
    let msgDiv = $("#messages");
    let html = msgDiv.html();
    let id = Math.floor(10000 * Math.random() + 1);
    html += "<div class=\"alert alert-" + alert_type + " alert-dismissible\">" +
        "<button id=\"close-message-" + id + "\" class=\"close\" data-dismiss=\"alert\" href=\"#\"><span aria-hidden=\"true\">×</span></button>"
        + msg + "</div>\n";
    msgDiv.html(html);

    if (timeout > 0) {
        setTimeout(function () {
            $("#close-message-" + id).click();
        }, timeout);
    }
}

/**
 * add Muliple error message from err_obj
 * @param errs_obj [{error_code:erro_message}]
 * @param timeout The delay (in millis) after that the message is auto-closed. If negative, then it is ignored.
 */
function errMsg(errs_obj, timeout=-1) {
    for (const err_msg of Object.values(errs_obj)) {
              addMsg(err_msg,'danger', timeout);
          }
}

var reloadWithTurbolinks = (function () {
  var scrollPosition;

  function reload () {
    scrollPosition = [window.scrollX, window.scrollY];
    Turbolinks.visit(window.location.toString(), { action: 'replace' })
  }

  document.addEventListener('turbolinks:load', function () {
    if (scrollPosition) {
      window.scrollTo.apply(window, scrollPosition);
      scrollPosition = null
    }
  });

  return reload;
})();

/**
 * Reload the balance of the user on the right top corner
 */
function refreshBalance() {
    $("#user_balance").load("/ #user_balance");
}

/**
 * Query the 20 first matched notes with a given pattern
 * @param pattern The pattern that is queried
 * @param fun For each found note with the matched alias `alias`, fun(note, alias) is called.
 */
function getMatchedNotes(pattern, fun) {
    $.getJSON("/api/note/alias/?format=json&alias=" + pattern + "&search=user|club|activity&ordering=normalized_name", fun);
}

/**
 * Generate a <li> entry with a given id and text
 */
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
    if (!note.display_image) {
        note.display_image = '/media/pic/default.png';
        $.getJSON("/api/note/note/" + note.id + "/?format=json", function(new_note) {
            note.display_image = new_note.display_image.replace("http:", "https:");
            note.name = new_note.name;
            note.balance = new_note.balance;
            note.user = new_note.user;

            displayNote(note, alias, user_note_field, profile_pic_field);
        });
        return;
    }

    let img = note.display_image;
    if (alias !== note.name)
        alias += " (aka. " + note.name + ")";
    if (user_note_field !== null)
        $("#" + user_note_field).text(alias + (note.balance == null ? "" : (" : " + pretty_money(note.balance))));
    if (profile_pic_field != null)
        $("#" + profile_pic_field).attr('src', img);
}

/**
 * Remove a note from the emitters.
 * @param d The note to remove
 * @param note_prefix The prefix of the identifiers of the <li> blocks of the emitters
 * @param notes_display An array containing the infos of the buyers: [alias, note id, note object, quantity]
 * @param note_list_id The div block identifier where the notes of the buyers are displayed
 * @param user_note_field The identifier of the field that display the note of the hovered note (useful in
 *                        consumptions, put null if not used)
 * @param profile_pic_field The identifier of the field that display the profile picture of the hovered note
 *                          (useful in consumptions, put null if not used)
 * @returns an anonymous function to be compatible with jQuery events
 */
function removeNote(d, note_prefix="note", notes_display, note_list_id, user_note_field=null, profile_pic_field=null) {
    return (function() {
        let new_notes_display = [];
        let html = "";
        notes_display.forEach(function (disp) {
            if (disp.quantity > 1 || disp.id !== d.id) {
                disp.quantity -= disp.id === d.id ? 1 : 0;
                new_notes_display.push(disp);
                html += li(note_prefix + "_" + disp.id, disp.name
                    + "<span class=\"badge badge-dark badge-pill\">" + disp.quantity + "</span>");
            }
        });

        notes_display.length = 0;
        new_notes_display.forEach(function(disp) {
            notes_display.push(disp);
        });

        $("#" + note_list_id).html(html);
        notes_display.forEach(function (disp) {
            let obj = $("#" + note_prefix + "_" + disp.id);
            obj.click(removeNote(disp, note_prefix, notes_display, note_list_id, user_note_field, profile_pic_field));
            obj.hover(function() {
                if (disp.note)
                    displayNote(disp.note, disp.name, user_note_field, profile_pic_field);
            });
        });
    });
}

/**
 * Generate an auto-complete field to query a note with its alias
 * @param field_id The identifier of the text field where the alias is typed
 * @param alias_matched_id The div block identifier where the matched aliases are displayed
 * @param note_list_id The div block identifier where the notes of the buyers are displayed
 * @param notes An array containing the note objects of the buyers
 * @param notes_display An array containing the infos of the buyers: [alias, note id, note object, quantity]
 * @param alias_prefix The prefix of the <li> blocks for the matched aliases
 * @param note_prefix The prefix of the <li> blocks for the notes of the buyers
 * @param user_note_field The identifier of the field that display the note of the hovered note (useful in
 *                        consumptions, put null if not used)
 * @param profile_pic_field The identifier of the field that display the profile picture of the hovered note
 *                          (useful in consumptions, put null if not used)
 * @param alias_click Function that is called when an alias is clicked. If this method exists and doesn't return true,
 *                    the associated note is not displayed.
 *                    Useful for a consumption if the item is selected before.
 */
function autoCompleteNote(field_id, alias_matched_id, note_list_id, notes, notes_display, alias_prefix="alias",
                          note_prefix="note", user_note_field=null, profile_pic_field=null, alias_click=null) {
    let field = $("#" + field_id);
    // When the user clicks on the search field, it is immediately cleared
    field.click(function() {
        field.val("");
    });

    let old_pattern = null;

    // When the user type "Enter", the first alias is clicked, and the informations are displayed
    field.keypress(function(event) {
        if (event.originalEvent.charCode === 13) {
            let li_obj = $("#" + alias_matched_id + " li").first();
            displayNote(notes[0], li_obj.text(), user_note_field, profile_pic_field);
            li_obj.trigger("click");
        }
    });

    // When the user type something, the matched aliases are refreshed
    field.keyup(function(e) {
        if (e.originalEvent.charCode === 13)
            return;

        let pattern = field.val();
        // If the pattern is not modified, we don't query the API
        if (pattern === old_pattern || pattern === "")
            return;

        old_pattern = pattern;

        // Clear old matched notes
        notes.length = 0;

        let aliases_matched_obj = $("#" + alias_matched_id);
        let aliases_matched_html = "";

        // Get matched notes with the given pattern
        getMatchedNotes(pattern, function(aliases) {
            // The response arrived too late, we stop the request
            if (pattern !== $("#" + field_id).val())
                return;

            aliases.results.forEach(function (alias) {
                let note = alias.note;
                note = {
                    id: note,
                    name: alias.name,
                    alias: alias,
                    balance: null
                };
                aliases_matched_html += li(alias_prefix + "_" + alias.id, alias.name);
                notes.push(note);
            });

            // Display the list of matched aliases
            aliases_matched_obj.html(aliases_matched_html);

            notes.forEach(function (note) {
                let alias = note.alias;
                let alias_obj = $("#" + alias_prefix + "_" + alias.id);
                // When an alias is hovered, the profile picture and the balance are displayed at the right place
                alias_obj.hover(function () {
                    displayNote(note, alias.name, user_note_field, profile_pic_field);
                });

                // When the user click on an alias, the associated note is added to the emitters
                alias_obj.click(function () {
                    field.val("");
                    old_pattern = "";
                    // If the note is already an emitter, we increase the quantity
                    var disp = null;
                    notes_display.forEach(function (d) {
                        // We compare the note ids
                        if (d.id === note.id) {
                            d.quantity += 1;
                            disp = d;
                        }
                    });
                    // In the other case, we add a new emitter
                    if (disp == null) {
                        disp = {
                            name: alias.name,
                            id: note.id,
                            note: note,
                            quantity: 1
                        };
                        notes_display.push(disp);
                    }

                    // If the function alias_click exists, it is called. If it doesn't return true, then the notes are
                    // note displayed. Useful for a consumption when a button is already clicked
                    if (alias_click && !alias_click())
                        return;

                    let note_list = $("#" + note_list_id);
                    let html = "";
                    notes_display.forEach(function (disp) {
                        html += li(note_prefix + "_" + disp.id, disp.name
                            + "<span class=\"badge badge-dark badge-pill\">" + disp.quantity + "</span>");
                    });

                    // Emitters are displayed
                    note_list.html(html);

                    notes_display.forEach(function (disp) {
                        let line_obj = $("#" + note_prefix + "_" + disp.id);
                        // Hover an emitter display also the profile picture
                        line_obj.hover(function () {
                            displayNote(disp.note, disp.name, user_note_field, profile_pic_field);
                        });

                        // When an emitter is clicked, it is removed
                        line_obj.click(removeNote(disp, note_prefix, notes_display, note_list_id, user_note_field,
                            profile_pic_field));
                    });
                });
            });
        });
    });
}

// When a validate button is clicked, we switch the validation status
function in_validate(id, validated) {

    let invalidity_reason;
    let reason_obj = $("#invalidity_reason_" + id);

    if (validated)
        invalidity_reason = reason_obj.val();
    else
        invalidity_reason = null;

    $("#validate_" + id).html("<i class='fa fa-spinner'></i>");

    // Perform a PATCH request to the API in order to update the transaction
    // If the user has insuffisent rights, an error message will appear
    $.ajax({
        "url": "/api/note/transaction/transaction/" + id + "/",
        type: "PATCH",
        dataType: "json",
        headers: {
            "X-CSRFTOKEN": CSRF_TOKEN
        },
        data: {
            resourcetype: "RecurrentTransaction",
            valid: !validated,
            invalidity_reason: invalidity_reason,
        },
        success: function () {
            // Refresh jQuery objects
            $(".validate").click(in_validate);

            refreshBalance();
            // error if this method doesn't exist. Please define it.
            refreshHistory();
        },
        error: function(err) {
            addMsg("Une erreur est survenue lors de la validation/dévalidation " +
                "de cette transaction : " + err.responseText, "danger");

            refreshBalance();
            // error if this method doesn't exist. Please define it.
            refreshHistory();
        }
    });
}
