/**
 * On form submit, create a new friendship
 */
function create_trust (e) {
  // Do not submit HTML form
  e.preventDefault()

  // Get data and send to API
  const formData = new FormData(e.target)
  $.getJSON('/api/note/alias/'+formData.get('trusted') + '/',
    function (trusted_alias) {
      if ((trusted_alias.note == formData.get('trusting')))
      {
         addMsg(gettext("You can't add yourself as a friend"), "danger")
         return
      }
      $.post('/api/note/trust/', {
        csrfmiddlewaretoken: formData.get('csrfmiddlewaretoken'),
        trusting: formData.get('trusting'),
        trusted: trusted_alias.note
      }).done(function () {
        // Reload table
        $('#trust_table').load(location.pathname + ' #trust_table')
        addMsg(gettext('Friendship successfully added'), 'success')
      }).fail(function (xhr, _textStatus, _error) {
        errMsg(xhr.responseJSON)
      })
    }).fail(function (xhr, _textStatus, _error) {
        errMsg(xhr.responseJSON)
    })
}

/**
 * On click of "delete", delete the alias
 * @param button_id:Integer Alias id to remove
 */
function delete_button (button_id) {
  $.ajax({
    url: '/api/note/trust/' + button_id + '/',
    method: 'DELETE',
    headers: { 'X-CSRFTOKEN': CSRF_TOKEN }
  }).done(function () {
    addMsg(gettext('Friendship successfully deleted'), 'success')
    $('#trust_table').load(location.pathname + ' #trust_table')
  }).fail(function (xhr, _textStatus, _error) {
    errMsg(xhr.responseJSON)
  })
}

$(document).ready(function () {
  // Attach event
  document.getElementById('form_trust').addEventListener('submit', create_trust)
})
