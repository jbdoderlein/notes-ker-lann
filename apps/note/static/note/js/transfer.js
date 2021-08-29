var LOCK = false

sources = []
sources_notes_display = []
dests = []
dests_notes_display = []

function refreshHistory () {
  $('#history').load('/note/transfer/ #history')
}

function reset (refresh = true) {
  sources_notes_display.length = 0
  sources.length = 0
  dests_notes_display.length = 0
  dests.length = 0
  $('#source_note_list').html('')
  $('#dest_note_list').html('')
  const source_field = $('#source_note')
  source_field.val('')
  const event = jQuery.Event('keyup')
  event.originalEvent = { charCode: 97 }
  source_field.trigger(event)
  source_field.removeClass('is-invalid')
  source_field.attr('data-original-title', '').tooltip('hide')
  const dest_field = $('#dest_note')
  dest_field.val('')
  dest_field.trigger(event)
  dest_field.removeClass('is-invalid')
  dest_field.attr('data-original-title', '').tooltip('hide')
  const amount_field = $('#amount')
  amount_field.val('')
  amount_field.removeClass('is-invalid')
  $('#amount-required').html('')
  const reason_field = $('#reason')
  reason_field.val('')
  reason_field.removeClass('is-invalid')
  $('#reason-required').html('')
  $('#last_name').val('')
  $('#first_name').val('')
  $('#bank').val('')
  $('#user_note').val('')
  $('#profile_pic').attr('src', '/static/member/img/default_picture.png')
  $('#profile_pic_link').attr('href', '#')
  if (refresh) {
    refreshBalance()
    refreshHistory()
  }

  LOCK = false
}

$(document).ready(function () {
  /**
     * If we are in credit/debit mode, check that only one note is entered.
     * More over, get first name and last name to autocomplete fields.
     */
  function checkUniqueNote () {
    if ($('#type_credit').is(':checked') || $('#type_debit').is(':checked')) {
      const arr = $('#type_credit').is(':checked') ? dests_notes_display : sources_notes_display

      if (arr.length === 0) { return }

      const last = arr[arr.length - 1]
      arr.length = 0
      arr.push(last)

      last.quantity = 1

      if (last.note.club) {
        $('#last_name').val(last.note.name)
        $('#first_name').val(last.note.name)
      }
      else if (!last.note.user) {
        $.getJSON('/api/note/note/' + last.note.id + '/?format=json', function (note) {
          last.note.user = note.user
          $.getJSON('/api/user/' + last.note.user + '/', function (user) {
            $('#last_name').val(user.last_name)
            $('#first_name').val(user.first_name)
          })
        })
      } else {
        $.getJSON('/api/user/' + last.note.user + '/', function (user) {
          $('#last_name').val(user.last_name)
          $('#first_name').val(user.first_name)
        })
      }
    }

    return true
  }

  autoCompleteNote('source_note', 'source_note_list', sources, sources_notes_display,
    'source_alias', 'source_note', 'user_note', 'profile_pic', checkUniqueNote)
  autoCompleteNote('dest_note', 'dest_note_list', dests, dests_notes_display,
    'dest_alias', 'dest_note', 'user_note', 'profile_pic', checkUniqueNote)

  const source = $('#source_note')
  const dest = $('#dest_note')

  $('#type_transfer').change(function () {
    if (LOCK) { return }

    $('#source_me_div').removeClass('d-none')
    $('#source_note').removeClass('is-invalid')
    $('#dest_note').removeClass('is-invalid')
    $('#special_transaction_div').addClass('d-none')
    source.removeClass('d-none')
    $('#source_note_list').removeClass('d-none')
    $('#credit_type').addClass('d-none')
    dest.removeClass('d-none')
    $('#dest_note_list').removeClass('d-none')
    $('#debit_type').addClass('d-none')

    $('#source_note_label').text(select_emitters_label)
    $('#dest_note_label').text(select_receveirs_label)

    location.hash = 'transfer'
  })

  $('#type_credit').change(function () {
    if (LOCK) { return }

    $('#source_me_div').addClass('d-none')
    $('#source_note').removeClass('is-invalid')
    $('#dest_note').removeClass('is-invalid')
    $('#special_transaction_div').removeClass('d-none')
    $('#source_note_list').addClass('d-none')
    $('#dest_note_list').removeClass('d-none')
    source.addClass('d-none')
    source.tooltip('hide')
    $('#credit_type').removeClass('d-none')
    dest.removeClass('d-none')
    dest.val('')
    dest.tooltip('hide')
    $('#debit_type').addClass('d-none')

    $('#source_note_label').text(transfer_type_label)
    $('#dest_note_label').text(select_receveir_label)

    if (dests_notes_display.length > 1) {
      $('#dest_note_list').html('')
      dests_notes_display.length = 0
    }

    location.hash = 'credit'
  })

  $('#type_debit').change(function () {
    if (LOCK) { return }

    $('#source_me_div').addClass('d-none')
    $('#source_note').removeClass('is-invalid')
    $('#dest_note').removeClass('is-invalid')
    $('#special_transaction_div').removeClass('d-none')
    $('#source_note_list').removeClass('d-none')
    $('#dest_note_list').addClass('d-none')
    source.removeClass('d-none')
    source.val('')
    source.tooltip('hide')
    $('#credit_type').addClass('d-none')
    dest.addClass('d-none')
    dest.tooltip('hide')
    $('#debit_type').removeClass('d-none')

    $('#source_note_label').text(select_emitter_label)
    $('#dest_note_label').text(transfer_type_label)

    if (sources_notes_display.length > 1) {
      $('#source_note_list').html('')
      sources_notes_display.length = 0
    }

    location.hash = 'debit'
  })

  $('#credit_type').change(function () {
    const type = $('#credit_type option:selected').text()
    if ($('#type_credit').is(':checked')) { source.val(type) } else { dest.val(type) }
  })

  // Ensure we begin in transfer mode. Removing these lines may cause problems when reloading.
  const type_transfer = $('#type_transfer') // Default mode
  type_transfer.removeAttr('checked')
  $('#type_credit').removeAttr('checked')
  $('#type_debit').removeAttr('checked')

  if (location.hash) { $('#type_' + location.hash.substr(1)).click() } else { type_transfer.click() }

  $('#source_me').click(function () {
    if (LOCK) { return }

    // Shortcut to set the current user as the only emitter
    sources_notes_display.length = 0
    sources.length = 0
    $('#source_note_list').html('')

    const source_note = $('#source_note')
    source_note.focus()
    source_note.val('')
    let event = jQuery.Event('keyup')
    event.originalEvent = { charCode: 97 }
    source_note.trigger(event)
    source_note.val(username)
    event = jQuery.Event('keyup')
    event.originalEvent = { charCode: 97 }
    source_note.trigger(event)
    const fill_note = function () {
      if (sources.length === 0) {
        setTimeout(fill_note, 100)
        return
      }
      event = jQuery.Event('keypress')
      event.originalEvent = { charCode: 13 }
      source_note.trigger(event)

      source_note.tooltip('hide')
      source_note.val('')
      $('#dest_note').focus()
    }
    fill_note()
  })
})

$('#btn_transfer').click(function () {
  if (LOCK) { return }

  LOCK = true

  let error = false

  const amount_field = $('#amount')
  amount_field.removeClass('is-invalid')
  $('#amount-required').html('')

  const reason_field = $('#reason')
  reason_field.removeClass('is-invalid')
  $('#reason-required').html('')

  if (!amount_field.val() || isNaN(amount_field.val()) || amount_field.val() <= 0) {
    amount_field.addClass('is-invalid')
    $('#amount-required').html('<strong>' + gettext('This field is required and must contain a decimal positive number.') + '</strong>')
    error = true
  }

  const amount = Math.round(100 * amount_field.val())
  if (amount > 2147483647) {
    amount_field.addClass('is-invalid')
    $('#amount-required').html('<strong>' + gettext('The amount must stay under 21,474,836.47 €.') + '</strong>')
    error = true
  }

  if (!reason_field.val() && $('#type_transfer').is(':checked')) {
    reason_field.addClass('is-invalid')
    $('#reason-required').html('<strong>' + gettext('This field is required.') + '</strong>')
    error = true
  }

  if (!sources_notes_display.length && !$('#type_credit').is(':checked')) {
    $('#source_note').addClass('is-invalid')
    error = true
  }

  if (!dests_notes_display.length && !$('#type_debit').is(':checked')) {
    $('#dest_note').addClass('is-invalid')
    error = true
  }

  if (error) {
    LOCK = false
    return
  }

  let reason = reason_field.val()

  if ($('#type_transfer').is(':checked')) {
    // We copy the arrays to ensure that transactions are well-processed even if the form is reset
    [...sources_notes_display].forEach(function (source) {
      [...dests_notes_display].forEach(function (dest) {
        if (source.note.id === dest.note.id) {
          addMsg(interpolate(gettext('Warning: the transaction of %s from %s to %s was not made because ' +
              'it is the same source and destination note.'), [pretty_money(amount), source.name, dest.name]), 'warning', 10000)
          LOCK = false
          return
        }

        $.post('/api/note/transaction/transaction/',
          {
            csrfmiddlewaretoken: CSRF_TOKEN,
            quantity: source.quantity * dest.quantity,
            amount: amount,
            reason: reason,
            valid: true,
            polymorphic_ctype: TRANSFER_POLYMORPHIC_CTYPE,
            resourcetype: 'Transaction',
            source: source.note.id,
            source_alias: source.name,
            destination: dest.note.id,
            destination_alias: dest.name
          }).done(function () {
          if (source.note.membership && source.note.membership.date_end < new Date().toISOString()) {
            addMsg(interpolate(gettext('Warning, the emitter note %s is no more a BDE member.'), [source.name]), 'danger', 30000)
          }
          if (dest.note.membership && dest.note.membership.date_end < new Date().toISOString()) {
            addMsg(interpolate(gettext('Warning, the destination note %s is no more a BDE member.'), [dest.name]), 'danger', 30000)
          }

          if (!isNaN(source.note.balance)) {
            const newBalance = source.note.balance - source.quantity * dest.quantity * amount
            if (newBalance <= -5000) {
              addMsg(interpolate(gettext('Warning, the transaction of %s from the note %s to the note %s succeed, but the emitter note %s is very negative.'),
                  [pretty_money(source.quantity * dest.quantity * amount), source.name, dest.name, source.name]), 'danger', 10000)
              reset()
              return
            } else if (newBalance < 0) {
              addMsg(interpolate(gettext('Warning, the transaction of %s from the note %s to the note %s succeed, but the emitter note %s is negative.'),
                  [pretty_money(source.quantity * dest.quantity * amount), source.name, dest.name, source.name]), 'danger', 10000)
              reset()
              return
            }
          }
          addMsg(interpolate(gettext('Transfer of %s from %s to %s succeed!'),
              [pretty_money(source.quantity * dest.quantity * amount), source.name, dest.name]), 'success', 10000)

          reset()
        }).fail(function (err) { // do it again but valid = false
          const errObj = JSON.parse(err.responseText)
          if (errObj.non_field_errors) {
            addMsg(interpolate(gettext('Transfer of %s from %s to %s failed: %s'),
                [pretty_money(source.quantity * dest.quantity * amount), source.name, dest.name, errObj.non_field_errors]), 'danger')
            LOCK = false
            return
          }

          $.post('/api/note/transaction/transaction/',
            {
              csrfmiddlewaretoken: CSRF_TOKEN,
              quantity: source.quantity * dest.quantity,
              amount: amount,
              reason: reason,
              valid: false,
              invalidity_reason: 'Solde insuffisant',
              polymorphic_ctype: TRANSFER_POLYMORPHIC_CTYPE,
              resourcetype: 'Transaction',
              source: source.note.id,
              source_alias: source.name,
              destination: dest.note.id,
              destination_alias: dest.name
            }).done(function () {
            addMsg(interpolate(gettext('Transfer of %s from %s to %s failed: %s'),
                [pretty_money(source.quantity * dest.quantity * amount), source.name, + dest.name, gettext('insufficient funds')]), 'danger', 10000)
            reset()
          }).fail(function (err) {
            const errObj = JSON.parse(err.responseText)
            let error = errObj.detail ? errObj.detail : errObj.non_field_errors
            if (!error) { error = err.responseText }
            addMsg(interpolate(gettext('Transfer of %s from %s to %s failed: %s'),
                [pretty_money(source.quantity * dest.quantity * amount), source.name, + dest.name, error]), 'danger')
            LOCK = false
          })
        })
      })
    })
  } else if ($('#type_credit').is(':checked') || $('#type_debit').is(':checked')) {
    let special_note
    let user_note
    let alias
    const given_reason = reason
    let source_id, dest_id
    if ($('#type_credit').is(':checked')) {
      special_note = $('#credit_type').val()
      user_note = dests_notes_display[0].note
      alias = dests_notes_display[0].name
      source_id = special_note
      dest_id = user_note.id
      reason = 'Crédit ' + $('#credit_type option:selected').text().toLowerCase()
      if (given_reason.length > 0) { reason += ' (' + given_reason + ')' }
    } else {
      special_note = $('#debit_type').val()
      user_note = sources_notes_display[0].note
      alias = sources_notes_display[0].name
      source_id = user_note.id
      dest_id = special_note
      reason = 'Retrait ' + $('#debit_type option:selected').text().toLowerCase()
      if (given_reason.length > 0) { reason += ' (' + given_reason + ')' }
    }
    $.post('/api/note/transaction/transaction/',
      {
        csrfmiddlewaretoken: CSRF_TOKEN,
        quantity: 1,
        amount: amount,
        reason: reason,
        valid: true,
        polymorphic_ctype: SPECIAL_TRANSFER_POLYMORPHIC_CTYPE,
        resourcetype: 'SpecialTransaction',
        source: source_id,
        source_alias: sources_notes_display.length ? alias : null,
        destination: dest_id,
        destination_alias: dests_notes_display.length ? alias : null,
        last_name: $('#last_name').val(),
        first_name: $('#first_name').val(),
        bank: $('#bank').val()
      }).done(function () {
      addMsg(gettext('Credit/debit succeed!'), 'success', 10000)
      if (user_note.membership && user_note.membership.date_end < new Date().toISOString()) { addMsg(gettext('Warning, the emitter note %s is no more a BDE member.'), 'danger', 10000) }
      reset()
    }).fail(function (err) {
      const errObj = JSON.parse(err.responseText)
      let error = errObj.detail ? errObj.detail : errObj.non_field_errors
      if (!error) { error = err.responseText }
      addMsg(interpolate(gettext('Credit/debit failed: %s'), [error]), 'danger', 10000)
      LOCK = false
    })
  }
})
