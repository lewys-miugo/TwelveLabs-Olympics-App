import streamlit as st
from twelvelabs import TwelveLabs
from twelvelabs.models.search import SearchData, GroupByVideoSearchData
import requests
import os
from dotenv import load_dotenv
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import time


load_dotenv()

def keep_alive():
    print("Keep-alive ping executed at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        app_url = os.getenv("STREAMLIT_APP_URL", "http://twelvelabs-olympics-app.streamlit.app/")
        requests.get(app_url, timeout=10)
        print("Successfully pinged the app")
    except Exception as e:
        print(f"Keep-alive ping failed: {str(e)}")


scheduler = BackgroundScheduler()
scheduler.add_job(keep_alive, 'interval', minutes=10)
scheduler.start()

API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.twelvelabs.io/v1.2"

INDEX_ID = os.getenv("INDEX_ID")

client = TwelveLabs(api_key=API_KEY)

page_element = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #ffffff;
}
[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0);
}
[data-testid="stToolbar"] {
    right: 2rem;
    background-image: url("");
    background-size: cover;
}
</style>
"""
st.markdown(page_element, unsafe_allow_html=True)


@st.cache_data
def get_initial_classes():
    return [
        {"name": "AquaticSports", "prompts": ["swimming competition", "diving event", "water polo match", "synchronized swimming", "open water swimming"]},
        {"name": "AthleticEvents", "prompts": ["track and field", "marathon running", "long jump competition", "javelin throw", "high jump event"]},
        {"name": "GymnasticsEvents", "prompts": ["artistic gymnastics", "rhythmic gymnastics", "trampoline gymnastics", "balance beam routine", "floor exercise performance"]},
        {"name": "CombatSports", "prompts": ["boxing match", "judo competition", "wrestling bout", "taekwondo fight", "fencing duel"]},
        {"name": "TeamSports", "prompts": ["basketball game", "volleyball match", "football (soccer) match", "handball game", "field hockey competition"]},
        {"name": "CyclingSports", "prompts": ["road cycling race", "track cycling event", "mountain bike competition", "BMX racing", "cycling time trial"]},
        {"name": "RacquetSports", "prompts": ["tennis match", "badminton game", "table tennis competition", "squash game", "tennis doubles match"]},
        {"name": "RowingAndSailing", "prompts": ["rowing competition", "sailing race", "canoe sprint", "kayak event", "windsurfing competition"]}
    ]
 
def get_custom_classes():
    if 'custom_classes' not in st.session_state:
        st.session_state.custom_classes = []
    return st.session_state.custom_classes

def add_custom_class(name, prompts):
    custom_classes = get_custom_classes()
    custom_classes.append({"name": name, "prompts": prompts})
    st.session_state.custom_classes = custom_classes
    st.session_state.new_class_added = True

def search_videos(selected_prompts, selected_class_names):
    results_by_prompt = {}
    
    for i, prompt in enumerate(selected_prompts):
        try:
            class_name = next((class_name for class_name in selected_class_names 
                              for cls in get_initial_classes() + get_custom_classes() 
                              if cls["name"] == class_name and prompt in cls["prompts"]), "Unknown")
            
            result = client.search.query(
                index_id=INDEX_ID,
                options=["visual", "audio"],
                query_text=prompt,
                group_by="video",
                threshold="medium",
                operator="or",
                page_limit=5,
                sort_option="score"
            )
            
            print(f"Search response for prompt '{prompt}':")
            print(f"  Total results: {result.page_info.total_results}")
            print(f"  Index ID: {result.pool.index_id}")
            print(f"  Total count in pool: {result.pool.total_count}")
            
            if result.data and len(result.data) > 0:
                print(f"  First result type: {type(result.data[0])}")
                if isinstance(result.data[0], GroupByVideoSearchData) and result.data[0].clips:
                    clip = result.data[0].clips[0]
                    print(f"  Sample clip data: score={clip.score}, start={clip.start}, end={clip.end}")
                    print(f"  Confidence type: {type(clip.confidence)}")
                    print(f"  Confidence value: {clip.confidence}")
            
            results_by_prompt[prompt] = {
                "class_name": class_name,
                "result": result
            }
        except Exception as e:
            st.error(f"API Error for prompt '{prompt}': {str(e)}")
            print(f"Exception details: {type(e).__name__}: {str(e)}")
    
    return results_by_prompt

def get_video_urls(video_ids):
    base_url = f"https://api.twelvelabs.io/v1.3/indexes/{INDEX_ID}/videos/{{}}"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    video_urls = {}

    for video_id in video_ids:
        try:
            response = requests.get(base_url.format(video_id), headers=headers)
            response.raise_for_status()
            data = response.json()
            if 'hls' in data and 'video_url' in data['hls']:
                video_urls[video_id] = data['hls']['video_url']
            else:
                st.warning(f"No video URL found for video ID: {video_id}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to get data for video ID: {video_id}. Error: {str(e)}")

    return video_urls

def render_video(video_url, key):
    hls_player = f"""
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <div style="width: 100%; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 10px; position: relative; padding-top: 56.25%;">
        <video id="video-{key}" controls style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain;"></video>
    </div>
    <script>
      var video = document.getElementById('video-{key}');
      var videoSrc = "{video_url}";
      if (Hls.isSupported()) {{
        var hls = new Hls();
        hls.loadSource(videoSrc);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function() {{
          video.pause();
        }});
      }}
      else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
        video.src = videoSrc;
        video.addEventListener('loadedmetadata', function() {{
          video.pause();
        }});
      }}
    </script>
    """
    st.components.v1.html(hls_player, height=400)


def main():

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
    }
    
    .big-font {
        font-size: 48px !important;
        font-weight: 700;
        color: #667eea;
        text-align: center;
        margin-bottom: 40px;
        letter-spacing: -1px;
    }
    
    .subheader {
        font-size: 28px;
        font-weight: 600;
        color: #1a202c;
        margin-top: 30px;
        margin-bottom: 20px;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
        display: inline-block;
    }
    
    .category-header {
        font-size: 24px;
        font-weight: 600;
        color: #2d3748;
        background-color: #f7fafc;
        padding: 20px 25px;
        border-radius: 15px;
        margin: 30px 0 20px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .category-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background-color: #667eea;
    }
    
    .prompt-header {
        font-size: 20px;
        font-weight: 500;
        color: #2d3748;
        background-color: #f0fff4;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 25px 0 15px 0;
        border-left: 4px solid #38a169;
        box-shadow: 0 2px 10px rgba(56, 161, 105, 0.1);
        position: relative;
    }
    
    .prompt-header::before {
        content: '🎯';
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 18px;
    }
    
    /* Multiselect styling */
    .stMultiSelect > label {
        color: #1a202c !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        animation: pulse 2s infinite;
    }
    
    .stMultiSelect > div > div {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        background-color: #ffffff !important;
    }
    
    .stMultiSelect > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stMultiSelect [data-baseweb="select"] {
        color: #1a202c !important;
    }
    
    .stMultiSelect [data-baseweb="select"] > div {
        color: #1a202c !important;
        background-color: #ffffff !important;
    }
    
    /* Text input styling */
    .stTextInput > label {
        color: #1a202c !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        animation: pulse 2s infinite;
    }
    
    .stTextInput > div > div > input {
        color: #1a202c !important;
        background-color: #ffffff !important;
    }
    
    /* Pulse animation */
    @keyframes pulse {
        0% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
            transform: scale(1.02);
        }
        100% {
            opacity: 1;
        }
    }
    
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        background-color: #5a67d8;
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }
    
    .video-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .video-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background-color: #667eea;
    }
    
    .video-meta {
        font-size: 15px;
        color: #4a5568;
        background-color: #f7fafc;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 3px solid #e2e8f0;
        font-weight: 500;
    }
    
    .confidence-high {
        color: #38a169;
        font-weight: 700;
        background-color: rgba(56, 161, 105, 0.1);
        padding: 4px 8px;
        border-radius: 6px;
    }
    
    .confidence-medium {
        color: #d69e2e;
        font-weight: 700;
        background-color: rgba(214, 158, 46, 0.1);
        padding: 4px 8px;
        border-radius: 6px;
    }
    
    .confidence-low {
        color: #e53e3e;
        font-weight: 700;
        background-color: rgba(229, 62, 62, 0.1);
        padding: 4px 8px;
        border-radius: 6px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        background-color: #f7fafc;
        padding: 10px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background: transparent;
        border-radius: 12px;
        padding: 15px 25px;
        font-weight: 600;
        font-size: 16px;
        color: #4a5568;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #667eea;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .custom-container {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .footer-style {
        background-color: #667eea;
        color: white;
        text-align: center;
        padding: 30px;
        border-radius: 20px;
        margin-top: 50px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    .footer-style a {
        color: #ffffff;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        padding: 5px 10px;
        border-radius: 8px;
    }
    
    .footer-style a:hover {
        background-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">🏅 Olympics Classification</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 18px; color: #4a5568; margin-bottom: 40px;">Powered by Twelve Labs AI • Discover Olympic moments with intelligent video search</p>', unsafe_allow_html=True)

    CLASSES = get_initial_classes() + get_custom_classes()
    
    tab1, tab2 = st.tabs([" Search Videos", "➕ Add Custom Class"])
    
    with tab1:
        # st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        st.markdown('<p class="subheader">Search Videos</p>', unsafe_allow_html=True)
        
        class_names = [cls["name"] for cls in CLASSES]
        selected_classes = st.multiselect(
            " Choose Olympic sports categories:", 
            class_names,
            help="Select one or more categories to search for relevant video content"
        )
        
        if st.button(" Search Videos", key="search_button"):
            if selected_classes:
                with st.spinner(" Searching videos..."):
                    selected_prompts = []
                    for cls in CLASSES:
                        if cls["name"] in selected_classes:
                            selected_prompts.extend(cls["prompts"])
                    
                    results_by_prompt = search_videos(selected_prompts, selected_classes)
                    
                    video_ids = set()
                    for prompt_data in results_by_prompt.values():
                        result = prompt_data["result"]
                        for item in result.data:
                            if isinstance(item, GroupByVideoSearchData):
                                video_ids.add(item.id)
                            else:
                                video_ids.add(item.video_id)
                    
                    video_urls = get_video_urls(list(video_ids))
                    
                    if not video_ids:
                        st.warning(" No videos found matching your search criteria.")
                    else:
                        st.success(f" Found {len(video_ids)} unique videos across {len(selected_prompts)} search prompts")
                        
                        results_by_class = {}
                        for prompt, prompt_data in results_by_prompt.items():
                            class_name = prompt_data["class_name"]
                            if class_name not in results_by_class:
                                results_by_class[class_name] = []
                            results_by_class[class_name].append({
                                "prompt": prompt,
                                "result": prompt_data["result"]
                            })
                        
                        for class_name, class_results in results_by_class.items():
                            st.markdown(f'<div class="category-header"> {class_name}</div>', unsafe_allow_html=True)
                            
                            for prompt_result in class_results:
                                prompt = prompt_result["prompt"]
                                result = prompt_result["result"]
                                
                                st.markdown(f'<div class="prompt-header">Results for: "{prompt}"</div>', unsafe_allow_html=True)
                                
                                video_count = 0
                                for item in result.data:
                                    if isinstance(item, GroupByVideoSearchData):
                                        video_id = item.id
                                        if not item.clips:
                                            continue
                                            
                                        with st.expander(f"🎬 Video {video_count+1}: {video_id}", expanded=(video_count == 0)):
                                            st.markdown('<div class="video-card">', unsafe_allow_html=True)
                                            
                                            for i, clip in enumerate(item.clips[:3]):
                                                confidence_class = "confidence-high" if clip.confidence == "high" else "confidence-medium" if clip.confidence == "medium" else "confidence-low"
                                                
                                                # Convert seconds to minutes:seconds format
                                                start_min, start_sec = divmod(int(float(clip.start)), 60)
                                                end_min, end_sec = divmod(int(float(clip.end)), 60)
                                                start_time = f"{start_min}:{start_sec:02d}"
                                                end_time = f"{end_min}:{end_sec:02d}"
                                                
                                                st.markdown(f"""
                                                <div class="video-meta">
                                                    <strong>🎬 Clip {i+1}:</strong> {start_time} - {end_time} | 
                                                    <strong>Score:</strong> {float(clip.score):.1f} | 
                                                    <strong>Confidence:</strong> <span class="{confidence_class}">{clip.confidence}</span>
                                                </div>
                                                """, unsafe_allow_html=True)
                                            
                                            if video_id in video_urls:
                                                render_video(video_urls[video_id], f"{class_name}-{prompt}-{video_count}")
                                            else:
                                                st.warning("⚠️ Video URL not available. Unable to render video.")
                                            
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        video_count += 1
                                        if video_count >= 3:
                                            break
                                    
                                if video_count == 0:
                                    st.info(f"ℹ️ No videos found for prompt: {prompt}")
            else:
                st.warning("⚠️ Please select at least one class.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        # st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        st.markdown('<p class="subheader">Add Custom Class</p>', unsafe_allow_html=True)
        
        custom_class_name = st.text_input("🏷️ Enter custom class name", placeholder="e.g., WinterSports")
        custom_class_prompts = st.text_input("📝 Enter custom class prompts (comma-separated)", placeholder="e.g., skiing, snowboarding, ice skating")
        
        if st.button("➕ Add Custom Class"):
            if custom_class_name and custom_class_prompts:
                prompts_list = [p.strip() for p in custom_class_prompts.split(',')]
                add_custom_class(custom_class_name, prompts_list)
                st.success(f"✅ Custom class '{custom_class_name}' added successfully!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter both class name and prompts.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get('new_class_added', False):
        st.session_state.new_class_added = False
        st.rerun()

if __name__ == "__main__":
    try:
        main()
        
        # Footer with developer info
        st.markdown("---")
        st.markdown("""
        <div class="footer-style">
            <p style="margin: 0; font-size: 16px; font-weight: 600;">
                Built by <strong>Lewys Miugo</strong>
            </p>
            <p style="margin: 15px 0 0 0; font-size: 14px;">
                <a href="https://github.com/lewys-miugo" target="_blank">
                    🐙 GitHub: @lewys-miugo
                </a>
                <span style="margin: 0 10px;">|</span>
                <a href="https://x.com/MiugoW" target="_blank">
                    ✖️ Twitter/X: @MiugoW
                </a>
                <span style="margin: 0 10px;">|</span>
                <a href="https://github.com/lewys-miugo/TwelveLabs-Olympics-App" target="_blank">
                    📂 View Source Code
                </a>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    import atexit
    atexit.register(lambda: scheduler.shutdown())
