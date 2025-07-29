import { eventBus, MusicEvent } from "./event.js";
import { vars, createIconButton, replaceIconButton, durationToString } from "../util.js";
import { windows } from "./window.js";
import { music, Playlist, Track } from "../api.js";
import { trackDisplayHtml } from "./track.js";
import { editor } from "./editor.js";
import { settings } from "./settings.js";
import { queue } from "./queue.js";
import { createPlaylistDropdown } from "./player.js";

const BROWSE_CONTENT = /** @type {HTMLDivElement} */ (document.getElementById('browse-content'));

class AbstractBrowse {
    /** @type {string} */
    title;
    /**
     * @param {string} title
     */
    constructor(title) {
        this.title = title;
    }

    async render(container) {
        throw new Error("abstract method");
    }
}

export class HomeBrowse extends AbstractBrowse {
    constructor() {
        super(vars.tBrowseNothing);
    }

    async render() {
        const playlistSelect = createPlaylistDropdown(false);
        const noPlaylistOption = document.createElement('option');
        noPlaylistOption.textContent = 'Playlist';
        playlistSelect.value = "";
        playlistSelect.prepend(noPlaylistOption);
        playlistSelect.addEventListener('input', () => browse.browse(new PlaylistBrowse(playlistSelect.value)));

        const recentlyAddedButton = document.createElement('button');
        recentlyAddedButton.textContent = vars.tBrowseRecentlyAdded;
        recentlyAddedButton.addEventListener("click", () => browse.browse(new RecentlyAddedBrowse()));

        const recentlyReleasedButton = document.createElement('button');
        recentlyReleasedButton.textContent = vars.tBrowseRecentlyReleased;
        recentlyReleasedButton.addEventListener("click", () => browse.browse(new RecentlyReleasedBrowse()));

        const randomButton = document.createElement('button');
        randomButton.textContent = vars.tBrowseRandom;
        randomButton.addEventListener("click", () => browse.browse(new RandomBrowse()));

        const missingMetadataButton = document.createElement('button');
        missingMetadataButton.textContent = vars.tBrowseMissingMetadata;
        missingMetadataButton.addEventListener("click", () => browse.browse(new MissingMetadataBrowse()));

        BROWSE_CONTENT.replaceChildren(playlistSelect, recentlyAddedButton, recentlyReleasedButton, randomButton,missingMetadataButton);
    }
}

export class TracksBrowse extends AbstractBrowse {
    filters;
    /**
     * @param {string} title
     * @param {import("../types.js").FilterJson} filters
     */
    constructor(title, filters) {
        super(title);
        this.filters = filters;
    }

    async render() {
        const table = document.createElement('table');
        const tbody = document.createElement('tbody');
        table.append(tbody);
        const tracks = await music.filter(this.filters);
        populateTrackTable(tbody, tracks);
        BROWSE_CONTENT.replaceChildren(table);
    }
}

export class ArtistBrowse extends TracksBrowse {
    /**
     * @param {string} artistName
     */
    constructor(artistName) {
        super(vars.tBrowseArtist + artistName, { artist: artistName, order: 'title' });
    }
}

export class AlbumBrowse extends TracksBrowse {
    /**
     * @param {string} albumName
     * @param {string|null} albumArtistName
     */
    constructor(albumName, albumArtistName) {
        const title = vars.tBrowseAlbum + (albumArtistName === null ? '' : albumArtistName + ' - ') + albumName;
        const filters = { album: albumName, order: 'number,title' };
        if (albumArtistName) {
            filters.album_artist = albumArtistName;
        }
        super(title, filters);
    }
}

export class TagBrowse extends TracksBrowse {
    /**
     * @param {string} tagName
     */
    constructor(tagName) {
        super(vars.tBrowseTag + tagName, { tag: tagName });
    }
}

export class PlaylistBrowse extends TracksBrowse {
    /**
     * @param {string} playlistName
     */
    constructor(playlistName) {
        super(vars.tBrowsePlaylist + playlistName, { playlist: playlistName, order: 'ctime_asc' });
    }
}

export class YearBrowse extends TracksBrowse {
    /**
     * @param {number} year
     */
    constructor(year) {
        super(vars.tBrowseYear + year, { year: year, order: 'title' });
    }
}

export class TitleBrowse extends TracksBrowse {
    /**
     * @param {string} title
     */
    constructor(title) {
        super(vars.tBrowseTitle + title, { title: title, order: 'ctime_asc' });
    }
}

export class RecentlyAddedBrowse extends TracksBrowse {
    constructor() {
        super(vars.tBrowseRecentlyAdded, { order: "ctime_desc", limit: 100 });
    }
}

export class RecentlyReleasedBrowse extends TracksBrowse {
    constructor() {
        super(vars.tBrowseRecentlyReleased, { order: "year_desc", limit: 100 });
    }
}

export class RandomBrowse extends TracksBrowse {
    constructor() {
        super(vars.tBrowseRandom, { order: "random", limit: 100 });
    }
}

export class MissingMetadataBrowse extends TracksBrowse {
    constructor() {
        super(vars.tBrowseMissingMetadata, { has_metadata: "0", order: "random", limit: 100 });
    }
}

class Browse {
    /** @type {Array<AbstractBrowse>} */
    #history = [];
    /** @type {AbstractBrowse | null} */
    #current = null;
    #allButton = /** @type {HTMLButtonElement} */ (document.getElementById('browse-all'));
    #backButton = /** @type {HTMLButtonElement} */ (document.getElementById('browse-back'));

    constructor() {
        // Button to open browse window
        this.#allButton.addEventListener('click', () => browse.browse(new HomeBrowse()));

        // Back button in top left corner of browse window
        this.#backButton.addEventListener('click', () => browse.back());

        eventBus.subscribe(MusicEvent.METADATA_CHANGE, () => {
            if (!windows.isOpen('window-browse')) {
                console.debug('browse: ignore METADATA_CHANGE, browse window is not open. Is editor open: ', windows.isOpen('window-editor'));
                return;
            }

            console.debug('browse: received METADATA_CHANGE, updating content');
            this.updateContent();
        });
    };

    /**
     * @param {string} textContent
     */
    setHeader(textContent) {
        const browseWindow = /** @type {HTMLDivElement} */ (document.getElementById('window-browse'));
        browseWindow.getElementsByTagName('h2')[0].textContent = textContent;
    };

    /**
     * @param {AbstractBrowse} nextBrowse
     */
    browse(nextBrowse) {
        windows.open('window-browse');
        if (this.#current != null) {
            this.#history.push(this.#current);
        }
        this.#current = nextBrowse;
        this.updateContent();
    };

    back() {
        const last = this.#history.pop();
        if (last) {
            this.#current = last;
            this.updateContent();
        }
    };

    async updateContent() {
        if (!this.#current) {
            throw new Error("current is null");
        }
        console.debug('browse:', this.#current);

        this.setHeader(this.#current.title);
        await this.#current.render();

        this.#backButton.disabled = this.#history.length == 0;
    }
};

/**
 * also used by search.js
 * @param {HTMLTableSectionElement} table
 * @param {Array<Track>} tracks
 */
export async function populateTrackTable(table, tracks) {
    const addButton = createIconButton('playlist-plus', vars.tTooltipAddToQueue);
    const editButton = createIconButton('pencil', vars.tTooltipEditMetadata);
    const fragment = document.createDocumentFragment();
    for (const track of tracks) {
        const colPlaylist = document.createElement('td');
        colPlaylist.textContent = track.playlistName;

        const colDuration = document.createElement('td');
        colDuration.textContent = durationToString(track.duration);

        const colTitle = document.createElement('td');
        colTitle.appendChild(trackDisplayHtml(track));

        const addButton2 = /** @type {HTMLButtonElement} */ (addButton.cloneNode(true));
        addButton2.addEventListener('click', async () => {
            replaceIconButton(addButton2, 'loading');
            addButton2.disabled = true;

            try {
                const downloadedTrack = await track.download(...settings.getTrackDownloadParams());
                queue.add(downloadedTrack, true);
            } catch (ex) {
                console.error('browse: error adding track to queue', ex);
            }

            replaceIconButton(addButton2, 'playlist-plus');
            addButton2.disabled = false;
        });
        const colAdd = document.createElement('td');
        colAdd.appendChild(addButton2);
        colAdd.style.width = '2rem';

        const colEdit = document.createElement('td');
        colEdit.style.width = '2rem';

        if ((music.playlist(track.playlistName)).write) {
            const editButton2 = editButton.cloneNode(true);
            editButton2.addEventListener('click', () => editor.open(track));
            colEdit.appendChild(editButton2);
        }

        const row = document.createElement('tr');
        row.append(colPlaylist, colDuration, colTitle, colAdd, colEdit);
        fragment.append(row);
    }
    table.replaceChildren(fragment);
}

export const browse = new Browse();
