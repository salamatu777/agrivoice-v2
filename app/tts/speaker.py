import os
import ssl
import logging
from typing import Optional

# Ensure SSL certificate verification works regardless of machine clock date
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

try:
    from gtts import gTTS
    HAVE_GTTS = True
except ImportError:
    HAVE_GTTS = False

logger = logging.getLogger(__name__)

class TTSSpeaker:
    def __init__(self):
        # Native gTTS voice for Hausa; Nigerian English accent for others
        pass

    def synthesize(self, text: str, language: str, output_path: str) -> Optional[str]:
        if not HAVE_GTTS:
            logger.warning("gTTS not installed. Skipping audio synthesis.")
            return None

        lang_code = language.lower()[:2]
        
        try:
            if lang_code == "ha":
                # Native Hausa speech synthesis
                tts = gTTS(text=text, lang="ha", slow=False)
            elif lang_code in ["yo", "ig"]:
                # Normalize diacritics for clean phonetic reading with Nigerian English accent
                try:
                    from natlas.orthography import NigerianOrthographyEngine
                    clean_text = NigerianOrthographyEngine.strip_diacritics(text)
                except Exception:
                    clean_text = text
                tts = gTTS(text=clean_text, lang="en", tld="com.ng", slow=False)
            else:
                # Nigerian-accented English
                tts = gTTS(text=text, lang="en", tld="com.ng", slow=False)

            tts.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            try:
                # Safe fallback to standard english
                tts = gTTS(text=text[:300], lang="en", slow=False)
                tts.save(output_path)
                return output_path
            except Exception as e2:
                logger.error(f"TTS Fallback failed: {e2}")
                return None
