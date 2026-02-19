#!/bin/bash
# Record HTML bumpers to MP4 video files using Xvfb + Chromium + FFmpeg
# Each bumper records for DURATION seconds at 1920x1080 30fps

DURATION=${1:-45}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DISPLAY_NUM=99
SCREEN_SIZE="1920x1080x24"

BUMPERS=(
  "well-be-right-back"
  "please-stand-by"
  "up-next"
)

cleanup() {
  kill "$UNCLUTTER_PID" 2>/dev/null
  kill "$XVFB_PID" 2>/dev/null
  kill "$CHROME_PID" 2>/dev/null
}
trap cleanup EXIT

echo "=== Pi TV Bumper Recorder ==="
echo "Duration: ${DURATION}s per bumper"
echo ""

# Start Xvfb
echo "[*] Starting virtual display :${DISPLAY_NUM}..."
Xvfb ":${DISPLAY_NUM}" -screen 0 "${SCREEN_SIZE}" -ac +extension GLX +render -noreset &
XVFB_PID=$!
sleep 2

if ! kill -0 "$XVFB_PID" 2>/dev/null; then
  echo "[!] Failed to start Xvfb"
  exit 1
fi

export DISPLAY=":${DISPLAY_NUM}"

# Hide the mouse cursor
unclutter -idle 0 -root &
UNCLUTTER_PID=$!
# Also move cursor off-screen
xdotool mousemove 9999 9999 2>/dev/null

echo "[OK] Virtual display running (cursor hidden)"
echo ""

for BUMPER in "${BUMPERS[@]}"; do
  HTML_FILE="${SCRIPT_DIR}/${BUMPER}.html"
  MP4_FILE="${SCRIPT_DIR}/${BUMPER}.mp4"

  if [ ! -f "$HTML_FILE" ]; then
    echo "[!] Skipping ${BUMPER} - HTML file not found"
    continue
  fi

  echo "[*] Recording: ${BUMPER}"
  echo "    Source: ${HTML_FILE}"
  echo "    Output: ${MP4_FILE}"

  # Launch Chromium in kiosk mode
  chromium \
    --no-sandbox \
    --disable-gpu \
    --disable-software-rasterizer \
    --window-size=1920,1080 \
    --window-position=0,0 \
    --kiosk \
    --disable-infobars \
    --disable-notifications \
    --disable-translate \
    --disable-extensions \
    --disable-background-timer-throttling \
    --disable-renderer-backgrounding \
    --disable-backgrounding-occluded-windows \
    --autoplay-policy=no-user-gesture-required \
    "file://${HTML_FILE}" &
  CHROME_PID=$!

  # Wait for the page to fully load and animations to start
  echo "    Waiting for page load..."
  sleep 5

  # Record with ffmpeg using x11grab
  echo "    Recording ${DURATION}s..."
  ffmpeg -y \
    -video_size 1920x1080 \
    -framerate 30 \
    -f x11grab \
    -i ":${DISPLAY_NUM}" \
    -t "${DURATION}" \
    -c:v libx264 \
    -preset medium \
    -crf 20 \
    -pix_fmt yuv420p \
    -movflags +faststart \
    "${MP4_FILE}" \
    2>/dev/null

  # Kill Chromium
  kill "$CHROME_PID" 2>/dev/null
  wait "$CHROME_PID" 2>/dev/null

  if [ -f "$MP4_FILE" ]; then
    SIZE=$(du -h "$MP4_FILE" | cut -f1)
    echo "    [OK] Done! (${SIZE})"
  else
    echo "    [!] Failed to create video"
  fi
  echo ""
done

echo "=== All bumpers recorded ==="
ls -lh "${SCRIPT_DIR}"/*.mp4 2>/dev/null
