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
function addMsg(msg, alert_type, timeout = -1) {
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
function errMsg(errs_obj, timeout = -1) {
    for (const err_msg of Object.values(errs_obj)) {
        addMsg(err_msg, 'danger', timeout);
    }
}

var reloadWithTurbolinks = (function () {
    var scrollPosition;

    function reload() {
        scrollPosition = [window.scrollX, window.scrollY];
        Turbolinks.visit(window.location.toString(), {action: 'replace'})
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
    $.getJSON("/api/note/alias/?format=json&alias=" + pattern + "&search=user|club&ordering=normalized_name", fun);
}

/**
 * Generate a <li> entry with a given id and text
 */
function li(id, text, extra_css) {
    return "<li class=\"list-group-item py-1 px-2 d-flex justify-content-between align-items-center text-truncate " + extra_css + "\"" +
        " id=\"" + id + "\">" + text + "</li>\n";
}

/**
 * Return style to apply according to the balance of the note and the validation status of the email address
 * @param note The concerned note.
 */
function displayStyle(note) {
    let balance = note.balance;
    var css = "";
    if (balance < -5000)
        css += " text-danger bg-dark";
    else if (balance < -1000)
        css += " text-danger";
    else if (balance < 0)
        css += " text-warning";
    if (!note.email_confirmed)
        css += " text-white bg-primary";
    return css;
}


/**
 * Render note name and picture
 * @param note The note to render
 * @param alias The alias to be displayed
 * @param user_note_field
 * @param profile_pic_field
 */
function displayNote(note, alias, user_note_field = null, profile_pic_field = null) {
    if (!note.display_image) {
        note.display_image = '/media/pic/default.png';
    }
    let img = note.display_image;
    if (alias !== note.name && note.name)
        alias += " (aka. " + note.name + ")";
    if (user_note_field !== null) {
        $("#" + user_note_field).removeAttr('class');
        $("#" + user_note_field).addClass(displayStyle(note));
        $("#" + user_note_field).text(alias + (note.balance == null ? "" : (" :\n" + pretty_money(note.balance))));
        if (profile_pic_field != null) {
            $("#" + profile_pic_field).attr('src', img);
            $("#" + profile_pic_field).click(function () {
                console.log(note);
                if (note.resourcetype === "NoteUser") {
                    document.location.href = "/accounts/user/" + note.user;
                } else if (note.resourcetype === "NoteClub") {
                    document.location.href = "/accounts/club/" + note.club;
                }
            });
        }
    }
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
function removeNote(d, note_prefix = "note", notes_display, note_list_id, user_note_field = null, profile_pic_field = null) {
    return (function () {
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
        new_notes_display.forEach(function (disp) {
            notes_display.push(disp);
        });

        $("#" + note_list_id).html(html);
        notes_display.forEach(function (disp) {
            let obj = $("#" + note_prefix + "_" + disp.id);
            obj.click(removeNote(disp, note_prefix, notes_display, note_list_id, user_note_field, profile_pic_field));
            obj.hover(function () {
                if (disp.note)
                    displayNote(disp.note, disp.name, user_note_field, profile_pic_field);
            });
        });
    });
}

/**
 * Generate an auto-complete field to query a note with its alias
 * @param field_id The identifier of the text field where the alias is typed
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
function autoCompleteNote(field_id, note_list_id, notes, notes_display, alias_prefix = "alias",
                          note_prefix = "note", user_note_field = null, profile_pic_field = null, alias_click = null) {
    let field = $("#" + field_id);

    // Configure tooltip
    field.tooltip({
        html: true,
        placement: 'bottom',
        title: 'Loading...',
        trigger: 'manual',
        container: field.parent()
    });

    // Clear search on click
    field.click(function () {
        field.tooltip('hide');
        field.val("");
    });

    let old_pattern = null;

    // When the user type "Enter", the first alias is clicked
    field.keypress(function (event) {
        if (event.originalEvent.charCode === 13 && notes.length > 0) {
            let li_obj = field.parent().find("ul li").first();
            displayNote(notes[0], li_obj.text(), user_note_field, profile_pic_field);
            li_obj.trigger("click");
        }
    });

    // When the user type something, the matched aliases are refreshed
    field.keyup(function (e) {
        if (e.originalEvent.charCode === 13)
            return;

        let pattern = field.val();

        // If the pattern is not modified, we don't query the API
        if (pattern === old_pattern)
            return;
        old_pattern = pattern;
        notes.length = 0;

        // get matched Alias with note associated
        if (pattern === "") {
            field.tooltip('hide');
            notes.length = 0;
            return;
        }

        $.getJSON("/api/note/consumer/?format=json&alias="
            + pattern
            + "&search=user|club&ordering=normalized_name",
            function (consumers) {
                // The response arrived too late, we stop the request
                if (pattern !== $("#" + field_id).val())
                    return;

                // Build tooltip content
                let aliases_matched_html = '<ul class="list-group list-group-flush">';
                consumers.results.forEach(function (consumer) {
                    let note = consumer.note;
                    note.email_confirmed = consumer.email_confirmed;
                    let extra_css = displayStyle(note);
                    aliases_matched_html += li(alias_prefix + '_' + consumer.id,
                        consumer.name,
                        extra_css);
                    notes.push(note);
                });
                aliases_matched_html += '</ul>';

                // Show tooltip
                field.attr('data-original-title', aliases_matched_html).tooltip('show');

                consumers.results.forEach(function (consumer) {
                    let note = consumer.note;
                    let consumer_obj = $("#" + alias_prefix + "_" + consumer.id);
                    consumer_obj.hover(function () {
                        displayNote(consumer.note, consumer.name, user_note_field, profile_pic_field)
                    });
                    consumer_obj.click(function () {
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
                                name: consumer.name,
                                id: consumer.id,
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
                            html += li(note_prefix + "_" + disp.id,
                                disp.name
                                + "<span class=\"badge badge-dark badge-pill\">"
                                + disp.quantity + "</span>",
                                displayStyle(disp.note));
                        });

                        // Emitters are displayed
                        note_list.html(html);

                        // Update tooltip position
                        field.tooltip('update');

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
                    })
                });

            });// end getJSON alias
    });
}// end function autocomplete

// When a validate button is clicked, we switch the validation status
function de_validate(id, validated) {
    let invalidity_reason = $("#invalidity_reason_" + id).val();
    $("#validate_" + id).html("<strong style=\"font-size: 16pt;\">⟳ ...</strong>");

    // Perform a PATCH request to the API in order to update the transaction
    // If the user has insufficient rights, an error message will appear
    $.ajax({
        "url": "/api/note/transaction/transaction/" + id + "/",
        type: "PATCH",
        dataType: "json",
        headers: {
            "X-CSRFTOKEN": CSRF_TOKEN
        },
        data: {
            "resourcetype": "RecurrentTransaction",
            "valid": !validated,
            "invalidity_reason": invalidity_reason,
        },
        success: function () {
            // Refresh jQuery objects
            $(".validate").click(de_validate);

            refreshBalance();
            // error if this method doesn't exist. Please define it.
            refreshHistory();
        },
        error: function (err) {
            addMsg("Une erreur est survenue lors de la validation/dévalidation " +
                "de cette transaction : " + err.responseText, "danger");

            refreshBalance();
            // error if this method doesn't exist. Please define it.
            refreshHistory();
        }
    });
}
