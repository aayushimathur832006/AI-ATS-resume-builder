 AI-ATS Resume Builder & Dynamic Portfolio SaaS
 A modern Web SaaS application built with Flask (Python) and Tailwind CSS that helps job seekers craft perfect resumes, optimize them for Applicant Tracking Systems (ATS) using Google Gemini AI, and instantly publish dynamic web portfolios.

 Key Features
 Interactive Resume Builder: Clean, modern UI designed for software engineers and professionals to input personal details, experience, achievements, and projects.

 Gemini-Powered ATS Optimizer: Analyzes resumes against specific Job Descriptions (JD) to generate a compatibility Health Score (0-100) and provides precise, actionable feedback on missing keywords and skills.

 Corporate PDF Resume Export: Directly downloads a beautifully formatted, executive-style PDF resume using ReportLab.

 Dynamic Web Portfolio Publisher: Instantly publishes an interactive web portfolio with dynamic theme color selections (Indigo, Emerald, Rose) that adapt on the fly.

 Persistent Storage: Uses SQLite and SQLAlchemy to securely store user profiles and portfolio data.

 Tech Stack
 Backend: Python, Flask, Flask-SQLAlchemy, Google GenAI SDK (Gemini 2.5-flash)

 Frontend: Tailwind CSS CDN, FontAwesome Icons, Urbanist Google Font

 PDF Generation: ReportLab (Python)

 Database: SQLite

📂 Project Structure
Plaintext
project-root/
│
├── app.py                      # Main Flask application & routing logic
├── instance/
│   └── saas_resume_portfolio.db # SQLite database (auto-generated)
└── templates/
    ├── form_sde.html           # Main user input form & ATS dashboard
    └── live_portfolio.html     # Interactive published portfolio template
⚙️ Setup & Installation
Follow these steps to run the project locally on your machine:

Clone the repository:

Bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME
Install dependencies:
Make sure you have Python installed, then run:

Bash
pip install flask flask-sqlalchemy reportlab google-genai
Configure API Key:
Open app.py and ensure your Google Gemini API key is correctly inserted in the client initialization:

Python
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")
Run the Application:

Bash
python app.py