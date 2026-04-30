import mpegts from 'mpegts.js';

export interface StreamPlayer {
  play(): void;
  destroy(): void;
  mute(muted: boolean): void;
  setVolume(v: number): void;
}

export function createStreamPlayer(
  videoEl: HTMLVideoElement,
  channelNumber: string | number
): StreamPlayer {
  const tsUrl = `/stream/${channelNumber}.ts`;

  // Try mpegts.js first for MPEG-TS streams
  if (mpegts.isSupported()) {
    const player = mpegts.createPlayer({
      type: 'mpegts',
      url: tsUrl,
      isLive: true,
    }, {
      enableWorker: true,
      liveBufferLatencyChasing: true,
      liveBufferLatencyMaxLatency: 3,
      liveBufferLatencyMinRemain: 0.5,
    });

    player.attachMediaElement(videoEl);

    return {
      play() {
        player.load();
        player.play();
      },
      destroy() {
        player.pause();
        player.unload();
        player.detachMediaElement();
        player.destroy();
      },
      mute(muted: boolean) {
        videoEl.muted = muted;
      },
      setVolume(v: number) {
        videoEl.volume = v / 100;
      },
    };
  }

  // Fallback: native HLS (Safari) or direct
  const hlsUrl = `/stream/${channelNumber}.m3u8`;

  return {
    play() {
      // Try HLS first, fall back to TS
      videoEl.src = videoEl.canPlayType('application/vnd.apple.mpegurl') ? hlsUrl : tsUrl;
      videoEl.play().catch(() => {});
    },
    destroy() {
      videoEl.pause();
      videoEl.removeAttribute('src');
      videoEl.load();
    },
    mute(muted: boolean) {
      videoEl.muted = muted;
    },
    setVolume(v: number) {
      videoEl.volume = v / 100;
    },
  };
}
