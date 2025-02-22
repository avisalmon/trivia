import wave
import math
import struct
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

def generate_beep(filename, frequency=800, duration=0.1, num_beeps=1, beep_gap=0.1):
    """Generate a beep sound and save it as a WAV file."""
    try:
        # Audio parameters
        sample_rate = 44100
        amplitude = 32767
        
        def generate_samples(freq, dur):
            num_samples = int(sample_rate * dur)
            samples = []
            for i in range(num_samples):
                t = float(i) / sample_rate
                sample = amplitude * math.sin(2 * math.pi * freq * t)
                samples.append(struct.pack('h', int(sample)))
            return b''.join(samples)
        
        # Create the WAV file
        with wave.open(filename, 'w') as wav_file:
            # Set parameters
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            
            # Generate beeps with gaps
            for i in range(num_beeps):
                wav_file.writeframes(generate_samples(frequency, duration))
                if i < num_beeps - 1:  # Don't add gap after last beep
                    wav_file.writeframes(generate_samples(0, beep_gap))
        
        logger.info(f"Successfully generated beep sound: {filename}")
    except Exception as e:
        logger.error(f"Error generating beep sound {filename}: {e}")
        raise

def generate_success_sound(filename):
    """Generate a success sound (ascending tones) and save it as a WAV file."""
    try:
        # Audio parameters
        sample_rate = 44100
        amplitude = 32767
        duration = 0.15
        
        frequencies = [523.25, 659.25, 783.99]  # C5, E5, G5 (C major chord)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            for freq in frequencies:
                num_samples = int(sample_rate * duration)
                for i in range(num_samples):
                    t = float(i) / sample_rate
                    sample = amplitude * math.sin(2 * math.pi * freq * t)
                    wav_file.writeframes(struct.pack('h', int(sample)))
        
        logger.info(f"Successfully generated success sound: {filename}")
    except Exception as e:
        logger.error(f"Error generating success sound {filename}: {e}")
        raise

def ensure_sound_files():
    """Ensure sound files exist, generate them if they don't."""
    try:
        # Get the assets directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        assets_dir = os.path.join(base_dir, "assets")
        
        # Create assets directory if it doesn't exist
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
            logger.info(f"Created assets directory: {assets_dir}")
        
        # Generate timer alert sound if it doesn't exist
        timer_sound = os.path.join(assets_dir, "timer_alert.wav")
        if not os.path.exists(timer_sound):
            generate_beep(timer_sound, frequency=800, duration=0.1, num_beeps=2, beep_gap=0.1)
            logger.info(f"Generated timer alert sound: {timer_sound}")
        
        # Generate success sound if it doesn't exist
        success_sound = os.path.join(assets_dir, "success.wav")
        if not os.path.exists(success_sound):
            generate_success_sound(success_sound)
            logger.info(f"Generated success sound: {success_sound}")
        
        return True
    except Exception as e:
        logger.error(f"Error ensuring sound files: {e}")
        return False

if __name__ == "__main__":
    # Configure logging when run directly
    logging.basicConfig(level=logging.INFO)
    ensure_sound_files() 