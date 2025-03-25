# AI Bot for University of Ibadan Information
This is an AI-powered chatbot (ai_bot) that provides information about the University of Ibadan (UI), including faculties, departments, and other academic details. It integrates DeepSeek AI to process and generate responses to user queries dynamically.

# Features
✅ University of Ibadan Information – Retrieves faculty and department details.
✅ AI-Powered Responses – Uses DeepSeek AI to generate answers.
✅ User-Friendly Interface – Clean and structured Django-based frontend.
✅ Formatted Output – Converts **bold text** into <b>bold text</b> for display.
✅ Chat History Support – Stores and displays previous conversations.

# Technologies Used
Python 
Django
DeepSeek AI API
HTML, CSS (for frontend styling)

# Installation & Setup
1. Clone the Repository
```git clone https://github.com/simplicityf/percert_ai_bot.git```
```cd ai_bot```

2. Create a Virtual Environment

```
python -m venv venv
source venv/bin/activate  # On Windows: 
venv\Scripts\activate
```
3. Install Dependencies
```pip install -r requirements.txt```

4. Run Migrations

```python manage.py migrate```

5. Start the Server

```python manage.py runserver```
Access the app at http://127.0.0.1:8000/

# Usage
Enter a question about the University of Ibadan.
The chatbot retrieves relevant information or generates an answer using DeepSeek AI.
Responses are displayed in a chatbox, formatted for readability.

# Future Enhancements
🚀 Add more university-related features (e.g., admission requirements, contact info).
🚀 Improve AI understanding & accuracy for better responses.
🚀 Implement database storage for more structured university data.

# Get started with integration
**To register user**

```GET: http://127.0.0.1:8000``` (Home Page, It requires signing in)

```POST: http://127.0.0.1:8000/register```
data_to_send: {
    "username": "username",
    "email": "example@mail.com",
    "password": "pass!52"
}
successful response: {
    "message": "Registration successful. An OTP has been sent to your email for verification."
}

```POST: http://127.0.0.1:8000/verify-email```
data_to_send: {"otp": "otpcode"}
success_response: {"message": "Email verification successful. Your account is now active."}

```POST http://127.0.0.1:8000/login```
data_to_send: {"username": "username", "password": "password"}
success_response: {"token": "", "message": "You are successfully logged in as {{username}}"}
**Save access_token on headers:  Authorization Token access_token**

```GET: http://127.0.0.1:8000/profile```
success_response: {"id": id, "username": "username", "email": "example@mail.com"}

<!-- Update Pofile Note: If user change email, email verification will be sent-->
```POST: http://127.0.0.1:8000/profile/update" ```
data to send {"username": "username", "email": "email@example.com"}
successful_response: {
    "id": id,
    "username": "username",
    "email": "mail@example.com"
}

<!-- To verify change of email OTP -->
``` http://127.0.0.1:8000/profile/verify-email-update ```
data_to_send: {"otp": "otpcode"}
success_response: {
    "message": "Email updated successfully."
}

<!-- Change password (User need to be authenticated) -->
```POST: http://127.0.0.1:8000/change-password ``` **(Note: no data to be sent)**
success_response: { "message": "OTP sent to your email." }
<!-- To verify change password OTP -->
```POST: http://127.0.0.1:8000/verify-change-password```
data_to_send: { "otp" : "otpcode", "new_password": "password" }
success_response: { "message": "Password changed successfully." }


<!-- Forgot Password (Does not requires authentication) -->
``` POST http://127.0.0.1:8000/forgot-password ```
data_to_send: {"email": "email@example.com"}
suceess_response: {"message": "OTP sent to your email."}

``` POST http://127.0.0.1:8000/verify-forgot-password ```
data_to_send: {
    "email": "mail@example.com",
    "otp": "otp code",
    "new_password": "new password"
}

success_response: { "message": "Password reset successfully." }

```POST: http://127.0.0.1:8000/logout```
success_response: {"message": "Logged out successfully."}