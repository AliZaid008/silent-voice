import cv2
import threading
import time
import mediapipe as mp
import os
import math
from collections import Counter

# -------------------------------
# 🗣️ Voice (PowerShell TTS)
# -------------------------------
def speak(text):
    safe_text = text.replace("'", "")
    command = f'PowerShell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{safe_text}\');"'
    os.system(command)

# -------------------------------
# 📐 Math Helper for Thumb Accuracy
# -------------------------------
def get_distance(p1, p2):
    return math.hypot(p1[1] - p2[1], p1[2] - p2[2])

# -------------------------------
# 🤚 MediaPipe Setup
# -------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.75)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# -------------------------------
# ⏱️ Variables
# -------------------------------
last_time = 0
gesture_sequence = []
final_sentence = "Start chatting..."
gesture_buffer = []

# -------------------------------
# 📚 THE MASSIVE 121 COMBO DICTIONARY
# Gestures: Open, Fist, Index, Two, Three, Four, Pinky, Rock, Thumb, Call, Gun
# -------------------------------
phrases_dict = {
    # --- 🖐️ STARTING WITH OPEN ---
    ("Open", "Open"): "I am completely open to that.",
    ("Open", "Fist"): "Goodbye, have a great day!",
    ("Open", "Index"): "Hello my friend, how are you?",
    ("Open", "Two"): "It is really nice to meet you.",
    ("Open", "Three"): "Where are we going today?",
    ("Open", "Four"): "Let's bring everyone together.",
    ("Open", "Pinky"): "Thank you so much!",
    ("Open", "Rock"): "Congratulations!",
    ("Open", "Thumb"): "That is a great job.",
    ("Open", "Call"): "Please call me later.",
    ("Open", "Gun"): "I need to point something out.",

    # --- ✊ STARTING WITH FIST ---
    ("Fist", "Open"): "Please wait a moment, I am thinking.",
    ("Fist", "Fist"): "System cleared.",
    ("Fist", "Index"): "I need some help right now.",
    ("Fist", "Two"): "I am feeling very stressed.",
    ("Fist", "Three"): "Could you repeat that?",
    ("Fist", "Four"): "Stop what you are doing.",
    ("Fist", "Pinky"): "I am sorry, my mistake.",
    ("Fist", "Rock"): "Be careful, that is dangerous.",
    ("Fist", "Thumb"): "I will hold on to this.",
    ("Fist", "Call"): "Emergency, I need assistance.",
    ("Fist", "Gun"): "Do not do that again.",

    # --- ☝️ STARTING WITH INDEX ---
    ("Index", "Open"): "I am doing great, thank you.",
    ("Index", "Fist"): "I did not catch that.",
    ("Index", "Index"): "I have a very important point.",
    ("Index", "Two"): "That sounds like a good idea.",
    ("Index", "Three"): "I have a quick question.",
    ("Index", "Four"): "Let me count the ways.",
    ("Index", "Pinky"): "Excuse me for a second.",
    ("Index", "Rock"): "I am so excited!",
    ("Index", "Thumb"): "I agree with your point.",
    ("Index", "Call"): "Who was that on the phone?",
    ("Index", "Gun"): "Look exactly right there.",

    # --- ✌️ STARTING WITH TWO ---
    ("Two", "Open"): "Yes, I completely agree.",
    ("Two", "Fist"): "Let us take a short break.",
    ("Two", "Index"): "What are we going to do now?",
    ("Two", "Two"): "We are in this together.",
    ("Two", "Three"): "Let's work as a team.",
    ("Two", "Four"): "There are too many options.",
    ("Two", "Pinky"): "I am sorry about the mix up.",
    ("Two", "Rock"): "See you tomorrow.",
    ("Two", "Thumb"): "Two thumbs up from me.",
    ("Two", "Call"): "Let's do a group call.",
    ("Two", "Gun"): "We need to choose one direction.",

    # --- 🤟 STARTING WITH THREE ---
    ("Three", "Open"): "That is fantastic news!",
    ("Three", "Fist"): "I do not understand at all.",
    ("Three", "Index"): "Look at this over here.",
    ("Three", "Two"): "Give me a few minutes.",
    ("Three", "Three"): "Third time is the charm.",
    ("Three", "Four"): "We are almost finished.",
    ("Three", "Pinky"): "No problem at all.",
    ("Three", "Rock"): "Have a safe trip.",
    ("Three", "Thumb"): "I highly recommend this.",
    ("Three", "Call"): "Conference call in five minutes.",
    ("Three", "Gun"): "Let's move to the next item.",

    # --- 🖐️ (Tucked Thumb) STARTING WITH FOUR ---
    ("Four", "Open"): "Everything is perfectly fine.",
    ("Four", "Fist"): "Close the door, please.",
    ("Four", "Index"): "First of all, listen to me.",
    ("Four", "Two"): "I have a couple of thoughts.",
    ("Four", "Three"): "Just a few more things.",
    ("Four", "Four"): "Keep it absolutely square.",
    ("Four", "Pinky"): "I promise I will do it.",
    ("Four", "Rock"): "This is a solid plan.",
    ("Four", "Thumb"): "Everything is under control.",
    ("Four", "Call"): "I will notify everyone.",
    ("Four", "Gun"): "Take a look at the details.",

    # --- 🤙 STARTING WITH PINKY ---
    ("Pinky", "Open"): "I need to use the restroom.",
    ("Pinky", "Fist"): "I am feeling very tired.",
    ("Pinky", "Index"): "I am thirsty, I need water.",
    ("Pinky", "Two"): "I am hungry, let's eat.",
    ("Pinky", "Three"): "What time is it right now?",
    ("Pinky", "Four"): "I need some personal space.",
    ("Pinky", "Pinky"): "Little by little we get there.",
    ("Pinky", "Rock"): "That is a tiny detail.",
    ("Pinky", "Thumb"): "Just a little bit better.",
    ("Pinky", "Call"): "I will call you specifically.",
    ("Pinky", "Gun"): "That is exactly the small issue.",

    # --- 🤘 STARTING WITH ROCK ---
    ("Rock", "Open"): "This is awesome!",
    ("Rock", "Fist"): "Stop doing that right now.",
    ("Rock", "Index"): "Turn up the volume.",
    ("Rock", "Two"): "Turn down the volume.",
    ("Rock", "Three"): "Play some music.",
    ("Rock", "Four"): "Change the song.",
    ("Rock", "Pinky"): "That is totally wild.",
    ("Rock", "Rock"): "Keep rocking on.",
    ("Rock", "Thumb"): "I am feeling very confident.",
    ("Rock", "Call"): "Let's throw a party.",
    ("Rock", "Gun"): "Let's hit the road.",

    # --- 👍 STARTING WITH THUMB ---
    ("Thumb", "Open"): "Good morning everyone.",
    ("Thumb", "Fist"): "I strongly disagree.",
    ("Thumb", "Index"): "I have one positive thought.",
    ("Thumb", "Two"): "That is twice as good.",
    ("Thumb", "Three"): "Excellent work.",
    ("Thumb", "Four"): "Four stars out of five.",
    ("Thumb", "Pinky"): "It is okay, don't worry.",
    ("Thumb", "Rock"): "You absolutely nailed it.",
    ("Thumb", "Thumb"): "Perfect, I love it.",
    ("Thumb", "Call"): "Sounds like a plan, call me.",
    ("Thumb", "Gun"): "You are right on target.",

    # --- 🤙 (Thumb+Pinky) STARTING WITH CALL ---
    ("Call", "Open"): "Let's open communication.",
    ("Call", "Fist"): "Hang up the phone.",
    ("Call", "Index"): "I am waiting for a message.",
    ("Call", "Two"): "Send me a text instead.",
    ("Call", "Three"): "Check your email.",
    ("Call", "Four"): "Broadcast the message to the team.",
    ("Call", "Pinky"): "Just a quick chat.",
    ("Call", "Rock"): "Loud and clear.",
    ("Call", "Thumb"): "Good talking to you.",
    ("Call", "Call"): "Stay in touch.",
    ("Call", "Gun"): "Shoot me an email.",

    # --- 🔫 (Thumb+Index) STARTING WITH GUN ---
    ("Gun", "Open"): "Expand on that idea.",
    ("Gun", "Fist"): "Target locked, let's go.",
    ("Gun", "Index"): "That is exactly the point.",
    ("Gun", "Two"): "Aim for the middle.",
    ("Gun", "Three"): "Triangulate the problem.",
    ("Gun", "Four"): "Look at the big picture.",
    ("Gun", "Pinky"): "Focus on the small stuff.",
    ("Gun", "Rock"): "We hit a roadblock.",
    ("Gun", "Thumb"): "Nailed the objective.",
    ("Gun", "Call"): "Direct line, no waiting.",
    ("Gun", "Gun"): "Right on the money."
}

# -------------------------------
# 🎯 Gesture Detector (STRICT & SMART)
# -------------------------------
def detect_gesture(lmList):
    # To avoid errors, we build an exact array of 5 fingers: [Thumb, Index, Middle, Ring, Pinky]
    fingers = []

    # 1. THUMB (Distance from Thumb Tip to Pinky Knuckle vs Thumb Joint to Pinky Knuckle)
    # This works flawlessly for both left and right hands!
    thumb_tip_dist = get_distance(lmList[4], lmList[17])
    thumb_joint_dist = get_distance(lmList[3], lmList[17])
    if thumb_tip_dist > thumb_joint_dist:
        fingers.append(1) # Thumb is out
    else:
        fingers.append(0) # Thumb is tucked

    # 2. OTHER 4 FINGERS (Compare Tip Y to Knuckle Y)
    for tip_id in [8, 12, 16, 20]:
        # If the tip is higher than the PIP joint (remember Y goes down in OpenCV)
        if lmList[tip_id][2] < lmList[tip_id - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    # -------------------------------
    # 🧩 EXACT BINARY MATCHING
    # -------------------------------
    if fingers == [1, 1, 1, 1, 1] or fingers == [0, 1, 1, 1, 1]: return "Open"
    if fingers == [0, 0, 0, 0, 0]: return "Fist"
    if fingers == [0, 1, 0, 0, 0]: return "Index"
    if fingers == [0, 1, 1, 0, 0]: return "Two"
    if fingers == [0, 1, 1, 1, 0]: return "Three"
    if fingers == [0, 1, 1, 1, 1]: return "Four"
    if fingers == [0, 0, 0, 0, 1]: return "Pinky"
    if fingers == [0, 1, 0, 0, 1]: return "Rock"
    if fingers == [1, 0, 0, 0, 0]: return "Thumb"
    if fingers == [1, 0, 0, 0, 1]: return "Call"
    if fingers == [1, 1, 0, 0, 0]: return "Gun"

    return None

# -------------------------------
# 🔁 Main Loop
# -------------------------------
while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1) # Mirror image for user
    h, w, _ = img.shape

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    current_gesture = None

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            # Build landmark list with pixel coordinates
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                lmList.append([id, int(lm.x * w), int(lm.y * h)])

            if lmList:
                detected = detect_gesture(lmList)

                # 🧠 SMOOTHING BUFFER (Increased to 8 frames for stability)
                if detected:
                    gesture_buffer.append(detected)
                    if len(gesture_buffer) > 8:
                        gesture_buffer.pop(0)

                    # Get the most common gesture in the last 8 frames
                    most_common = Counter(gesture_buffer).most_common(1)[0][0]
                    current_gesture = most_common

                # 🧩 COMBO LOGIC
                current_time = time.time()

                # Require 2 seconds between gestures
                if current_gesture and (current_time - last_time) > 2:
                    
                    # Prevent adding the exact same gesture twice in a row if holding it still
                    if len(gesture_sequence) == 0 or gesture_sequence[-1] != current_gesture:
                        gesture_sequence.append(current_gesture)
                        last_time = current_time

                        # If we have 2 gestures, form a combo!
                        if len(gesture_sequence) == 2:
                            combo = tuple(gesture_sequence)

                            if combo in phrases_dict:
                                final_sentence = phrases_dict[combo]

                                # Speak in background thread
                                threading.Thread(
                                    target=speak,
                                    args=(final_sentence,),
                                    daemon=True
                                ).start()
                            
                            # Clear the sequence after speaking
                            gesture_sequence = []

    # -------------------------------
    # 🎨 UI & Rendering
    # -------------------------------
    # Draw Current Combo State
    cv2.putText(img, f'Combo: {" + ".join(gesture_sequence)}', 
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

    # Draw Text Background Box
    cv2.rectangle(img, (0, h - 80), (w, h), (0, 0, 0), cv2.FILLED)

    # Draw Final Sentence
    cv2.putText(img, final_sentence, 
                (20, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, (255, 255, 255), 2)

    cv2.imshow("Holo Study AI", img)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
