from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load employee data
with open('../data/Employee_Profiles.json', 'r', encoding='utf-8') as f:
    employees = json.load(f)

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({"status": "Backend is running!", "total_employees": len(employees)})

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Return simplified employee list"""
    simple_list = [{
        'id': emp['employee_id'],
        'name': emp['personal_info']['name'],
        'title': emp['employment_info']['job_title'],
        'department': emp['employment_info']['department']
    } for emp in employees]
    return jsonify(simple_list)

@app.route('/api/employee/<emp_id>', methods=['GET'])
def get_employee(emp_id):
    """Get full employee profile"""
    emp = next((e for e in employees if e['employee_id'] == emp_id), None)
    if not emp:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(emp)

@app.route('/api/analyze', methods=['POST'])
def analyze_career():
    """AI-powered career analysis"""
    data = request.json
    emp_id = data.get('employee_id')
    target_role = data.get('target_role', '')
    
    emp = next((e for e in employees if e['employee_id'] == emp_id), None)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Extract employee info
    current_skills = [s['skill_name'] for s in emp['skills']]
    competencies = [f"{c['name']} ({c['level']})" for c in emp['competencies']]
    years_at_psa = 2025 - int(emp['employment_info']['hire_date'][:4])
    
    prompt = f"""You are an expert career advisor at PSA International, a global port operator.

Employee Profile:
- Name: {emp['personal_info']['name']}
- Current Role: {emp['employment_info']['job_title']}
- Department: {emp['employment_info']['department']}
- Years at PSA: {years_at_psa}
- Current Skills: {', '.join(current_skills[:10])}
- Competencies: {', '.join(competencies)}

Target Role: {target_role if target_role else 'Advancement in their current career path'}

Provide a comprehensive career development plan in this EXACT JSON format:
{{
  "readiness_score": 75,
  "summary": "Brief 2-sentence assessment of their readiness and potential",
  "skill_gaps": [
    {{"skill": "Skill Name", "priority": "High", "why": "Why this matters"}},
    {{"skill": "Another Skill", "priority": "Medium", "why": "Reason"}}
  ],
  "learning_path": [
    {{"step": 1, "skill": "First Skill", "action": "Specific action to take", "timeline": "3 months", "resources": ["Course 1", "Certification 2"]}},
    {{"step": 2, "skill": "Second Skill", "action": "Next action", "timeline": "2 months", "resources": ["Workshop", "Book"]}}
  ],
  "internal_opportunities": ["Specific PSA project or role they could pursue", "Another opportunity"],
  "mentorship_match": "Suggest who they should connect with at PSA and why (be specific to their skills)",
  "next_30_days": ["Actionable step 1", "Actionable step 2", "Actionable step 3"]
}}

Guidelines:
- Be specific to maritime/port/logistics/supply chain industry
- Reference PSA's operations (automated terminals, PORTNET, global network)
- Readiness score should be realistic (50-95 range)
- Include 3-5 skill gaps
- Learning path should have 3-4 steps
- Make it actionable and PSA-specific"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        # Try to extract JSON if wrapped in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content)
        return jsonify(result)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)