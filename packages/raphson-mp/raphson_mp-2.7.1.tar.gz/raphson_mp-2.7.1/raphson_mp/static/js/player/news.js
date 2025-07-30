import { queue } from "./queue.js";
import { player } from "./player.js";
import { DownloadedTrack, music, VirtualTrack } from "../api.js";

class News {
    #newsSetting = /** @type {HTMLInputElement} */ (document.getElementById('settings-news'));

    constructor() {
        setInterval(() => this.check(), 60_000);
    }

    #hasQueuedNews() {
        const isNews = (/** @type {DownloadedTrack} */ track) => track.track instanceof VirtualTrack && track.track.isNews();

        return (queue.currentTrack && isNews(queue.currentTrack))
            || queue.queuedTracks.some(isNews)
            || queue.previousTracks.some(isNews);
    }

    /**
     * Called every minute. Checks if news should be queued.
     * @returns {void}
     */
    check() {
        if (!this.#newsSetting.checked) {
            console.debug('news: is disabled');
            return;
        }

        const minutes = new Date().getMinutes();
        const isNewsTime = minutes >= 10 && minutes < 15;
        if (!isNewsTime) {
            console.debug('news: not news time');
            return;
        }

        if (this.#hasQueuedNews()) {
            console.debug('news: already queued');
            return;
        }

        if (player.isPaused()) {
            console.debug('news: will not queue, audio paused');
            return;
        }

        console.info('news: queueing news');
        this.queue();
    }

    /**
     * Downloads news, and add it to the queue
     */
    async queue() {
        const track = await music.downloadNews();
        if (track) {
            queue.add(track, true, true);
        }
    }
}

export const news = new News();
