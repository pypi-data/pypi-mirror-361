// Common JavaScript interface to API, to be used by the music player and other pages.

import { vars, uuidv4, checkResponseCode, jsonPost, jsonGet, clamp } from "./util.js";

const NEWS_URL = '/news/audio';

export const RAPHSON_URL = '/static/img/raphson.png';
export const RAPHSON_SMALL_URL = '/static/img/raphson_small.webp';

export const ControlCommand = {
    CLIENT_REQUEST_UPDATE: "c_request_update",
    CLIENT_PLAYING: "c_playing",
    CLIENT_SUBSCRIBE: "c_subscribe",
    CLIENT_TOKEN: "c_token",
    CLIENT_PLAY: "c_play",
    CLIENT_PAUSE: "c_pause",
    CLIENT_PREVIOUS: "c_previous",
    CLIENT_NEXT: "c_next",
    CLIENT_VOLUME: "c_volume",
    CLIENT_SEEK: "c_seek",
    CLIENT_SET_QUEUE: "c_set_queue",
    CLIENT_SET_PLAYLISTS: "c_set_playlists",
    SERVER_REQUEST_UPDATE: "s_request_update",
    SERVER_PLAYING: "s_playing",
    SERVER_PLAYED: "s_played",
    SERVER_PLAYING_STOPPED: "s_playing_stopped",
    SERVER_FILE_CHANGE: "s_file_change",
    SERVER_PLAY: "s_play",
    SERVER_PAUSE: "s_pause",
    SERVER_PREVIOUS: "s_previous",
    SERVER_NEXT: "s_next",
    SERVER_VOLUME: "s_volume",
    SERVER_SEEK: "s_seek",
    SERVER_SET_QUEUE: "s_set_queue",
    SERVER_SET_PLAYLISTS: "s_set_playlists",
};

export const ControlTopic = {
    ACTIVITY: "activity",
};

class ControlChannel {
    /** @type {string} */
    player_id;
    /** @type {Set<string>} */
    #subscriptions;
    /** @type {Object<string, Array<function>>} */
    #handlers;
    /** @type {Array<Function>} */
    #onConnect;
    /** @type {WebSocket | null} */
    #socket;
    constructor() {
        this.player_id = uuidv4();
        this.#subscriptions = new Set();
        this.#handlers = {};
        this.#onConnect = [];
        this.#socket = null;

        for (const command of Object.values(ControlCommand)) {
            this.#handlers[command] = [];
        }

        if (!vars.offlineMode) {
            setInterval(() => {
                if (this.#socket == null ||
                    !(this.#socket.readyState in [WebSocket.CONNECTING, WebSocket.OPEN])
                ) {
                    this.#open();
                }
            }, 10000);

            this.#open();
        }
    }

    #open() {
        // Modern browsers (since early 2024) have support for connecting to a partial URL (just "/control?id=...").
        // However, we need to support earlier versions, especially because of mobile Safari and Firefox ESR in Linux distributions.
        // So, construct a URL manually:
        var url = new URL('/control?id=' + encodeURIComponent(this.player_id), window.location.href);
        url.protocol = url.protocol.replace('http', 'ws'); // http -> ws, https -> wss
        console.info('ws: connect:', url.href);
        this.#socket = new WebSocket(url.href);

        this.#socket.addEventListener("message", event => this.#handleMessage(event.data));

        // Reissue previous subscriptions when socket is opened
        this.#socket.addEventListener("open", () => {
            this.sendMessage(ControlCommand.CLIENT_TOKEN, { "csrf": vars.csrfToken });
            for (const func of this.#onConnect) {
                func();
            }
            for (const topic of this.#subscriptions) {
                this.sendMessage(ControlCommand.CLIENT_SUBSCRIBE, { "topic": topic });
            }
        });
    }

    /**
     * @param {object} message
     */
    #handleMessage(message) {
        message = JSON.parse(message);
        console.debug('api: ws: received:', message);
        if (message.name in this.#handlers) {
            for (const handler of this.#handlers[message.name]) {
                handler(message);
            }
        } else {
            console.warn("ws: received command is unknown");
        }
    }

    /**
     * @param {string} name
     * @param {import("./types.js").ControlClientCommand} data
     */
    sendMessage(name, data) {
        if (vars.offlineMode) {
            return;
        }
        if (this.#socket == null || this.#socket.readyState != WebSocket.OPEN) {
            console.warn('api: ws: disconnected, cannot send:', name);
            return;
        }
        console.debug('api: ws: send:', name, data);
        this.#socket.send(JSON.stringify({ name: name, ...data }));
    }

    /**
     * @param {string} command
     * @param {function} handler
     */
    registerMessageHandler(command, handler) {
        if (command.startsWith("c_")) throw new Error("it does not make sense to listen for a client event, they are only sent to the server")
        this.#handlers[command].push(handler);
    }

    /**
     * @param {string} command
     * @param {function} handler
     */
    unregisterMessageHandler(command, handler) {
        const i = this.#handlers[command].indexOf(handler);
        if (i == -1) throw new Error("handler not registered");
        this.#handlers[command].splice(i, 1);
    }

    registerConnectHandler(handler) {
        this.#onConnect.push(handler);
    }

    /**
     * @param {string} topic
     * @returns {boolean} true if subscribed, false if already subscribed
     */
    subscribe(topic) {
        if (topic in this.#subscriptions) return false;
        this.#subscriptions.add(topic);
        this.sendMessage(ControlCommand.CLIENT_SUBSCRIBE, { topic: topic });
        return true;
    }

    async play(player_id) {
        this.sendMessage(ControlCommand.CLIENT_PLAY, { player_id: player_id });
    }

    async pause(player_id) {
        this.sendMessage(ControlCommand.CLIENT_PAUSE, { player_id: player_id });
    }

    async previous(player_id) {
        this.sendMessage(ControlCommand.CLIENT_PREVIOUS, { player_id: player_id });
    }

    async next(player_id) {
        this.sendMessage(ControlCommand.CLIENT_NEXT, { player_id: player_id });
    }

    sendStopSignal() {
        const data = new FormData();
        data.set("csrf", vars.csrfToken);
        data.set("id", this.player_id);
        navigator.sendBeacon("/activity/stop", data);
    }
}

export function estimateCurrentPosition(/** @type {import("./types.js").ControlServerPlaying} */ data) {
    if (data.position == null || data.duration == null) {
        return null;
    }
    if (data.paused) {
        return data.position;
    }
    return clamp(data.position + Date.now() / 1000 - data.update_time, 0, data.duration);
}

export const controlChannel = new ControlChannel();

export class Album {
    /** @type {string} */
    name;
    /** @type {string|null} */
    artist;
    /** @type {string} */
    track; // arbitrary track from album to get cover image
    /** @type {number|null} */
    trackMtime;

    /**
     * @param {import("./types.js").AlbumJson} albumObj
     * @param {number | null} mtime
     */
    constructor(albumObj, mtime = null) {
        this.name = albumObj.name;
        this.artist = albumObj.artist;
        this.track = albumObj.track;
        this.trackMtime = mtime;
    }

    /**
     * @param {string} imageQuality 'low' or 'high'
     * @param {boolean} memeCover
     * @returns {string}
     */
    getCoverURL(imageQuality, memeCover) {
        return `/track/${encodeURIComponent(this.track)}/cover?quality=${imageQuality}&meme=${memeCover ? 1 : 0}&mtime=` + this.trackMtime;
    }
}

class SearchResult {
    /** @type {Array<Track>} */
    tracks;
    /** @type {Array<Album>} */
    albums;
    constructor(tracks, albums) {
        this.tracks = tracks;
        this.albums = albums;
    }
}

class Music {
    /** @type {Array<Playlist>|null} */
    #playlists;

    constructor() { }

    async retrievePlaylists() {
        const response = await fetch('/playlist/list');
        checkResponseCode(response);
        const json = await response.json();
        const playlists = [];
        for (const playlistObj of json) {
            playlists.push(new Playlist(playlistObj));
        }
        this.#playlists = playlists;
    }

    /**
     * @returns {Array<Playlist>}
     */
    playlists() {
        if (this.#playlists == null) {
            throw new Error("retrievePlaylists() must be called first");
        }
        return this.#playlists;

    }

    /**
     * @param {string} name
     * @returns {Playlist}
     */
    playlist(name) {
        for (const playlist of this.playlists()) {
            if (playlist.name == name) {
                return playlist;
            }
        }
        throw new Error("playlist not found: " + name);
    }

    /**
     * @param {Array<import("./types.js").TrackJson>} json
     * @returns {Array<Track>}
     */
    #tracksFromJson(json) {
        const tracks = [];
        for (const trackObj of json) {
            tracks.push(new Track(trackObj));
        }
        return tracks;
    }

    /**
     * @param {Array<object>} json
     * @returns {Array<Album>}
     */
    #albumsFromJson(json) {
        const albums = [];
        for (const album of json) {
            albums.push(new Album(album));
        }
        return albums;
    }

    /**
     * @param {object} filters with key = playlist, artist, album_artist, album, etc.
     * @returns {Promise<Array<Track>>}
     */
    async filter(filters) {
        const encodedFilters = [];
        for (const filter in filters) {
            encodedFilters.push(filter + '=' + encodeURIComponent(filters[filter]));
        }
        const response = await fetch('/tracks/filter?' + encodedFilters.join('&'));
        checkResponseCode(response);
        const json = await response.json();
        return this.#tracksFromJson(json.tracks);
    }

    /**
     * @param {string} query FTS5 search query
     * @returns {Promise<SearchResult>}
     */
    async search(query) {
        const response = await fetch('/tracks/search?query=' + encodeURIComponent(query));
        checkResponseCode(response);
        const json = await response.json();
        const tracks = this.#tracksFromJson(json.tracks);
        const albums = this.#albumsFromJson(json.albums);
        return new SearchResult(tracks, albums);
    }

    /**
     * @param {string} path
     * @returns {Promise<Track>}
     */
    async track(path) {
        const response = await fetch(`/track/${encodeURIComponent(path)}/info`);
        checkResponseCode(response);
        return new Track(await response.json());
    }

    /**
     * @returns {Promise<Array<string>>}
     */
    async tags() {
        const response = await fetch('/tracks/tags');
        checkResponseCode(response);
        return await response.json();
    }

    /**
     * @param {Track} track
     * @param {number} startTimestamp
     */
    async played(track, startTimestamp) {
        const data = {
            track: track.path,
            timestamp: startTimestamp,
        };
        await jsonPost('/activity/played', data);
    }

    /**
     * @returns {Promise<DownloadedTrack|null>}
     */
    async downloadNews() {
        const audioResponse = await fetch(NEWS_URL);
        if (audioResponse.status == 503) {
            return null;
        }
        checkResponseCode(audioResponse);
        const name = audioResponse.headers.get("X-Name");
        if (name == null) throw new Error("null name");
        const track = new VirtualTrack(name, 'news');
        const audioBlob = URL.createObjectURL(await audioResponse.blob());
        return new DownloadedTrack(track, audioBlob, RAPHSON_URL, null);
    }
}

export const music = new Music();

export class Playlist {
    /** @type {string} */
    name;
    /** @type {number} */
    trackCount;
    /** @type {boolean} */
    favorite;
    /** @type {boolean} */
    write;

    /**
     * @param {Object.<string, string|boolean|number>} objectFromApi
     */
    constructor(objectFromApi) {
        this.name = /** @type {string} */ (objectFromApi.name);
        this.trackCount = /** @type {number} */ (objectFromApi.track_count);
        this.favorite = /** @type {boolean} */ (objectFromApi.favorite);
        this.write = /** @type {boolean} */ (objectFromApi.write);
    }

    /**
     * @param {boolean} requireMetadata
     * @param {object} tagFilter Empty object for no tag filter
     * @returns
     */
    async chooseRandomTrack(requireMetadata, tagFilter) {
        const chooseResponse = await jsonPost('/playlist/' + encodeURIComponent(this.name) + '/choose_track', { 'require_metadata': requireMetadata, ...tagFilter });
        const trackData = await chooseResponse.json();
        console.info('api: chosen track', trackData.path);
        return new Track(trackData);
    }
}

export class Track {
    /** @type {string} */
    path;
    /** @type {number} */
    mtime
    /** @type {number} */
    ctime;
    /** @type {number} */
    duration;
    /** @type {Array<string>} */
    tags;
    /** @type {string | null} */
    title;
    /** @type {Array<string>} */
    artists;
    /** @type {string | null} */
    album;
    /** @type {string | null} */
    albumArtist;
    /** @type {number | null} */
    year;
    /** @type {number | null} */
    trackNumber;
    /** @type {string | null} */
    video;
    /** @type {string | null} */
    lyrics;

    /**
     * @param {import("./types.js").TrackJson} trackData
     */
    constructor(trackData) {
        this.#updateLocalVariablesFromTrackDataResponse(trackData);
    };

    get playlistName() {
        return this.path.substring(0, this.path.indexOf('/'));
    }

    /**
     * @param {import("./types.js").TrackJson} trackData
     */
    #updateLocalVariablesFromTrackDataResponse(trackData) {
        this.path = trackData.path;
        this.mtime = trackData.mtime;
        this.ctime = trackData.ctime;
        this.duration = trackData.duration;
        this.title = trackData.title || null;
        this.album = trackData.album || null;
        this.albumArtist = trackData.album_artist || null;
        this.year = trackData.year || null;
        this.trackNumber = trackData.track_number || null;
        this.video = trackData.video || null;
        this.lyrics = trackData.lyrics || null;
        this.artists = trackData.artists || [];
        this.tags = trackData.tags || [];
    }

    /**
     * Generates display text for this track
     * @param {boolean} showPlaylist
     * @returns {string}
     */
    displayText(showPlaylist = true, showAlbum = true) {
        // Should be similar to on Metadata.display_title on server for consistency

        let text = '';

        if (showPlaylist) {
            text += `${this.playlistName}: `;
        }

        if (this.artists.length > 0 && this.title !== null) {
            text += this.artists.join(', ');
            text += ' - ';
            text += this.title;

            if (this.album && showAlbum) {
                text += ` (${this.album}`;
                if (this.year) {
                    text += `, ${this.year})`;
                } else {
                    text += ')';
                }
            } else if (this.year) {
                text += ` (${this.year})`;
            }
        } else {
            // Not enough metadata available, generate display title based on file name
            let filename = this.path.substring(this.path.lastIndexOf('/') + 1);

            // remove extension
            filename = filename.substring(0, filename.lastIndexOf('.'));

            // Remove YouTube id suffix
            filename = filename.replaceAll(/\[[a-zA-Z0-9\-_]+\]/g, "");

            // Remove whitespace
            filename = filename.trim();

            text += filename;
        }

        return text;
    };

    /**
     * @param {string} audioType
     * @returns string
     */
    getAudioURL(audioType) {
        return `/track/${encodeURIComponent(this.path)}/audio?type=${audioType}&mtime=` + this.mtime;
    }

    getAlbum() {
        return new Album({ 'name': this.album, 'artist': this.albumArtist, 'track': this.path }, this.mtime);
    }

    /**
     * @returns {Promise<Lyrics|null>}
     */
    async getLyrics() {
        const lyricsUrl = `/track/${encodeURIComponent(this.path)}/lyrics?mtime=` + this.mtime;
        const lyricsResponse = await fetch(lyricsUrl);
        checkResponseCode(lyricsResponse);
        const lyricsJson = await lyricsResponse.json();
        console.debug('api: downloaded lyrics', lyricsUrl);
        switch (lyricsJson.type) {
            case "none":
                return null;
            case "synced":
                const lines = [];
                for (const line of lyricsJson.text) {
                    lines.push(new LyricsLine(line.start_time, line.text));
                }
                return new TimeSyncedLyrics(lyricsJson.source, lines);
            case "plain":
                return new PlainLyrics(lyricsJson.source, lyricsJson.text);
        }
        throw new Error("unexpected lyrics type");
    }

    /**
     * @param {string} audioType
     * @param {boolean} memeCover
     * @returns {Promise<DownloadedTrack>}
     */
    async download(audioType = 'webm_opus_high', memeCover = false) {
        const imageQuality = audioType == 'webm_opus_low' ? 'low' : 'high';
        const audioUrl = this.getAudioURL(audioType);
        const coverUrl = this.getAlbum().getCoverURL(imageQuality, memeCover);
        const lyrics = await this.getLyrics();

        // cache audio in background
        fetch(audioUrl)
        return new DownloadedTrack(this, audioUrl, coverUrl, lyrics);
    }

    async delete() {
        const oldName = this.path.split('/').pop();
        const newName = '.trash.' + oldName;
        await jsonPost('/files/rename', { path: this.path, new_name: newName });
    }

    async dislike() {
        await jsonPost('/dislikes/add', { track: this.path });
    }

    /**
     * Updates track metadata by sending current metadata of this object to the server.
     */
    async saveMetadata() {
        const payload = {
            title: this.title,
            album: this.album,
            artists: this.artists,
            album_artist: this.albumArtist,
            tags: this.tags,
            year: this.year,
            track_number: this.trackNumber,
            lyrics: this.lyrics,
        };

        await jsonPost(`/track/${encodeURIComponent(this.path)}/update_metadata`, payload);
    }

    /**
     * Copy track to other ~playlist
     * @param {string} playlistName
     * @returns {Promise<void>}
     */
    async copyTo(playlistName) {
        await jsonPost('/files/copy', { src: this.path, dest: playlistName });
    }

    async refresh() {
        const json = await jsonGet(`/track/${encodeURIComponent(this.path)}/info`);
        this.#updateLocalVariablesFromTrackDataResponse(json);
    }

    /**
     * Look up metadata for this track using the AcoustID service
     * @returns {Promise<import("./types.js").AcoustIDResult | null>}
     */
    async acoustid() {
        return await jsonGet(`/track/${encodeURIComponent(this.path)}/acoustid`);
    }

    getVideoURL() {
        return `/track/${encodeURIComponent(this.path)}/video`;
    }

    async reportProblem() {
        await jsonPost(`/track/${encodeURIComponent(this.path)}/report_problem`, {});
    }
}

export class VirtualTrack {
    /** @type {string} */
    title;
    /** @type {string} */
    type;

    /**
     * @param {string} title
     * @param {string} type
     */
    constructor(title, type) {
        this.title = title;
        this.type = type;
    }

    isNews() {
        return this.type == 'news';
    }
}

export class DownloadedTrack {
    /**
     * @type {Track|VirtualTrack}
     */
    track;
    /**
     * @type {string}
     */
    audioUrl;
    /**
     * @type {string}
     */
    imageUrl;
    /**
     * @type {Lyrics|null}
     */
    lyrics;

    /**
     *
     * @param {Track|VirtualTrack} track
     * @param {string} audioUrl
     * @param {string} imageUrl
     * @param {Lyrics|null} lyrics
     */
    constructor(track, audioUrl, imageUrl, lyrics) {
        this.track = track;
        this.audioUrl = audioUrl;
        this.imageUrl = imageUrl;
        this.lyrics = lyrics;
    }
}

export class Lyrics {
    /** @type {string | null} */
    source;
    constructor(source) {
        this.source = source;
    };
};

export class PlainLyrics extends Lyrics {
    /** @type {string} */
    text;
    constructor(source, text) {
        super(source);
        this.text = text;
    };
};

export class LyricsLine {
    /** @type {number} */
    startTime;
    /** @type {string} */
    text;
    constructor(startTime, text) {
        this.startTime = startTime;
        this.text = text;
    }
}

export class TimeSyncedLyrics extends Lyrics {
    /** @type {Array<LyricsLine>} */
    text;
    constructor(source, text) {
        super(source);
        this.text = text;
    };

    /**
     * @returns {string}
     */
    asPlainText() {
        const lines = [];
        for (const line of this.text) {
            lines.push(line.text);
        }
        return lines.join('\n');
    }

    /**
     * @param {number} currentTime
     * @returns {number}
     */
    currentLine(currentTime) {
        currentTime += 0.5; // go to next line slightly earlier, to give the user time to read
        // current line is the last line where currentTime is after the line start time
        for (let i = 0; i < this.text.length; i++) {
            if (currentTime < this.text[i].startTime) {
                return i - 1;
            }
        }
        return this.text.length - 1;
    }
};
