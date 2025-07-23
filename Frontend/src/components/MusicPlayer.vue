<template>
  <div class="music-player">
    <div class="cover">
      <img :src="currentTrack.cover || defaultCover" alt="Album Cover" />
    </div>

    <div class="track-info">
      <div class="song-title">{{ currentTrack.title }}</div>
      <div class="song-artist">{{ currentTrack.artist }}</div>
    </div>

    <div class="time-display">
      <span>{{ formatTime(currentTime) }}</span>
      <input type="range" min="0" :max="duration" step="0.1" v-model="seek" @input="seekAudio" />
      <span>{{ formatTime(duration) }}</span>
    </div>

    <div class="controls">
      <button @click="prevTrack">⏮</button>
      <button @click="togglePlay">{{ isPlaying ? '⏸' : '▶️' }}</button>
      <button @click="nextTrack">⏭</button>
      <button :class="{ active: isShuffle }" @click="toggleShuffle">🔀</button>
      <button :class="{ active: isRepeating }" @click="toggleRepeat">🔁</button>
    </div>

    <div class="volume-control">
      🔉
      <input type="range" min="0" max="1" step="0.01" v-model="volume" @input="changeVolume" />
    </div>

    <audio
      ref="audioRef"
      :src="currentTrack.url"
      @timeupdate="updateTime"
      @ended="handleTrackEnd"
      @loadedmetadata="setDuration"
    ></audio>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import apiService from '@/services/apiService'

const audioRef = ref(null)
const playlist = ref([])
const defaultCover = 'https://via.placeholder.com/200x200?text=Cover'
const activeIndex = ref(0)

const isPlaying = ref(false)
const isShuffle = ref(false)
const isRepeating = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const seek = ref(0)
const volume = ref(Number(localStorage.getItem('music-volume')) || 0.7)

const currentTrack = computed(() => playlist.value[activeIndex.value] || {})

// Fetch playlist from backend
async function fetchPlaylist() {
  try {
    const res = await apiService.get('/sc/my-music') // ❗ Customize URL to your backend music endpoint
    playlist.value = res.data.tracks || []
    activeIndex.value = 0
  } catch (err) {
    console.error('🔴 Failed to fetch playlist:', err)
  }
}

// Playback Controls
async function togglePlay() {
  const audio = audioRef.value
  if (!audio) return
  try {
    if (isPlaying.value) {
      audio.pause()
    } else {
      await audio.play()
    }
    isPlaying.value = !isPlaying.value
  } catch (err) {
    console.warn('❌ Autoplay blocked or play failed:', err.message)
  }
}

function nextTrack() {
  if (isShuffle.value) {
    let next = Math.floor(Math.random() * playlist.value.length)
    while (next === activeIndex.value && playlist.value.length > 1) {
      next = Math.floor(Math.random() * playlist.value.length)
    }
    activeIndex.value = next
  } else {
    activeIndex.value = (activeIndex.value + 1) % playlist.value.length
  }
  resetAndPlay()
}

function prevTrack() {
  activeIndex.value =
    activeIndex.value === 0 ? playlist.value.length - 1 : activeIndex.value - 1
  resetAndPlay()
}

// Helpers
function resetAndPlay() {
  const audio = audioRef.value
  if (!audio) return
  audio.pause()
  audio.currentTime = 0
  nextTick(() => {
    if (isPlaying.value) {
      audio.play().catch(err => console.warn('▶️ Autoplay failed:', err.message))
    }
  })
}

function updateTime() {
  const audio = audioRef.value
  if (audio) {
    currentTime.value = audio.currentTime
    seek.value = currentTime.value
  }
}
function setDuration() {
  const audio = audioRef.value
  if (audio) {
    duration.value = audio.duration || 0
  }
}
function seekAudio() {
  if (audioRef.value) {
    audioRef.value.currentTime = seek.value
  }
}
function changeVolume() {
  const audio = audioRef.value
  if (audio) {
    audio.volume = volume.value
    localStorage.setItem('music-volume', volume.value)
  }
}
function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}
function toggleShuffle() {
  isShuffle.value = !isShuffle.value
}
function toggleRepeat() {
  isRepeating.value = !isRepeating.value
}

function handleTrackEnd() {
  if (isRepeating.value) {
    resetAndPlay()
  } else {
    nextTrack()
  }
}

// Mount
onMounted(async () => {
  await fetchPlaylist()
  const savedVolume = localStorage.getItem('music-volume')
  if (savedVolume) volume.value = Number(savedVolume)
  changeVolume()
})
</script>

<style scoped>
.music-player {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  max-width: 500px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  margin: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.cover img {
  width: 180px;
  height: 180px;
  object-fit: cover;
  border-radius: 16px;
}
.track-info {
  text-align: center;
}
.song-title {
  font-weight: bold;
  font-size: 1.2rem;
}
.song-artist {
  color: #555;
  font-size: 0.95rem;
}
.controls {
  display: flex;
  gap: 1rem;
}
.controls button {
  font-size: 1.3rem;
  padding: 0.4rem 0.8rem;
  cursor: pointer;
  border: none;
  border-radius: 8px;
  background-color: #f1f1f1;
  transition: all 0.2s;
}
.controls button.active {
  background-color: #8bc34a;
  color: white;
}
.volume-control, .time-display {
  display: flex;
  align-items: center;
  width: 90%;
  gap: 0.5rem;
}
input[type='range'] {
  flex-grow: 1;
  accent-color: #2196f3;
}
</style>
