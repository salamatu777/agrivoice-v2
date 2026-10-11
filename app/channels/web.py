import gradio as gr
from app.voice_pipeline import VoicePipeline
import numpy as np

def create_demo():
    pipeline = VoicePipeline()

    def process(audio_filepath):
        if not audio_filepath:
            return "No audio provided", "No advice", None
            
        import librosa
        audio_data, sr = librosa.load(audio_filepath, sr=16000)
        result = pipeline.process_audio(audio_data, sr)
        
        return result.get("transcript", ""), result.get("advice", ""), result.get("audio_url", "").lstrip('/')

    with gr.Blocks(title="AgriVoice") as demo:
        gr.Markdown("# AgriVoice: Voice-First Agricultural Advisor")
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(type="filepath", label="Record your question (Hausa, Yoruba, Igbo, English)")
                btn = gr.Button("Get Advice")
                
            with gr.Column():
                transcript_out = gr.Textbox(label="Transcript")
                advice_out = gr.Textbox(label="Advice")
                audio_out = gr.Audio(label="Voice Response")
                
        btn.click(fn=process, inputs=audio_input, outputs=[transcript_out, advice_out, audio_out])
        
    return demo

if __name__ == "__main__":
    demo = create_demo()
    demo.launch()
