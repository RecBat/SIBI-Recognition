from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import mediapipe as mp
import numpy as np
import joblib
import cv2
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

KNN_model = joblib.load("KNN_Model.pkl")
RF_model = joblib.load("RF_Model.pkl")
ensemble_model = joblib.load("Ensemble_Model.pkl")
label_encode = joblib.load("Label_Encoder.pkl")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, 
                       max_num_hands=1, min_detection_confidence=0.3)

def normalize_lm(feature):
  lm = np.array(feature).reshape(21,3)
  wrist = lm[0]
  lm = lm - wrist
  scale = np.max(np.abs(lm))
  if scale > 0:
    lm = lm / scale
  return lm.flatten().tolist()

def extract_landmarks(img):
    img = cv2.resize(img, (224,224))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    
    if result.multi_hand_landmarks:
        landmarks = result.multi_hand_landmarks[0]

        features = []
        for lm in landmarks.landmark:
          features.extend([lm.x, lm.y, lm.z])

        features = normalize_lm(features)
        return np.array(features).reshape(1, -1)
    return None

@app.post("/predict")
async def predict(file: UploadFile=File(...)):
   contents = await file.read()
   array = np.frombuffer(contents, np.uint8)
   img = cv2.imdecode(array, cv2.IMREAD_COLOR)

   features = extract_landmarks(img)
   if features is None:
      return {"success": False, "message": "Tangan tidak terdeteksi"}
   
   start = time.time()
   knn_pred = label_encode.inverse_transform(KNN_model.predict(features))[0]
   knn_time = round((time.time() - start) * 1000, 2)
   knn_conf = round(max(KNN_model.predict_proba(features)[0]) * 100, 2)

   start = time.time()
   rf_pred = label_encode.inverse_transform(RF_model.predict(features))[0]
   rf_time = round((time.time() - start) * 1000, 2)
   rf_conf = round(max(RF_model.predict_proba(features)[0]) * 100, 2)

   start = time.time()
   ensemble_pred = label_encode.inverse_transform(ensemble_model.predict(features))[0]
   ensemble_time = round((time.time() - start) * 1000, 2)
   ensemble_conf = round(max(ensemble_model.predict_proba(features)[0]) * 100, 2)

   return {
      "success" : True,
      "KNN_Model" : {"label" : knn_pred, "confidence" : knn_conf, "time_ms" : knn_time},
      "RF_Model" : {"label" : rf_pred, "confidence" : rf_conf, "time_ms" : rf_time},
      "Ensemble_Model" : {"label" : ensemble_pred, "confidence" : ensemble_conf, "time_ms" : ensemble_time}
   }

@app.get("/")
def root():
   return {"message" : "SIBI API is running"}