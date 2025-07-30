import { DownloadedTrack, music, Track } from "./api.js";
import { PlaylistCheckboxes } from "./playlistcheckboxes.js";
import { choice } from "./util.js";

/** @type {Array<DownloadedTrack>} */
const downloadedTracks = [];
const playlists = /** @type {HTMLDivElement} */ (document.getElementById('playlists'));
const cover =  /** @type {HTMLDivElement} */ (document.getElementById('cover'));
const audio = /** @type {HTMLAudioElement} */ (document.getElementById('audio'));
const loadingText = /** @type {HTMLDivElement} */ (document.getElementById('loading-text'));
const startText = /** @type {HTMLDivElement} */ (document.getElementById('start-text'));
const revealText = /** @type {HTMLDivElement} */ (document.getElementById('reveal-text'));
const nextText = /** @type {HTMLDivElement} */ (document.getElementById('next-text'));
const details = /** @type {HTMLDivElement} */ (document.getElementById('details'));

/** @type {DownloadedTrack | null} */
let currentTrack = null;
let state = 'start'; // one of: start, playing, reveal

function start() {
    // Choose a random track, and display it blurred. Show start text
    state = 'start';
    console.info('start');

    audio.pause();
    details.textContent = '';

    if (downloadedTracks.length == 0) {
        console.debug('games_guess: cachedTracks still empty')
        setTimeout(start, 500);
        return;
    }

    currentTrack = /** @type {DownloadedTrack} */ (downloadedTracks.shift());

    cover.style.backgroundImage = `url("${currentTrack.imageUrl}")`;
    audio.src = currentTrack.audioUrl;
    cover.classList.add('blurred');
    startText.hidden = false;
    nextText.hidden = true;
    loadingText.hidden = true;
}

function play() {
    // Hide start text, start playing audio, show reveal text
    state = 'playing';
    console.info('playing');
    startText.hidden = true;
    revealText.hidden = false;
    audio.play();
}

function reveal() {
    // Hide reveal text, show next text
    state = 'reveal'
    console.info('reveal');
    cover.classList.remove('blurred');
    revealText.hidden = true;
    nextText.hidden = false;
    if (!currentTrack || !currentTrack.track || !(currentTrack.track instanceof Track)) throw new Error();
    details.textContent = currentTrack.track.displayText();
}

function onClick() {
    if (state == "start") {
        play();
    } else if (state == "playing") {
        reveal();
    } else if (state == "reveal") {
        start();
    }
}

cover.addEventListener('click', onClick);
document.addEventListener('keydown', event => {
    if (event.key == ' ') {
        onClick();
    }
});

const onPlaylistChange = () => {
    downloadedTracks.length = 0;
    fillCachedTracks();
}

const playlistCheckboxes = new PlaylistCheckboxes(playlists, onPlaylistChange);

async function fillCachedTracks() {
    if (downloadedTracks.length > 2) {
        return;
    }

    const playlists = playlistCheckboxes.getActivePlaylists()
    if (playlists.length == 0) {
        return;
    }

    const playlist = music.playlist(choice(playlists));
    const track = await playlist.chooseRandomTrack(true, {});
    const downloadedTrack = await track.download();
    downloadedTracks.push(downloadedTrack);
}

async function init() {
    await music.retrievePlaylists();
    start();
    playlistCheckboxes.createPlaylistCheckboxes();
    fillCachedTracks();
    setInterval(fillCachedTracks, 2000);
}

init();
