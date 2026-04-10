import requests
import os

# Configuration
API_URL = "http://127.0.0.1:8001/api/upload/"
IMAGE_PATH = r"..\ai\photo_2025-12-27_17-12-56.jpg"

def test_upload():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image not found at {IMAGE_PATH}")
        return

    print(f"Uploading {IMAGE_PATH} to {API_URL}...")
    
    with open(IMAGE_PATH, 'rb') as f:
        files = {'image': f}
        data = {'camera_id': 'TEST_CAM_01'}
        
        try:
            response = requests.post(API_URL, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 201:
                print("Success!")
                print("Response JSON:", response.json())
            else:
                print("Failed!")
                print("Response:", response.text)
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_upload()
