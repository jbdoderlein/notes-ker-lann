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
        return (value < 0 ? "- " : "") + Math.floor(Math.abs(value) / 100) + "." + (Math.abs(value) % 100) + " €";
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
    getJSONSync("/api/note/alias/?format=json&alias=" + pattern + "&search=user|club", function(aliases) {
        aliases.results.forEach(function(alias) {
            getJSONSync("/api/note/note/" + alias.note + "/?format=json", function (note) {
                fun(note, alias);
                console.log(alias.name);
            });
        });
    });
}
