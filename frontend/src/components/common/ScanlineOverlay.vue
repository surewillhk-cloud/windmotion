<template>
  <div class="scanline-overlay" />
</template>

<style scoped>
.scanline-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 229, 255, 0.015) 2px,
    rgba(0, 229, 255, 0.015) 4px
  );
}
</style>
