import os
import uuid
from app.asr.transcriber import ASRTranscriber
from app.llm.advisor import AgriculturalAdvisor
from app.rag.retriever import KnowledgeRetriever
from app.tts.speaker import TTSSpeaker
import logging

logger = logging.getLogger(__name__)

class VoicePipeline:
    def __init__(self):
        self.transcriber = ASRTranscriber()
        self.retriever = KnowledgeRetriever()
        self.advisor = AgriculturalAdvisor()
        self.speaker = TTSSpeaker()

    def process_audio(self, audio_data, sampling_rate=16000) -> dict:
        """
        Process incoming audio: ASR -> RAG -> LLM -> TTS
        """
        logger.info("Starting voice pipeline processing...")
        
        # 1. ASR
        transcription_result = self.transcriber.transcribe(audio_data, sampling_rate)
        text = transcription_result["text"]
        detected_lang = transcription_result["language"]
        
        logger.info(f"Transcribed ({detected_lang}): {text}")
        
        if not text:
            return {"error": "Could not understand audio."}

        # 2. RAG Retrieval
        context = self.retriever.retrieve(text)
        
        # 3. LLM Advisor
        advice_text = self.advisor.get_advice(query=text, context=context, language=detected_lang)
        logger.info(f"Advice generated: {advice_text}")
        
        # 4. TTS
        output_filename = f"static/outputs/response_{uuid.uuid4().hex}.mp3"
        os.makedirs("static/outputs", exist_ok=True)
        
        audio_path = self.speaker.synthesize(advice_text, detected_lang, output_filename)
        
        return {
            "transcript": text,
            "language": detected_lang,
            "advice": advice_text,
            "audio_url": f"/{audio_path}" if audio_path else None
        }

    def process_text(self, text: str, language: str = "ha") -> dict:
        """
        Process text query directly (sample queries or typed questions): RAG -> LLM -> TTS
        """
        logger.info(f"Starting text pipeline for ({language}): {text}")
        context = self.retriever.retrieve(text)
        advice_text = self.advisor.get_advice(query=text, context=context, language=language)
        
        output_filename = f"static/outputs/response_{uuid.uuid4().hex}.mp3"
        os.makedirs("static/outputs", exist_ok=True)
        audio_path = self.speaker.synthesize(advice_text, language, output_filename)
        
        return {
            "transcript": text,
            "language": language,
            "advice": advice_text,
            "audio_url": f"/{audio_path}" if audio_path else None
        }
