import os
import sys
import json
import time
import base64
import urllib.request
import urllib.error
import wave
import subprocess
import shutil
import re
from datetime import datetime
import streamlit as st

# Configure page layout & title
st.set_page_config(
    page_title="AI Voiceover Studio — Loghz & Haqiqah",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sleek Dark UI Styling (English UI with RTL Arabic text support)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Cairo:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #080C14;
    color: #F8FAFC;
}

/* Header */
.studio-header {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid rgba(6, 182, 212, 0.25);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.studio-title {
    font-size: 26px;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.studio-subtitle {
    color: #94A3B8;
    font-size: 14px;
    margin-top: 4px;
}

.channel-link {
    background: rgba(6, 182, 212, 0.15);
    color: #06B6D4;
    border: 1px solid rgba(6, 182, 212, 0.4);
    padding: 8px 18px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
    transition: all 0.2s ease;
}

.channel-link:hover {
    background: #06B6D4;
    color: #080C14;
    box-shadow: 0 0 16px rgba(6, 182, 212, 0.4);
}

/* Stat cards */
.stat-box {
    background: #0E1626;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
}

.stat-value {
    font-size: 26px;
    font-weight: 800;
    color: #06B6D4;
    font-family: 'JetBrains Mono', monospace;
}

.stat-label {
    font-size: 12px;
    font-weight: 600;
    color: #94A3B8;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Arabic text area inside English interface */
div[data-testid="stTextArea"] textarea {
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Cairo', sans-serif !important;
    font-size: 16px !important;
    line-height: 1.8 !important;
    background-color: #0B111D !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    color: #F8FAFC !important;
    border-radius: 12px !important;
    padding: 18px !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color: #06B6D4 !important;
    box-shadow: 0 0 0 1px #06B6D4 !important;
}

/* Input title */
div[data-testid="stTextInput"] input {
    background-color: #0B111D !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    color: #F8FAFC !important;
    border-radius: 10px !important;
    font-size: 15px !important;
}

/* Primary Generate Button */
button[data-testid="baseButton-primary"] {
    font-size: 18px !important;
    font-weight: 700 !important;
    padding: 14px 28px !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%) !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(6, 182, 212, 0.35) !important;
    transition: all 0.2s ease !important;
}

button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 26px rgba(6, 182, 212, 0.5) !important;
}

/* Results Box */
.result-card {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(6, 182, 212, 0.35);
    border-radius: 14px;
    padding: 22px;
    margin-top: 24px;
}
</style>
""", unsafe_allow_html=True)

# Application Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# API keys are loaded securely from Streamlit secrets or user input
DEFAULT_API_KEYS = []

def get_configured_keys():
    keys = []
    try:
        if "GEMINI_API_KEYS" in st.secrets:
            sec_keys = st.secrets["GEMINI_API_KEYS"]
            if isinstance(sec_keys, list):
                keys.extend([k.strip() for k in sec_keys if k.strip()])
            elif isinstance(sec_keys, str):
                keys.extend([k.strip() for k in sec_keys.split(",") if k.strip()])
    except Exception:
        pass
    
    if "custom_api_keys" in st.session_state and st.session_state.custom_api_keys:
        custom_list = [k.strip() for k in st.session_state.custom_api_keys.split("\n") if k.strip()]
        if custom_list:
            return custom_list

    return keys if keys else DEFAULT_API_KEYS

# Model Constants
MODEL_NAME = "gemini-3.1-flash-tts-preview"
DEFAULT_VOICE = "Charon"

# Auto-segmentation
def auto_segment_text(raw_text, target_words=105):
    if '---' in raw_text:
        chunks = [c.strip() for c in raw_text.split('---') if c.strip()]
        if chunks:
            return chunks

    paragraphs = [p.strip() for p in raw_text.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [raw_text.strip()]

    segments = []
    current_chunk = []
    current_count = 0

    for p in paragraphs:
        p_words = p.split()
        if not p_words:
            continue

        if len(p_words) > target_words * 1.5:
            sentences = re.split(r'([.!\?؟\n]+)', p)
            sent_buffer = ""
            for s in sentences:
                sent_buffer += s
                if len(sent_buffer.split()) >= target_words:
                    if current_chunk:
                        segments.append("\n\n".join(current_chunk))
                        current_chunk = []
                        current_count = 0
                    segments.append(sent_buffer.strip())
                    sent_buffer = ""
            if sent_buffer.strip():
                current_chunk.append(sent_buffer.strip())
                current_count += len(sent_buffer.split())
        else:
            if current_count + len(p_words) > target_words * 1.3 and current_chunk:
                segments.append("\n\n".join(current_chunk))
                current_chunk = [p]
                current_count = len(p_words)
            else:
                current_chunk.append(p)
                current_count += len(p_words)

    if current_chunk:
        segments.append("\n\n".join(current_chunk))

    return segments if segments else [raw_text.strip()]

# TTS Generation
def generate_single_segment(text_content, out_file, idx, total, api_keys, voice_name=DEFAULT_VOICE):
    prompt_text = (
        "Narrate the following true-crime story in an authentic, natural, raw, everyday Cairo street storyteller accent (لهجة عامية مصرية قاهرية حقيقية زي حكاوي الشارع وسامح سند). "
        "Do NOT speak in Modern Standard Arabic (فصحى) or stiff classical Arabic. "
        "Do NOT sound like a formal news anchor or stiff documentary voice. "
        "Speak like a seasoned Egyptian street investigator or master storyteller sitting with friends at a Cairo cafe late at night, narrating real events with natural street rhythm, dramatic pauses, deep suspense, open relaxed throat, and pure everyday Egyptian colloquial dialect. "
        "Pronounce words naturally as spoken on Cairo streets. "
        "Respond ONLY with the audio. "
        f"Script:\n{text_content}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            }
        }
    }

    max_attempts = len(api_keys) * 2
    for attempt in range(max_attempts):
        api_key = api_keys[attempt % len(api_keys)]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=55) as response:
                res_body = json.loads(response.read().decode('utf-8'))
                candidates = res_body.get("candidates", [])
                if not candidates:
                    continue
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    continue
                inline_data = parts[0].get("inlineData")
                if not inline_data:
                    continue
                b64_data = inline_data.get("data")
                audio_bytes = base64.b64decode(b64_data)

                with wave.open(out_file, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(24000)
                    wav_file.writeframes(audio_bytes)

                dur = len(audio_bytes) / (24000 * 2)
                return dur, None
        except urllib.error.HTTPError:
            time.sleep(1)
        except Exception:
            time.sleep(1)

    return None, "All API keys failed or hit quota limits."

# Dual-Pass Linear EBU R128 Mastering
def clean_simple_master(input_wav, out_wav, out_mp3):
    cmd_meas = [
        "ffmpeg", "-i", input_wav,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    meas = subprocess.run(cmd_meas, stderr=subprocess.PIPE)
    stderr_text = meas.stderr.decode('utf-8', errors='replace')
    start = stderr_text.rfind('{')
    end = stderr_text.rfind('}') + 1
    if start == -1 or end == 0:
        raise RuntimeError("Failed to parse ffmpeg loudnorm measurement")
    stats = json.loads(stderr_text[start:end])

    clean_loud_filter = (
        f"loudnorm=I=-16:TP=-1.5:LRA=11:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:"
        f"measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true"
    )

    subprocess.run([
        "ffmpeg", "-y", "-i", input_wav,
        "-af", clean_loud_filter,
        "-ar", "44100", "-c:a", "pcm_s16le",
        out_wav
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    subprocess.run([
        "ffmpeg", "-y", "-i", out_wav,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        out_mp3
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return stats

# Audio Segment Stitching with 0.5s pause
def stitch_audio_segments(seg_files, out_wav, pause_sec=0.5):
    silence_frames = int(24000 * pause_sec)
    silence_bytes = b'\x00\x00' * silence_frames

    with wave.open(out_wav, "wb") as out_wf:
        out_wf.setnchannels(1)
        out_wf.setsampwidth(2)
        out_wf.setframerate(24000)

        for i, s_file in enumerate(seg_files):
            with wave.open(s_file, "rb") as in_wf:
                frames = in_wf.readframes(in_wf.getnframes())
                out_wf.writeframes(frames)
            if i < len(seg_files) - 1:
                out_wf.writeframes(silence_bytes)

# Sidebar (Minimal)
with st.sidebar:
    st.markdown("### Settings")
    keys_configured = get_configured_keys()
    st.success(f"Active API Keys: **{len(keys_configured)}**")
    
    with st.expander("Custom API Keys (Optional)"):
        st.session_state.custom_api_keys = st.text_area(
            "Paste keys (one per line):",
            value="",
            help="Leave blank to use pre-configured system keys automatically."
        )
    
    st.markdown("---")
    st.caption("• Voice: **Charon** (Gemini 3.1 Flash TTS)")
    st.caption("• Style: **Sameh Sanad Egyptian Persona**")
    st.caption("• Mastering: **EBU R128 (-16 LUFS / TP -1.5 dB)**")

# Header
st.markdown("""
<div class="studio-header">
    <div>
        <div class="studio-title">
            <span>🎙️ AI Voiceover Studio</span>
        </div>
        <div class="studio-subtitle">
            Automated Egyptian Storyteller Voiceover Engine for <b>لغز وحقيقة</b>
        </div>
    </div>
    <div>
        <a href="https://www.youtube.com/@%D9%84%D8%BA%D8%B2%D9%88%D8%AD%D9%82%D9%8A%D9%82%D9%87" target="_blank" class="channel-link">
            YouTube Channel ↗
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# 1. Inputs
ep_title = st.text_input("Episode Title:", value="", placeholder="e.g. The Mysterious Case of...")

script_text = st.text_area(
    "Script (Paste your Arabic text here):",
    height=340,
    placeholder="الصق نص القصة هنا بالعامية المصرية... (يمكنك استخدام '---' للفصل بين المشاهد يدوياً)"
)

# 2. Live Stat Counters
words = script_text.split() if script_text else []
word_count = len(words)
est_minutes = word_count / 125.0
est_min_floor = int(est_minutes)
est_sec = int((est_minutes - est_min_floor) * 60)
detected_segments = auto_segment_text(script_text, target_words=105) if script_text.strip() else []
num_segments = len(detected_segments)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-value">{word_count}</div>
        <div class="stat-label">Words</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-value">{est_min_floor}:{est_sec:02d}</div>
        <div class="stat-label">Est. Duration</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-value">{num_segments}</div>
        <div class="stat-label">Story Beats</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-value">Charon</div>
        <div class="stat-label">Voice Model</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# 3. Main Action Button
generate_clicked = st.button("🚀 Generate Voiceover & Master Audio", type="primary", use_container_width=True)

# 4. Generation & Progress Tracking
if generate_clicked:
    if not script_text.strip():
        st.error("Please paste your script text first!")
    else:
        api_keys = get_configured_keys()
        if not api_keys:
            st.error("No valid Gemini API keys found. Please add a key in the sidebar.")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title_clean = ep_title.strip() if ep_title.strip() else f"episode_{timestamp}"
            safe_slug = re.sub(r'[\s/\\:*?"<>|]+', '_', title_clean)[:40]
            ep_id = f"{safe_slug}_{timestamp}"
            ep_dir = os.path.join(OUTPUT_DIR, ep_id)
            seg_dir = os.path.join(ep_dir, "segments")
            os.makedirs(seg_dir, exist_ok=True)

            raw_wav = os.path.join(ep_dir, "raw_stitched.wav")
            master_wav = os.path.join(ep_dir, f"{safe_slug}_mastered.wav")
            master_mp3 = os.path.join(ep_dir, f"{safe_slug}_mastered.mp3")

            status_tracker = st.status("🎬 Producing Voiceover & Audio Master...", expanded=True)
            progress_bar = st.progress(0.0)

            with status_tracker:
                # Step 1: Segmentation
                st.write("✂️ Dividing script into balanced story beats...")
                segments = auto_segment_text(script_text, target_words=105)
                total_segs = len(segments)
                time.sleep(0.3)

                # Step 2: Generation Loop
                st.write(f"🎙️ Generating {total_segs} audio segments via Gemini 3.1 Flash TTS (Charon)...")
                seg_files = []
                failed = False

                for i, seg_text in enumerate(segments):
                    seg_file = os.path.join(seg_dir, f"seg_{i+1:03d}.wav")
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;• Segment {i+1} of {total_segs}...")
                    dur, err = generate_single_segment(seg_text, seg_file, i, total_segs, api_keys, DEFAULT_VOICE)
                    if dur is None:
                        st.error(f"Failed on segment {i+1}: {err}")
                        failed = True
                        break
                    seg_files.append(seg_file)
                    progress_bar.progress((i + 1) / (total_segs + 2))

                if not failed and len(seg_files) == total_segs:
                    # Step 3: Stitching
                    st.write("🧩 Stitching segments with 0.5s storytelling pauses...")
                    stitch_audio_segments(seg_files, raw_wav, pause_sec=0.5)
                    progress_bar.progress((total_segs + 1) / (total_segs + 2))

                    # Step 4: Mastering
                    st.write("🎚️ Applying dual-pass linear EBU R128 mastering (-16.0 LUFS / TP -1.5 dBTP)...")
                    if shutil.which("ffmpeg"):
                        stats = clean_simple_master(raw_wav, master_wav, master_mp3)
                        st.write("✨ Encoding Studio MP3 (320 kbps)...")
                    else:
                        shutil.copyfile(raw_wav, master_wav)
                        master_mp3 = None
                        st.warning("FFmpeg not detected. Raw WAV audio exported.")

                    progress_bar.progress(1.0)
                    status_tracker.update(label="🎉 Production Complete!", state="complete", expanded=False)

                    # Output Presentation
                    st.balloons()
                    st.success(f"Voiceover successfully generated & mastered for: **{title_clean}**")

                    audio_file = master_mp3 if (master_mp3 and os.path.exists(master_mp3)) else master_wav

                    st.markdown("### 🎧 Listen to Studio Master:")
                    with open(audio_file, "rb") as f:
                        audio_data = f.read()

                    mime = "audio/mp3" if audio_file.endswith(".mp3") else "audio/wav"
                    st.audio(audio_data, format=mime)

                    # Download Buttons
                    d1, d2 = st.columns(2)
                    with d1:
                        if master_mp3 and os.path.exists(master_mp3):
                            with open(master_mp3, "rb") as f_mp3:
                                st.download_button(
                                    label="📥 Download Studio MP3 (320 kbps)",
                                    data=f_mp3.read(),
                                    file_name=f"{safe_slug}_mastered.mp3",
                                    mime="audio/mpeg",
                                    use_container_width=True
                                )
                    with d2:
                        with open(master_wav, "rb") as f_wav:
                            st.download_button(
                                label="📥 Download Master WAV (44.1 kHz 16-bit)",
                                data=f_wav.read(),
                                file_name=f"{safe_slug}_mastered.wav",
                                mime="audio/wav",
                                use_container_width=True
                            )
