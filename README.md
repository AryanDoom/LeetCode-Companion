# LeetCode Companion

A powerful Chrome extension designed to enhance your LeetCode experience. Track your solving progress, get personalized problem recommendations, and stay updated with your friends' recent submissions.

## Key Features

*   **Smart Recommendations**: Get problem suggestions tailored to your recently solved topics and interests.
*   **Live Profile Stats**: View your accepted submission counts across different difficulties in real-time.
*   **Friend Activity Tracker**: Keep an eye on what your friends are solving with the built-in "spy" feature.
*   **GraphQL Proxy**: Uses a Python backend to efficiently communicate with LeetCode's internal APIs.

---

## Installation Guide

### 1. Prerequisites
*   Python 3.x installed.
*   Google Chrome or any Chromium based browser.

### 2. Backend Setup
The extension relies on a Flask backend for problem indexing and API proxying.

```bash
# Clone the repository
git clone https://github.com/yourusername/LeetCode-Companion.git
cd LeetCode-Companion

# Install required packages
pip install flask flask-cors requests

# Run the server
python app.py
```
Wait for the message `data loaded good`. The server runs on `http://127.0.0.1:5000`.

### 3. Extension Setup
1.  Open Chrome and go to `chrome://extensions/`.
2.  Toggle on **Developer mode**.
3.  Click **Load unpacked**.
4.  Navigate to and select the `extension` folder in the project directory.

---

## Usage Information

1.  **Launch**: Click the extension icon to open the popup.
2.  **Profile**: Enter your LeetCode username to fetch your current stats.
3.  **Recommendations**: The system uses the `problems.json` dataset and the `simi.py` engine to find problems that match your profile.
4.  **Friends**: Enter a friend's username in the dedicated field to see their latest activity.

> [!TIP]  
> Ensure `app.py` is running before requesting recommendations, as the recommendation engine lives on the backend for maximum speed.
