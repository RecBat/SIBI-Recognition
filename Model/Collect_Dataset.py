import cv2
import os
import time

ALPHABETS = [chr(i) for i in range (65, 90) if i != 74]
SUBJECT = "Sinta"
TOTAL = 50
DELAY = 0.5

def collect_dataset():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Can't Open The Camera")
        exit()

    for a in ALPHABETS:
        output = f"dataset/{SUBJECT}/{a}"
        os.makedirs(output, exist_ok=True)

        index = len(os.listdir(output)) + 1
        last_capture = time.time()

        skip = False
        while True:
            success, frame = camera.read()

            if not success:
                print("Can't Receive Frame")
                break

            cv2.putText(frame, f"Alphabet: '{a}' | Index: {index}/{TOTAL}",
                        (10, 30), cv2.FONT_HERSHEY_COMPLEX,
                        0.8, (21, 205, 21), 2)
            
            cv2.putText(frame, "SPACE = Take a picture | Q = Skip",
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_COMPLEX,
                        1, (21, 205, 21), 2)
            
            cv2.imshow("Collecting Dataset", frame)
            
            key = cv2.waitKey(1)
            if key == ord(' '):
                skip = False
                break
            elif key == ord('q') or key == ord('Q'):
                skip = True
                break
        
        if skip == True:
            continue

        while index <= TOTAL:
            success, frame = camera.read()

            if not success:
                print("Can't Receive Frame")
                break

            cv2.putText(frame, f"Alphabet: '{a}' | Index: {index}/{TOTAL}",
                        (10, 30), cv2.FONT_HERSHEY_COMPLEX,
                        0.8, (21, 205, 21), 2)
            
            cv2.putText(frame, "Q = Skip",
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_COMPLEX,
                        1, (21, 205, 21), 2)
            
            cv2.imshow("Collecting Dataset", frame)

            now = time.time()
            if now - last_capture >= DELAY:
                frame_saved = cv2.resize(frame, (224, 224))
                pict_name = f"{a}_{index:03d}.jpg"
                path = os.path.join(output, pict_name)
                cv2.imwrite(path, frame_saved)
                index+=1
                last_capture = now

            key = cv2.waitKey(1)

            if key == ord('q') or key == ord('Q'):
                break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    collect_dataset()