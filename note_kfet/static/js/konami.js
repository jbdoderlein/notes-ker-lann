/*
 * Konami code support
 */

// Cursor denote the position in konami code
let cursor = 0
const KONAMI_CODE = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]

function afterKonami() {
    // Load Rythm.js
    var rythmScript = document.createElement('script')
    rythmScript.setAttribute('src','https://unpkg.com/rythm.js@2.2.5/rythm.min.js')
    document.head.appendChild(rythmScript)

    rythmScript.addEventListener('load', function() {
        // This media source need to be accessible with a cross-origin header
        const audioElement = new Audio('https://okazari.github.io/Rythm.js/samples/rythmC.mp3')
        audioElement.crossOrigin = 'anonymous'
        audioElement.play();

        const rythm = new Rythm()
        rythm.connectExternalAudioElement(audioElement)
        rythm.addRythm('card', 'pulse', 0, 10)
        rythm.addRythm('nav-link', 'color', 0, 10, {
           from: [0,0,255],
           to:[255,0,255]
        })
        rythm.start()
    });
}

// Register custom event
document.addEventListener('keydown', (e) => {
    cursor = (e.keyCode == KONAMI_CODE[cursor]) ? cursor + 1 : 0;
    if (cursor == KONAMI_CODE.length) {
        afterKonami()
    }
});
