import { AlbumBrowse, ArtistBrowse, browse, PlaylistBrowse, TitleBrowse, YearBrowse } from "./browse.js";
import { Track, VirtualTrack } from "../api.js";


/**
 * @param {Track} track
 */
function getPrimaryLine(track) {
    const primary = document.createElement('div');

    if (track.artists.length > 0 && track.title) {
        let first = true;
        for (const artist of track.artists) {
            if (first) {
                first = false;
            } else {
                primary.append(', ');
            }

            const artistHtml = document.createElement('a');
            artistHtml.textContent = artist;
            artistHtml.addEventListener("click", () => browse.browse(new ArtistBrowse(artist)));
            primary.append(artistHtml);
        }

        const titleHtml = document.createElement('a');
        titleHtml.textContent = track.title;
        titleHtml.style.color = 'var(--text-color)';
        const title = track.title;
        titleHtml.addEventListener("click", () => browse.browse(new TitleBrowse(title)));
        primary.append(' - ', titleHtml);
    } else {
        const span = document.createElement('span');
        span.style.color = "var(--text-color-warning)";
        span.textContent = track.path.substring(track.path.indexOf('/') + 1);
        primary.append(span);
    }
    return primary;
}

/**
 * @param {Track} track
 * @param {boolean} showPlaylist
 */
function getSecondaryLine(track, showPlaylist) {
    const secondary = document.createElement('div');
    secondary.classList.add('secondary');
    secondary.style.marginTop = 'var(--smallgap)';

    if (showPlaylist) {
        const playlistHtml = document.createElement('a');
        playlistHtml.addEventListener("click", () => browse.browse(new PlaylistBrowse(track.playlistName)));
        playlistHtml.textContent = track.playlistName;
        secondary.append(playlistHtml);
    }

    const year = track.year;
    const album = track.album;
    const albumArtist = track.albumArtist;

    if (year || track.album) {
        if (showPlaylist) {
            secondary.append(', ');
        }

        if (album) {
            const albumHtml = document.createElement('a');
            albumHtml.addEventListener("click", () => browse.browse(new AlbumBrowse(album, albumArtist)));
            if (albumArtist) {
                albumHtml.textContent = albumArtist + ' - ' + album;
            } else {
                albumHtml.textContent = album;
            }
            secondary.append(albumHtml);
            if (track.year) {
                secondary.append(', ');
            }
        }

        if (year) {
            const yearHtml = document.createElement('a');
            yearHtml.textContent = year + '';
            yearHtml.addEventListener('click', () => browse.browse(new YearBrowse(year)));
            secondary.append(yearHtml);
        }
    }
    return secondary;
}

/**
 * Get display HTML for a track
 * @param {Track|VirtualTrack} track
 * @param {boolean} showPlaylist
 * @returns {HTMLSpanElement}
 */
export function trackDisplayHtml(track, showPlaylist = false) {
    const html = document.createElement('div');
    html.classList.add('track-display-html');

    if (track instanceof VirtualTrack) {
        html.textContent = track.title;
    } else {
        html.append(getPrimaryLine(track), getSecondaryLine(track, showPlaylist));
    }

    return html;
};
