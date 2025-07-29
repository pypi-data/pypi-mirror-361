from openal import oalOpen, oalQuit, Listener
import threading


class AudioEngine:
    def __init__(self, max_channels=32):
        self.max_channels = max_channels
        self.current_channels = 0
        self.groups = {
            "master": 1.0,
            "music": 1.0,
            "effects": 1.0,
        }
        self.loaded_sounds = {}  # {name: buffer}
        self.active_sounds = []  # List of playing sources
        self.lock = threading.Lock()

    def load_sound(self, name, file_path):
        """Load a sound file into memory."""
        if name in self.loaded_sounds:
            print(f"Sound '{name}' is already loaded.")
            return
        sound = oalOpen(file_path)
        if sound:
            self.loaded_sounds[name] = sound
            print(f"Sound '{name}' loaded.")
        else:
            print(f"Failed to load sound: {file_path}")

    def unload_sound(self, name):
        """Unload a sound from memory."""
        if name in self.loaded_sounds:
            self.loaded_sounds[name].stop()
            self.loaded_sounds[name].delete()
            del self.loaded_sounds[name]
            print(f"Sound '{name}' unloaded.")
        else:
            print(f"Sound '{name}' is not loaded.")

    def play_sound(self, name, group="master", position=(0, 0, 0), volume=1.0, loop=False):
        """Play a loaded sound with spatial positioning."""
        with self.lock:
            if name not in self.loaded_sounds:
                print(f"Sound '{name}' is not loaded. Please load it first.")
                return

            sound = self.loaded_sounds[name]
            source = sound.play()

            if not source:
                print(f"Failed to play sound '{name}'.")
                return

            source.set_position(position)
            source.set_gain(volume)
            source.set_looping(loop)
            self.active_sounds.append(source)
            self.current_channels += 1

            # Monitor sound status
            threading.Thread(target=self._monitor_sound, args=(source,), daemon=True).start()
            return source


    def _monitor_sound(self, source):
        """Monitor the sound and release the channel when it finishes."""
        while source.state == "playing":
            pass  # Wait for the sound to finish
        with self.lock:
            self.current_channels -= 1
            self.active_sounds.remove(source)

    def set_group_volume(self, group, volume):
        """Set the volume for a specific group."""
        if group in self.groups:
            self.groups[group] = volume
            for source in self.active_sounds:
                # Update volumes for active sounds in this group
                gain = source.gain / self.groups[group] * volume
                source.set_gain(gain)

    def stop_all(self):
        """Stop all currently playing sounds."""
        with self.lock:
            for source in self.active_sounds:
                source.stop()
            self.active_sounds.clear()
            self.current_channels = 0

    def set_listener_position(self, position):
        """Set the listener's position for spatial audio."""
        Listener().set_position(position)

    def set_listener_orientation(self, at, up):
        """Set the listener's orientation for spatial audio."""
        Listener().set_orientation(at, up)

    def quit(self):
        """Clean up and quit the audio engine."""
        self.stop_all()
        oalQuit()


# Example Usage
if __name__ == "__main__":
    from ursina import *

    app = Ursina()
    engine = AudioEngine(max_channels=8)

    # Load sounds
    music = engine.load_sound("background", "chillstep_1.ogg")

    # # Play sounds
    music = engine.play_sound("background", group="music", position=(0, 0, 0), volume=0.1, loop=True)

    # # Adjust listener position for 3D audio
    def update():
        engine.set_listener_position(camera.world_position)
        print(music)
        if music:
            music.set_gain(.1)

    # # Adjust group volume
    engine.set_group_volume("music", 0.1)
    # Wait for a while to hear the sounds
    # import time
    # time.sleep(10)

    # Stop all sounds and quit
    # engine.quit()
    from ursina.prefabs.first_person_controller import FirstPersonController
    FirstPersonController(gravity=0)
    Sky()
    ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))
    app.run()