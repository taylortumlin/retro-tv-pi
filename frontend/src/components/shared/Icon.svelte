<script lang="ts">
  interface Props {
    name: string;
    size?: number;
    strokeWidth?: number;
    fill?: string;
  }

  let { name, size = 20, strokeWidth = 2, fill = 'none' }: Props = $props();

  interface IconDef {
    paths: string;
    defaultFill?: boolean;
  }

  const icons: Record<string, IconDef> = {
    search: { paths: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>' },
    close: { paths: '<path d="M18 6L6 18M6 6l12 12"/>' },
    play: { paths: '<polygon points="5 3 19 12 5 21 5 3"/>', defaultFill: true },
    pause: { paths: '<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>', defaultFill: true },
    mute: { paths: '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/>' },
    unmute: { paths: '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14M15.54 8.46a5 5 0 010 7.07"/>' },
    volume: { paths: '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 010 7.07"/>' },
    menu: { paths: '<path d="M4 6h16M4 12h16M4 18h16"/>' },
    settings: { paths: '<path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3"/>' },
    cloud: { paths: '<path d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"/>' },
    star: { paths: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>' },
    'star-filled': { paths: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>', defaultFill: true },
    tv: { paths: '<rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/>' },
    bell: { paths: '<path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/>' },
    'bell-filled': { paths: '<path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/>', defaultFill: true },
    'chevron-left': { paths: '<path d="M15 18l-6-6 6-6"/>' },
    'chevron-right': { paths: '<path d="M9 18l6-6-6-6"/>' },
    'chevron-up': { paths: '<path d="M18 15l-6-6-6 6"/>' },
    'chevron-down': { paths: '<path d="M6 9l6 6 6-6"/>' },
    refresh: { paths: '<path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>' },
    plus: { paths: '<path d="M12 5v14M5 12h14"/>' },
    trash: { paths: '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>' },
    download: { paths: '<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>' },
    clock: { paths: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>' },
    grid: { paths: '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>' },
    home: { paths: '<path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>' },
  };

  let icon = $derived(icons[name]);
  let computedFill = $derived(fill !== 'none' ? fill : (icon?.defaultFill ? 'currentColor' : 'none'));
</script>

{#if icon}
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill={computedFill}
    stroke="currentColor"
    stroke-width={strokeWidth}
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    {@html icon.paths}
  </svg>
{/if}
