/**
 * On form submit, create a new alias
 */
function create_alias (e) {
  // Do not submit HTML form
  e.preventDefault()

  // Get data and send to API
  const formData = new FormData(e.target)
  $.post('/api/note/alias/', {
    csrfmiddlewaretoken: formData.get('csrfmiddlewaretoken'),
    name: formData.get('name'),
    note: formData.get('note')
  }).done(function () {
    // Reload table
    $('#alias_table').load(location.pathname + ' #alias_table')
    addMsg('Alias ajouté', 'success')
  }).fail(function (xhr, _textStatus, _error) {
    errMsg(xhr.responseJSON)
  })
}

/**
 * On click of "delete", delete the alias
 * @param Integer button_id Alias id to remove
 */
function delete_button (button_id) {
  $.ajax({
    url: '/api/note/alias/' + button_id + '/',
    method: 'DELETE',
    headers: { 'X-CSRFTOKEN': CSRF_TOKEN }
  }).done(function () {
    addMsg('Alias supprimé', 'success')
    $('#alias_table').load(location.pathname + ' #alias_table')
  }).fail(function (xhr, _textStatus, _error) {
    errMsg(xhr.responseJSON)
  })
}

$(document).ready(function () {
  // Attach event
  document.getElementById('form_alias').addEventListener('submit', create_alias)
})
