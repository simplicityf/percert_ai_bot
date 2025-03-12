import requests
from django.shortcuts import render
from openai import OpenAI
from django.contrib.auth.decorators import login_required
import os
import re
from .keyword_mapping import keyword_mapping

# API Details
HOSTED_QA_API = os.getenv("HOSTED_QA_API")
API_KEY = os.getenv("API_KEY")
CSE_ID = os.getenv("CSE_ID")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_KEY"),
    base_url="https://api.deepseek.com",
)

chat_history = []

# Keyword Mapping
def fetch_hosted_answer(question):
    """Fetch an answer from the hosted Q&A API and format it properly."""
    try:
        response = requests.get(f"{HOSTED_QA_API}?q={question}")
        if response.status_code == 200:
            data = response.json()
            if "answer" in data:
                return format_nested_answer(data["answer"])
    except Exception as e:
        print("Error fetching hosted Q&A:", e)
    return None


def format_nested_answer(answer):
    """Format nested dictionaries and lists into a readable HTML-friendly string."""
    if isinstance(answer, str):
        return re.sub(r"\*\*(.*?)\*\*", r"\1", answer)  # Removes ** but keeps text
    elif isinstance(answer, list):
        return "\n".join(format_nested_answer(item) if not isinstance(item, dict) else format_nested_answer(item) for item in answer)
    elif isinstance(answer, dict):
        return "\n".join(f"{key}: {format_nested_answer(value)}" for key, value in answer.items())
    return str(answer)


def search_google(query, site=None):
    """Fetch results from Google Search API with optional site restriction."""
    search_query = f"site:{site} {query}" if site else query
    url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&cx={CSE_ID}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        return "Google Search API error."
    
    data = response.json()
    results = [f"{item.get('title', 'No title')}\n{item.get('link', '#')}\n\n{item.get('snippet', '').strip()}\n---"
               for item in data.get("items", [])[:3]]
    return "\n".join(results) if results else "No relevant information found."


def match_keywords(question):
    """Find the best matching keyword category for a given question."""
    question = question.lower()
    for category, keywords in keyword_mapping.items():
        for keyword in keywords:
            # Remove trailing 's' if it exists to cover both singular and plural forms.
            base_keyword = keyword.lower().rstrip('s')
            pattern = rf"\b{re.escape(base_keyword)}s?\b"
            if re.search(pattern, question, re.IGNORECASE):
                return category
    return None

@login_required
def chat(request):
    """Multi-round chat with DeepSeek."""
    global chat_history
    username = request.user

    if request.method == 'POST':
        user_message = request.POST.get('question')
        if user_message:
            chat_history.append({'role': 'user', 'content': user_message})

            # Check for an exact match in the hosted Q&A API
            hosted_answer = fetch_hosted_answer(user_message)
            if hosted_answer:
                ai_message = f"[📌 Answer from Knowledge Base:]\n{hosted_answer}"
            else:
                # Keyword-based matching
                matched_category = match_keywords(user_message)
                if matched_category:
                    hosted_answer = fetch_hosted_answer(matched_category)
                    
                    if hosted_answer:
                        ai_message = f"[📌 Answer from Knowledge Base:]\n{hosted_answer}"
                    else:
                        ai_message = f"[🔎 Keyword Match: {matched_category}]\nNo direct answer found."
                else:
                    # Google Search fallback
                    google_results = search_google(user_message, site="ui.edu.ng") if "university of ibadan" in user_message.lower() else search_google(user_message)
                    ai_message = f"[🔎 Latest Update:]\n{google_results}" if google_results and "No relevant information found" not in google_results else None
                    
                    # DeepSeek AI fallback
                    if not ai_message:
                        response = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=chat_history,
                            temperature=0.7,
                            stream=False
                        )
                        ai_message = response.choices[0].message.content.strip()

            chat_history.append({'role': 'assistant', 'content': ai_message})
        
        return render(request, 'index.html', {"chat_history": chat_history, "username": username})

    return render(request, 'index.html', {"chat_history": chat_history, "username": username})
