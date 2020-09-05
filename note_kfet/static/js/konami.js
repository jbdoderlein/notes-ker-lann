/*
 * Konami code support
 */

// Cursor denote the position in konami code
let cursor = 0
const KONAMI_CODE = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]

function afterKonami () {
  // Load Rythm.js
  var rythmScript = document.createElement('script')
  rythmScript.setAttribute('src', '//unpkg.com/rythm.js@2.2.5/rythm.min.js')
  document.head.appendChild(rythmScript)

  rythmScript.addEventListener('load', function () {
    // Ker-Lyon audio courtesy of @adalan, ker-lyon.fr
    const audioElement = new Audio('/static/song/konami.ogg')
    audioElement.loop = true
    audioElement.play()

    const rythm = new Rythm()
    rythm.connectExternalAudioElement(audioElement)
    rythm.addRythm('card', 'pulse', 50, 50, {
      min: 1,
      max: 1.1
    })
    rythm.addRythm('d-flex', 'color', 50, 50, {
      from: [64, 64, 64],
      to: [128, 64, 128]
    })
    rythm.addRythm('nav-link', 'jump', 150, 50, {
      min: 0,
      max: 10
    })
    rythm.start()
  })
}

// Register custom event
document.addEventListener('keydown', (e) => {
  cursor = (e.keyCode == KONAMI_CODE[cursor]) ? cursor + 1 : 0
  if (cursor == KONAMI_CODE.length) {
    afterKonami()
  }
})
