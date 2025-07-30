const { importWhiteboxStateStore } = Whitebox;

const useMapStore = await importWhiteboxStateStore("map");

// Patch the marker icon URL to use the one from the plugin
useMapStore.getState().setWhiteboxMarkerIcon({
  iconURL: Whitebox.api.getStaticUrl("whitebox_plugin_map_icons/assets/plane.svg"),
  isRotating: true,
  initialRotation: 180,
})
