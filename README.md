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

