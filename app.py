import json
import requests
import streamlit as st
from generator import generate_video_content

st.set_page_config(
    page_title="AI Video Studio Pro",
    page_icon="🎬",
    layout="wide"
)

@st.cache_data(show_spinner=False)
def load_scene_image(visual_prompt: str, tone: str, scene_number: int, is_short_format: bool):
    width, height = (720, 1280) if is_short_format else (1280, 720)
    
    tone_styles = {
        "Cinematic": "cinematic movie scene lighting",
        "Professional": "clean corporate minimalist style",
        "Humorous": "vibrant cartoon funny illustration",
        "Educational": "clear infographic diagram style"
    }
    
    style_modifier = tone_styles.get(tone, "cinematic style")
    combined_query = f"{visual_prompt}, {style_modifier}"
    encoded_query = requests.utils.quote(combined_query)
    
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width={width}&height={height}&seed={scene_number * 33}&model=flux&nologo=true"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(pollinations_url, headers=headers, timeout=20)
        if response.status_code == 200 and len(response.content) > 2000:
            return response.content
    except requests.RequestException:
        pass

    fallback_seed = abs(hash(f"{visual_prompt}_{tone}_{scene_number}"))
    fallback_url = f"https://picsum.photos/seed/{fallback_seed}/{width}/{height}"
    
    try:
        response = requests.get(fallback_url, headers=headers, timeout=10)
        if response.status_code == 200 and len(response.content) > 1000:
            return response.content
    except requests.RequestException:
        pass

    return None

st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-size: 18px !important; }
    .stButton > button {
        width: 100%; height: 3.5em; border-radius: 8px;
        background-color: #4F46E5; color: white;
        font-size: 20px !important; font-weight: 700; border: none;
    }
    .main-header { font-size: 42px !important; font-weight: 900; margin-bottom: 10px; }
    .big-text { font-size: 20px !important; line-height: 1.6; }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.title("⚙️ Studio Settings")
    st.write("Configure your video parameters below.")
    st.divider()

    video_topic = st.text_input("Video Topic", placeholder="e.g., Cyberpunk City in 2099")
    col1, col2 = st.columns(2)
    with col1:
        video_duration = st.selectbox("Duration", ["Shorts (9:16)", "5 Minutes", "10+ Minutes"])
    with col2:
        video_tone = st.selectbox("Vibe/Tone", ["Cinematic", "Professional", "Humorous", "Educational"])

    st.divider()
    process_request = st.button("🚀 Generate Content")

st.markdown('<p class="main-header">🎬 AI Video Creator & Visual Studio</p>', unsafe_allow_html=True)
st.caption("Powered by Groq AI and Script-Adaptive AI Visual Generator")

if process_request:
    if not video_topic.strip():
        st.error("Please enter a video topic in the sidebar.")
    else:
        with st.spinner("AI is creating your script, storyboard, and exact matching AI visuals..."):
            output = generate_video_content(video_topic, video_duration, video_tone)

        if "error" in output:
            st.error(f"Execution Error: {output['error']}")
        else:
            tab_storyboard, tab_metadata, tab_export = st.tabs([
                "🎨 Visual Storyboard",
                "🏷️ Titles & SEO",
                "📥 Export Options"
            ])

            with tab_storyboard:
                st.markdown("## 💡 Script Overview")
                video_script = output.get("video_script", {})
                st.info(f"**Hook:** {video_script.get('hook', '')}")
                st.write(f"**Intro:** {video_script.get('intro', '')}")
                st.divider()

                st.markdown("## 🎬 Scene-by-Scene Storyboard")
                storyboard = output.get("storyboard", [])
                is_short = "Shorts" in video_duration or "Reel" in video_duration
                
                if not storyboard:
                    st.warning("No storyboard scenes were generated.")
                else:
                    for scene in storyboard:
                        scene_number = scene.get("scene_number", 1)
                        narration = scene.get("narration", "")
                        visual_prompt = scene.get("visual_prompt", "")

                        st.markdown(f"### 📍 Scene {scene_number}")
                        col_text, col_image = st.columns([1, 1])

                        with col_text:
                            st.markdown("#### 🗣️ Narration / Voiceover")
                            st.markdown(f"<div class='big-text'>{narration}</div>", unsafe_allow_html=True)
                            st.write("")
                            st.markdown("#### 🎨 AI Image Prompt")
                            st.code(visual_prompt, language="text")

                        with col_image:
                            with st.spinner(f"Generating exact AI visual for Scene {scene_number}..."):
                                image_data = load_scene_image(visual_prompt, video_tone, scene_number, is_short)

                            if image_data:
                                st.image(image_data, caption=f"Scene {scene_number} AI Visual ({video_tone})", use_container_width=True)
                            else:
                                st.warning(f"Visual busy for Scene {scene_number}. Click below to retry.")
                                if st.button(f"🔄 Retry Scene {scene_number}", key=f"retry_{scene_number}"):
                                    st.rerun()

                        st.divider()

                st.markdown("#### 🎯 Outro")
                st.write(video_script.get("outro", ""))

            with tab_metadata:
                st.markdown("## 🔥 Viral Title Suggestions")
                viral_titles = output.get("viral_titles", [])
                if viral_titles:
                    for title in viral_titles:
                        st.success(f"• {title}")
                else:
                    st.warning("No title suggestions were generated.")

                st.markdown("## 📝 SEO Description")
                seo_metadata = output.get("seo_metadata", {})
                st.text_area("Description", value=seo_metadata.get("description", ""), height=200)

                st.markdown("## 🏷️ Tags")
                tags = seo_metadata.get("tags", [])
                if tags:
                    formatted_tags = ", ".join([f"`#{tag}`" for tag in tags])
                    st.markdown(formatted_tags)
                else:
                    st.warning("No tags were generated.")

            with tab_export:
                st.markdown("## 📦 Complete Project Package")
                st.json(output)
                formatted_json = json.dumps(output, indent=4, ensure_ascii=False)
                safe_filename = video_topic.strip().replace(" ", "_").lower()
                st.download_button(
                    label="📥 Download Project Package (.JSON)",
                    data=formatted_json,
                    file_name=f"{safe_filename}_studio_package.json",
                    mime="application/json"
                )
else:
    st.markdown("---")
    st.markdown("### Ready to Create Your Video?")
    st.write(
        "Enter your video topic in the sidebar and click **Generate Content** "
        "to generate your script, storyboard, SEO details, and exact matching AI visuals."
    )