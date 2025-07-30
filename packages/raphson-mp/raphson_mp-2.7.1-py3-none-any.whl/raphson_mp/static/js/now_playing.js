import { controlChannel, ControlCommand, ControlTopic, estimateCurrentPosition, RAPHSON_SMALL_URL, RAPHSON_URL, Track } from "./api.js";
import { createIconButton, vars } from "./util.js";

/**
 * @param {import("./types").ControlServerPlaying} data
 * @param {HTMLDivElement} elem
 */
function setProgressWidth(data, elem) {
    const position = estimateCurrentPosition(data);
    const barWidth = position == null || data.duration == null ? 0 : (position / data.duration) * 100;
    elem.style.background = `linear-gradient(90deg, var(--seek-bar-color) ${barWidth}%, transparent 0%)`;
    return
}

/**
 * @param {import("./types").ControlServerPlaying} data
 * @returns {HTMLDivElement}
 */
function createNowPlayingCard(data) {
    const track = data.track ? new Track(data.track) : null;

    const card = document.createElement('div');
    card.classList.add('box');

    const cardHeaderUsername = document.createElement('div');
    cardHeaderUsername.textContent = data.username;

    const cardHeaderClient = document.createElement('div');
    cardHeaderClient.textContent = data.client;
    cardHeaderClient.style.color = 'var(--text-color-secondary)';

    const cardHeader = document.createElement('div');
    cardHeader.classList.add('box-header');
    cardHeader.style.display = 'flex';
    cardHeader.style.justifyContent = 'space-between';
    cardHeader.append(cardHeaderUsername, cardHeaderClient);

    card.append(cardHeader);

    const cardBody = document.createElement('div');
    cardBody.classList.add('nowplaying-body');
    cardBody.style.gap = 'var(--halfgap)';
    card.append(cardBody);

    const coverThumbUrl = track ? track.getAlbum().getCoverURL('low', false) : RAPHSON_SMALL_URL;
    const coverFullUrl = track ? track.getAlbum().getCoverURL('high', false) : RAPHSON_URL;

    const coverImg = document.createElement('a');
    coverImg.classList.add('nowplaying-coverimg')
    coverImg.style.background = `black url("${coverThumbUrl}") no-repeat center / cover`;
    coverImg.href = coverFullUrl;

    const imgInner = document.createElement('div');
    imgInner.style.width = imgInner.style.height = '100%';
    imgInner.style.filter = 'invert(1)';
    imgInner.style.mixBlendMode = 'difference';

    if (data.paused) {
        imgInner.classList.add('icon-pause');
    }

    coverImg.append(imgInner);
    cardBody.append(coverImg);

    const cardBodyRight = document.createElement('div');
    cardBodyRight.classList.add('nowplaying-body-right');
    cardBody.append(cardBodyRight);

    const infoDiv = document.createElement('div');
    cardBodyRight.append(infoDiv);

    if (track && track.title && track.artists.length > 0) {
        const titleDiv = document.createElement('div');
        titleDiv.style.fontSize = '1.3em';
        titleDiv.textContent = track.title;
        const artistDiv = document.createElement('div');
        artistDiv.style.fontSize = '1.1em';
        artistDiv.textContent = track.artists.join(', ');
        infoDiv.append(titleDiv, artistDiv);
    } else {
        let fallbackTitle = '';
        if (track != null) {
            fallbackTitle = track.displayText(false, false);
        } else if (data.virtual_track != null) {
            fallbackTitle = data.virtual_track.title;
        }
        const fallbackDiv = document.createElement('div');
        fallbackDiv.style.fontSize = '1.1em';
        fallbackDiv.textContent = fallbackTitle;
        infoDiv.append(fallbackDiv);
    }

    const playlistDiv = document.createElement('div');
    playlistDiv.classList.add('secondary');
    playlistDiv.textContent = track ? track.playlistName : "";
    infoDiv.append(playlistDiv);

    if (data.control) {
        const controlsDiv = document.createElement("div");
        controlsDiv.classList.add('nowplaying-controls');
        cardBodyRight.append(controlsDiv);

        const prevButton = createIconButton('skip-previous');
        prevButton.addEventListener('click', () => controlChannel.previous(data.player_id));
        controlsDiv.append(prevButton);

        if (data.paused) {
            const playButton = createIconButton('play');
            playButton.addEventListener('click', () => controlChannel.play(data.player_id));
            controlsDiv.append(playButton);
        } else {
            const pauseButton = createIconButton('pause');
            pauseButton.addEventListener('click', () => controlChannel.pause(data.player_id));
            controlsDiv.append(pauseButton);
        }

        const nextButton = createIconButton('skip-next');
        nextButton.addEventListener('click', () => controlChannel.next(data.player_id));
        controlsDiv.append(nextButton);

        if (data.queue != null && data.playlists != null) {
            const syncButton = createIconButton('remote');
            syncButton.addEventListener('click', () => {
                window.location.assign('/player#' + data.player_id);
            });
            controlsDiv.append(syncButton);
        }
    }

    const progressBar = document.createElement('div');
    progressBar.classList.add('nowplaying-progress');
    setProgressWidth(data, progressBar);
    card.append(progressBar);

    return card;
}

/**
 * @param {HTMLElement} container
 */
export function initNowPlayingCards(container, showNothingPlaying) {
    container.classList.add('boxes');

    /** @type {Object.<string, HTMLDivElement>} */
    const cardsElem = {};
    /** @type {Object.<string, import("./types").ControlServerPlaying>} */
    const cardsData = {};

    const nothing = document.createElement('p');
    nothing.textContent = vars.tActivityNothingPlaying;
    let nothingPresent = false;

    function checkEmpty() {
        if (!showNothingPlaying) {
            return;
        }

        if (Object.keys(cardsElem).length == 0) {
            if (!nothingPresent) {
                container.append(nothing);
                nothingPresent = true;
            }
        } else {
            if (nothingPresent) {
                container.removeChild(nothing);
                nothingPresent = false;
            }
        }
    }

    controlChannel.subscribe(ControlTopic.ACTIVITY);

    controlChannel.registerConnectHandler(checkEmpty);

    controlChannel.registerMessageHandler(ControlCommand.SERVER_PLAYING, (/** @type {import("./types").ControlServerPlaying} */ data) => {
        const newCard = createNowPlayingCard(data);

        if (data.player_id in cardsElem) {
            cardsElem[data.player_id].replaceWith(newCard);
        } else {
            container.append(newCard);
        }

        cardsData[data.player_id] = data;
        cardsElem[data.player_id] = newCard;

        checkEmpty();
    });

    /**
     * @param {import("./types").ControlServerPlaying} data
     */
    function removeCard(data) {
        if (data.player_id in cardsElem) {
            cardsElem[data.player_id].remove();
            delete cardsElem[data.player_id];
            delete cardsData[data.player_id];
            checkEmpty();
        }
    }

    controlChannel.registerMessageHandler(ControlCommand.SERVER_PLAYING_STOPPED, removeCard);

    function quickUpdate() {
        for (const data of Object.values(cardsData)) {
            const card = cardsElem[data.player_id];
            const progress = /** @type {HTMLDivElement} */ (card.getElementsByClassName('nowplaying-progress')[0]);
            setProgressWidth(data, progress);
        }
    }

    let quickUpdateTimer = null;
    quickUpdateTimer = setInterval(quickUpdate, 300);
    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState == "visible" && !quickUpdateTimer) {
            quickUpdateTimer = setInterval(quickUpdate, 300);
        } else if (document.visibilityState == 'hidden' && quickUpdateTimer) {
            clearInterval(quickUpdateTimer);
            quickUpdateTimer = null;
        }
    });

    // Periodically check for and remove expired cards
    setInterval(() => {
        for (const data of Object.values(cardsData)) {
            if (Date.now() / 1000 - data.update_time > data.expiry) {
                removeCard(data);
            }
        }
    }, 30_000);
}
