// Copyright (C) 2018-2020 by BDE ENS Paris-Saclay
// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Perform a request on an URL and get result
 * @param url The url where the request is performed
 * @param success The function to call with the request
 * @param data The data for the request (optional)
 */
function getJSONSync(url, success, data) {
    $.ajax({
        url: url,
        dataType: 'json',
        data: data,
        async: false,
        success: success
    });
}

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
 * Reload the balance of the user on the right top corner
 */
function refreshBalance() {
    $("#user_balance").load("/ #user_balance");
}

/**
 * Query the 20 first matched notes with a given pattern
 * @param pattern The pattern that is queried
 * @param fun For each found note with the matched alias `alias`, fun(note, alias) is called.
 * This function is synchronous.
 */
function getMatchedNotes(pattern, fun) {
    getJSONSync("/api/note/alias/?format=json&alias=" + pattern + "&search=user|club&ordering=normalized_name", function(aliases) {
        aliases.results.forEach(function(alias) {
            fun(alias, alias.note);
        });
    });
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
            if (disp[3] > 1 || disp[1] !== d[1]) {
                disp[3] -= disp[1] === d[1] ? 1 : 0;
                new_notes_display.push(disp);
                html += li(note_prefix + "_" + disp[1], disp[0]
                    + "<span class=\"badge badge-dark badge-pill\">" + disp[3] + "</span>");
            }
        });

        notes_display.length = 0;
        new_notes_display.forEach(function(disp) {
            notes_display.push(disp);
        });

        $("#" + note_list_id).html(html);
        notes_display.forEach(function (disp) {
            let obj = $("#" + note_prefix + "_" + disp[1]);
            obj.click(removeNote(disp, note_prefix, notes_display, note_list_id, user_note_field, profile_pic_field));
            obj.hover(function() {
                displayNote(disp[2], disp[0], user_note_field, profile_pic_field);
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

    // When the user type something, the matched aliases are refreshed
    field.keyup(function() {
        let pattern = field.val();
        // If the pattern is not modified, or if the field is empty, we don't query the API
        if (pattern === old_pattern || pattern === "")
            return;

        old_pattern = pattern;

        // Clear old matched notes
        notes.length = 0;

        let aliases_matched_obj = $("#" + alias_matched_id);
        let aliases_matched_html = "";
        // Get matched notes with the given pattern
        getMatchedNotes(pattern, function(note, alias) {
            aliases_matched_html += li(alias_prefix + "_" + alias.normalized_name, alias.name);
            note.alias = alias;
            notes.push(note);
        });

        // Display the list of matched aliases
        aliases_matched_obj.html(aliases_matched_html);

        notes.forEach(function (note) {
            let alias = note.alias;
            let alias_obj = $("#" + alias_prefix + "_" + alias.normalized_name);
            // When an alias is hovered, the profile picture and the balance are displayed at the right place
            alias_obj.hover(function() {
                displayNote(note, alias.name, user_note_field, profile_pic_field);
            });

            // When the user click on an alias, the associated note is added to the emitters
            alias_obj.click(function() {
                field.val("");
                // If the note is already an emitter, we increase the quantity
                var disp = null;
                notes_display.forEach(function(d) {
                    // We compare the note ids
                    if (d[1] === note.id) {
                        d[3] += 1;
                        disp = d;
                    }
                });
                // In the other case, we add a new emitter
                if (disp == null)
                    notes_display.push([alias.name, note.id, note, 1]);

                // If the function alias_click exists, it is called. If it doesn't return true, then the notes are
                // note displayed. Useful for a consumption when a button is already clicked
                if (alias_click && !alias_click())
                    return;

                let note_list = $("#" + note_list_id);
                let html = "";
                notes_display.forEach(function(disp) {
                   html += li(note_prefix + "_" + disp[1], disp[0]
                        + "<span class=\"badge badge-dark badge-pill\">" + disp[3] + "</span>");
                });

                // Emitters are displayed
                note_list.html(html);

                notes_display.forEach(function(disp) {
                    let line_obj = $("#" + note_prefix + "_" + disp[1]);
                    // Hover an emitter display also the profile picture
                    line_obj.hover(function() {
                        displayNote(disp[2], disp[0], user_note_field, profile_pic_field);
                    });

                    // When an emitter is clicked, it is removed
                    line_obj.click(removeNote(disp, note_prefix, notes_display, note_list_id, user_note_field, profile_pic_field));
                });
            });
        });
    });
}
