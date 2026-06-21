#!/usr/bin/env python3
"""
Generate TTS audio from article text using OpenClaw's TTS capability.
"""
import json
import sys
import os
import subprocess
import tempfile

def generate_tts(text, output_path, voice=None):
    """Generate TTS audio from text and save to output_path."""
    
    # Write text to temp file (say reads from file, no CLI arg limits)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp.write(text)
        tmp_path = tmp.name
    
    try:
        aiff_path = output_path.replace('.mp3', '.aiff').replace('.aac', '.aiff')
        
        # Use say with -f to read from file (handles any length)
        if voice:
            cmd = f"say -v '{voice}' -f '{tmp_path}' -o '{aiff_path}'"
        else:
            cmd = f"say -f '{tmp_path}' -o '{aiff_path}'"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=300)
        
        if result.returncode != 0:
            print(f"say command failed: {result.stderr.decode()}", file=sys.stderr)
            return None
        
        # Convert to mp3 with ffmpeg
        cmd = f"ffmpeg -y -i '{aiff_path}' -codec:a libmp3lame -qscale:a 2 '{output_path}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
        
        if result.returncode == 0:
            os.remove(aiff_path)
            os.remove(tmp_path)
            return output_path
        else:
            print(f"ffmpeg conversion failed: {result.stderr.decode()}", file=sys.stderr)
            os.remove(tmp_path)
            return aiff_path
        
    except Exception as e:
        os.remove(tmp_path)
        print(f"Error generating TTS: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate-tts.py <input-text-file> <output-audio-path> [voice]", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_path = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else None
    
    with open(input_file, 'r') as f:
        text = f.read()
    
    result = generate_tts(text, output_path, voice)
    if result:
        print(result)
    else:
        sys.exit(1)
