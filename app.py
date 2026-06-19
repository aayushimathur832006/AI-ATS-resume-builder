import os
from dotenv import load_dotenv
import re
from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


from google import genai
from google.genai import types


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saas_resume_portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    summary = db.Column(db.Text, nullable=False)
    skills = db.Column(db.String(200), nullable=False)
    exp_company = db.Column(db.String(100))
    exp_role = db.Column(db.String(100))
    exp_responsibilities = db.Column(db.Text)
    proj_title = db.Column(db.String(100))
    proj_desc = db.Column(db.Text)
    proj_link = db.Column(db.String(200))
    selected_theme = db.Column(db.String(50), default='indigo')

with app.app_context():
    db.create_all()



@app.route('/')
def index():
    empty_portfolio = {
        "name": "", "email": "", "phone": "", "summary": "", 
        "skills": "", "exp_company": "", "exp_role": "", 
        "exp_responsibilities": "", "proj_title": "", 
        "proj_desc": "", "proj_link": "", "selected_theme": "indigo"
    }
    return render_template('form_sde.html', portfolio=empty_portfolio)


@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    jd_text = request.form.get('jd_text', '')
    skills_input = request.form.get('skills', '')
    exp_resp = request.form.get('exp_responsibilities', '')
    proj_desc = request.form.get('proj_desc', '')
    summary = request.form.get('summary', '')
    
    
    resume_data = f"""
    Summary: {summary}
    Skills: {skills_input}
    Experience Details: {exp_resp}
    Project Details: {proj_desc}
    """
    
    final_score = 70
    feedback = ["Resume evaluated successfully."]
    
    try:
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) and Technical Recruiter.
        Analyze the following Job Description and Candidate Resume details.
        
        Job Description:
        {jd_text}
        
        Candidate Resume Details:
        {resume_data}
        
        Tasks:
        1. Calculate an ATS compatibility score from 0 to 100 based on keyword match, required skills, and relevancy.
        2. Identify missing key skills or qualifications required in the JD but absent in the resume.
        3. Give precise, actionable feedback on what is missing and how to improve.
        
        Provide the response strictly in the following JSON format:
        {{
            "score": <integer score 0-100>,
            "feedback": ["point 1", "point 2", "point 3"]
        }}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        import json
        ai_output = json.loads(response.text)
        final_score = ai_output.get("score", 70)
        feedback = ai_output.get("feedback", ["No feedback provided."])
        
    except Exception as e:
        print(f"Gemini API Error fallback triggered: {e}")
        feedback.append("AI analysis parsing error fallback executed. Please verify API configuration.")

    analysis_result = {
        "score": final_score,
        "feedback": feedback
    }

    preview_portfolio = {
        "name": request.form.get('name'),
        "email": request.form.get('email'),
        "phone": request.form.get('phone'),
        "summary": request.form.get('summary'),
        "skills": request.form.get('skills'),
        "exp_company": request.form.get('exp_company'),
        "exp_role": request.form.get('exp_role'),
        "exp_responsibilities": request.form.get('exp_responsibilities'),
        "proj_title": request.form.get('proj_title'),
        "proj_desc": request.form.get('proj_desc'),
        "proj_link": request.form.get('proj_link'),
        "selected_theme": request.form.get('selected_theme', 'indigo')
    }
    
    return render_template('form_sde.html', analysis=analysis_result, portfolio=preview_portfolio)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    name = request.form.get('name', 'Portfolio_User')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    summary = request.form.get('summary', '')
    skills = request.form.get('skills', '')
    exp_company = request.form.get('exp_company', '')
    exp_role = request.form.get('exp_role', '')
    exp_resp = request.form.get('exp_responsibilities', '')
    proj_title = request.form.get('proj_title', '')
    proj_desc = request.form.get('proj_desc', '')
    proj_link = request.form.get('proj_link', '')

    pdf_filename = f"{name.replace(' ', '_')}_Professional_Resume.pdf"
    
  
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=letter, 
        rightMargin=45, 
        leftMargin=45, 
        topMargin=45, 
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
  
    primary_color = colors.HexColor('#2563EB')
    text_dark = colors.HexColor('#0F172A')    
    text_muted = colors.HexColor('#475569')  
    line_color = colors.HexColor('#CBD5E1')   
  
    name_style = ParagraphStyle(
        'FullName', 
        parent=styles['Heading1'], 
        fontSize=26, 
        leading=30, 
        textColor=primary_color,
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    contact_style = ParagraphStyle(
        'ContactInfo', 
        parent=styles['Normal'], 
        fontSize=10, 
        leading=14, 
        textColor=text_muted,
        alignment=0 # Left aligned
    )
    h2_style = ParagraphStyle(
        'SectionHeader', 
        parent=styles['Heading2'], 
        fontSize=13, 
        leading=17, 
        textColor=text_dark, 
        fontName='Helvetica-Bold',
        spaceBefore=16, 
        spaceAfter=8,
        borderPadding=(0,0,2,0),
        borderColour=line_color,
        borderWidth=1
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', 
        parent=styles['Normal'], 
        fontSize=10.5, 
        leading=16, 
        textColor=text_dark,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    story = []
    
  
    story.append(Paragraph(name, name_style))
    contact_text = f"<b>Email:</b> {email} &nbsp;|&nbsp; <b>Phone:</b> {phone} &nbsp;|&nbsp; <b>Portfolio/Source:</b> {proj_link}"
    story.append(Paragraph(contact_text, contact_style))
    story.append(Spacer(1, 12))
    
  
    if summary:
        story.append(Paragraph("Professional Summary", h2_style))
        story.append(Paragraph(summary, body_style))
    

    if skills:
        story.append(Paragraph("Technical Competencies & Skills", h2_style))
        formatted_skills = skills.replace(",", " &bull; ").strip()
        story.append(Paragraph(formatted_skills, body_style))
        
   
    if exp_company or exp_role or exp_resp:
        story.append(Paragraph("Professional Experience", h2_style))
        exp_header = f"<b>{exp_role}</b> &nbsp;&mdash;&nbsp; <font color='#2563EB'><b>{exp_company}</b></font>"
        story.append(Paragraph(exp_header, body_style))
        
        for resp in exp_resp.split('\n'):
            if resp.strip():
                story.append(Paragraph(f"&bull; {resp.strip()}", bullet_style))

    # Projects Section
    if proj_title or proj_desc:
        story.append(Paragraph("Projects & Technical Achievements", h2_style))
        proj_header = f"<b>{proj_title}</b>"
        story.append(Paragraph(proj_header, body_style))
        
        for desc in proj_desc.split('\n'):
            if desc.strip():
                story.append(Paragraph(f"&bull; {desc.strip()}", bullet_style))
        
        if proj_link:
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<b>Live Codebase/Deployment:</b> <font color='#2563EB'>{proj_link}</font>", body_style))

   
    doc.build(story)
    
    return send_file(pdf_filename, as_attachment=True)

@app.route('/save-portfolio', methods=['POST'])
def save_portfolio():
    name = request.form.get('name')
    username = name.lower().replace(" ", "") + "123"
    
    existing_user = UserProfile.query.filter_by(username=username).first()
    
    if existing_user:
       
        existing_user.email = request.form.get('email')
        existing_user.phone = request.form.get('phone')
        existing_user.summary = request.form.get('summary')
        existing_user.skills = request.form.get('skills')
        existing_user.exp_company = request.form.get('exp_company')
        existing_user.exp_role = request.form.get('exp_role')
        existing_user.exp_responsibilities = request.form.get('exp_responsibilities')
        existing_user.proj_title = request.form.get('proj_title')
        existing_user.proj_desc = request.form.get('proj_desc')
        existing_user.proj_link = request.form.get('proj_link')
        existing_user.selected_theme = request.form.get('selected_theme', 'indigo')
        db.session.commit()
    else:
        new_profile = UserProfile(
            username=username,
            name=name,
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            summary=request.form.get('summary'),
            skills=request.form.get('skills'),
            exp_company=request.form.get('exp_company'),
            exp_role=request.form.get('exp_role'),
            exp_responsibilities=request.form.get('exp_responsibilities'),
            proj_title=request.form.get('proj_title'),
            proj_desc=request.form.get('proj_desc'),
            proj_link=request.form.get('proj_link'),
            selected_theme=request.form.get('selected_theme', 'indigo')
        )
        db.session.add(new_profile)
        db.session.commit()
    
    return redirect(url_for('show_portfolio', username=username))

@app.route('/p/<username>')
def show_portfolio(username):
    user_data = UserProfile.query.filter_by(username=username).first_or_404()
    return render_template('live_portfolio.html', portfolio=user_data)

if __name__ == '__main__':
    app.run(debug=True)