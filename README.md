# Smart-Login

## Overview
Smart-Login is a modern web application that provides secure user authentication using both password and facial recognition. Designed for HR and IT teams, it offers a seamless and user-friendly experience for onboarding and login, ensuring enhanced security and compliance.

## Features
- **User Signup:** Register with username, password, email, and a live photo (face capture).
- **Login:** Authenticate using password and live face capture for two-factor security.
- **Dashboard:** Personalized dashboard after login.
- **Session Management:** Secure sessions with login/logout functionality.
- **Responsive UI:** Beautiful, modern interface for signup, login, and dashboard.
- **Email Validation:** Ensures only valid email addresses are accepted.
- **Image Quality:** High-quality image processing for reliable face matching.
- **HR Friendly:** Easy onboarding, clear error messages, and intuitive navigation.

## Technology Stack
- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript (with camera integration)
- **Image Processing:** Pillow, NumPy
- **Security:** Password hashing (Werkzeug)

## Getting Started
### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation
1. **Clone the repository:**
   ```powershell
   git clone <repository-url>
   cd Smart-Login
   ```
2. **Install dependencies:**
   ```powershell
   pip install flask pillow numpy werkzeug
   ```
3. **Run the application:**
   ```powershell
   python dev.py
   ```
4. **Access the app:**
   Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Usage
- **Sign Up:**
  1. Go to `/signup`.
  2. Fill in your details and capture a live photo using your device camera.
  3. Submit the form to create your account.
- **Login:**
  1. Go to `/login`.
  2. Enter your username and password, then capture a live photo.
  3. Submit to authenticate and access your dashboard.
- **Dashboard:**
  - View your profile and access additional features.
- **Logout:**
  - Click the logout button to securely end your session.

## Folder Structure
```
Smart-Login/
├── dev.py
├── README.md
├── templates/
│   ├── signup.html
│   ├── login.html
│   └── dashboard.html
├── uploads/
```

## Security & Privacy
- Passwords are securely hashed.
- Face images are stored locally and compared securely.
- No user data is shared externally.
- HR teams can onboard users with confidence.

## Customization
- Update UI templates in the `templates/` folder for branding.
- Adjust image match threshold in `dev.py` for stricter/looser face matching.

## Troubleshooting
- **Camera Issues:** Ensure your device camera is enabled and accessible.
- **Dependency Errors:** Reinstall required Python packages.
- **Port Issues:** Change the Flask port in `dev.py` if needed.

## Contact & Support
For questions, support, or HR onboarding assistance, please contact:
- **Project Owner:** [Ganesh Prasad Panda]
- **Email:** [roy862452@gmail.com]


---
**Smart-Login is designed to make secure authentication simple and accessible for everyone. HR teams can easily onboard new users and ensure compliance with modern security standards.**
