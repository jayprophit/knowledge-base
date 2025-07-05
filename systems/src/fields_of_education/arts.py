"""
Arts Integration: Fine Arts, Music, Performing Arts, Design
"""
from midi2audio import FluidSynth

class ArtsModule:
    def midi_to_audio(self, midi_file, output_file):
        fs = FluidSynth()
        fs.midi_to_audio(midi_file, output_file)
