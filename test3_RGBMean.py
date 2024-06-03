import streamlit as st
import numpy as np
import cv2
from PIL import Image
import time
import os
import config
from select_git import run_select
from utils import vid_with_label_1stg, vid_with_label_2stage

def stream_display(response, placeholder):
    text = ''
    for chunk in response:
        if parts := chunk.parts:
            if parts_text := parts[0].text:
                text += parts_text
                placeholder.write(text + "▌")
    return text

def init_messages() -> None:
    st.session_state.messages = []

def undo() -> None:
    st.session_state.messages.pop()

def set_generate(state=True):
    st.session_state.generate = state

st.title("💬 Emotion detector")
st.caption("🚀 A streamlit emotion detector by custom model")

confidence = float(st.sidebar.slider("Select Model Confidence", 25, 100, 40)) / 100
model_selection = st.sidebar.selectbox("Select Model", ["Model 1 (1stg)", "Model 2 (2stage)"])

def main():
    set_generate()
    run = st.checkbox('Run')
    cap = cv2.VideoCapture(0)
    FRAME_WINDOW = st.image([])

    start_time = None
    emotion_detected = None
    dark_warning = st.empty()  # Placeholder for dark warning

    try:
        while run and st.session_state.get("camera_active", True):
            success, frame = cap.read()
            frame = cv2.resize(frame, (640, 480))
            
            if success:
                brightness = np.mean(frame) # Color image mean

                if brightness < 30:  # Threshold for dark frame
                    dark_warning.warning("너무 어둡습니다. 화면이 가려진건 아닌지 확인해주세요.")
                    continue
                else:
                    dark_warning.empty()

                
                if model_selection == "Model 1 (1stg)":
                    img, label = vid_with_label_1stg(frame, confidence, config.YOLO_CUSTOM)
                elif model_selection == "Model 2 (5emo_1stg)" :
                    img, label = vid_with_label_1stg(frame, confidence, config.YOLO_5EMO)
                elif model_selection == "Model 3 (2stg)" :
                    img, label = vid_with_label_2stage(frame, confidence, config.SWINV2)
                elif model_selection == "Model 4 (5emo_2stg)" :
                    img, label = vid_with_label_2stage(frame, confidence, config.SWINV2_5EMO)
                    
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                FRAME_WINDOW.image(img)

                if label and label != 'Happy':
                    if emotion_detected is None:
                        emotion_detected = label
                        start_time = time.time()
                    elif emotion_detected == label and time.time() - start_time >= 1:
                        st.write(f"{label} detected for 1 s")
                        run = False
                        cap.release()
                        run_select()
                        break
                else:
                    emotion_detected = None
                    start_time = None    
            else:
                cap.release()
                break

        else:
            st.write('Stopped')

    except Exception as e:
        st.error(f"Error loading video: {str(e)}")

if __name__ == "__main__":
    main()
