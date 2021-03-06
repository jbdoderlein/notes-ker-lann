$(document).ready(function () {
  $('.autocomplete').keyup(function (e) {
    const target = $('#' + e.target.id)
    const prefix = target.attr('id')
    const api_url = target.attr('api_url')
    let api_url_suffix = target.attr('api_url_suffix')
    if (!api_url_suffix) { api_url_suffix = '' }
    let name_field = target.attr('name_field')
    if (!name_field) { name_field = 'name' }
    const input = target.val()
    target.addClass('is-invalid')
    target.removeClass('is-valid')
    $('#' + prefix + '_reset').removeClass('d-none')

    $.getJSON(api_url + (api_url.includes('?') ? '&' : '?') + 'format=json&search=^' + input + api_url_suffix, function (objects) {
      let html = '<ul class="list-group list-group-flush" id="' + prefix + '_list">'

      objects.results.forEach(function (obj) {
        html += li(prefix + '_' + obj.id, obj[name_field])
      })
      html += '</ul>'

      target.tooltip({
        html: true,
        placement: 'bottom',
        trigger: 'manual',
        container: target.parent(),
        fallbackPlacement: 'clockwise'
      })

      target.attr("data-original-title", html).tooltip("show")

      objects.results.forEach(function (obj) {
        $('#' + prefix + '_' + obj.id).click(function () {
          target.val(obj[name_field])
          $('#' + prefix + '_pk').val(obj.id)

          target.tooltip("hide")
          target.removeClass('is-invalid')
          target.addClass('is-valid')

          if (typeof autocompleted !== 'undefined') { autocompleted(obj, prefix) }
        })

        if (input === obj[name_field]) { $('#' + prefix + '_pk').val(obj.id) }
      })

      if (objects.results.length === 1 && e.originalEvent.keyCode >= 32) {
        $('#' + prefix + '_' + objects.results[0].id).trigger('click')
      }
    })
  })

  $('.autocomplete-reset').click(function () {
    const name = $(this).attr('id').replace('_reset', '')
    $('#' + name + '_pk').val('')
    $('#' + name).val('')
    $('#' + name + '_list').html('')
    $(this).addClass('d-none')
  })
})
