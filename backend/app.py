from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# TEMPORARY - For testing only! Remove before pushing to GitHub!
TEST_API_KEY = None  # Set to None to use .env, or paste key as string for testing

# Load employee data
with open('../data/Employee_Profiles.json', 'r', encoding='utf-8') as f:
    employees = json.load(f)

# Load skills taxonomy
with open('../data/skills_taxonomy.json', 'r', encoding='utf-8') as f:
    skills_taxonomy = json.load(f)

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        "status": "Backend is running!", 
        "total_employees": len(employees),
        "total_skills": len(skills_taxonomy)
    })

@app.route('/api/debug', methods=['GET'])
def debug():
    """Debug endpoint to check Azure config"""
    api_key = TEST_API_KEY if TEST_API_KEY else os.getenv("AZURE_OPENAI_KEY")
    return jsonify({
        "using_test_key": bool(TEST_API_KEY),
        "has_key": bool(api_key),
        "key_length": len(api_key) if api_key else 0,
        "key_preview": (api_key[:8] + "...") if api_key else "NOT SET",
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION")
    })

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

@app.route('/api/skills-taxonomy', methods=['GET'])
def get_skills_taxonomy():
    """Get all available skills in PSA"""
    return jsonify(skills_taxonomy)

@app.route('/api/match-skills/<emp_id>', methods=['GET'])
def match_skills(emp_id):
    """Match employee skills against full PSA taxonomy"""
    emp = next((e for e in employees if e['employee_id'] == emp_id), None)
    if not emp:
        return jsonify({'error': 'Not found'}), 404
    
    # Get employee's current skills
    current_skills = [s['skill_name'].lower() for s in emp['skills']]
    current_functions = list(set([s['function_area'].lower() for s in emp['skills']]))
    
    # Build skills map
    all_skills = {}
    for skill in skills_taxonomy:
        func = skill['Function / Unit / Skill']
        spec = skill['Specialisation / Unit']
        
        if func not in all_skills:
            all_skills[func] = []
        all_skills[func].append(spec)
    
    # Recommend related skills in their domain
    recommendations = []
    for func in current_functions:
        for skill_func in all_skills.keys():
            # Check if this function area is related
            if any(word in skill_func.lower() for word in func.lower().split()):
                for spec in all_skills[skill_func]:
                    # Only recommend if they don't have it
                    if spec.lower() not in ' '.join(current_skills).lower():
                        recommendations.append({
                            'function': skill_func,
                            'skill': spec,
                            'relevance': 'high'
                        })
    
    # Remove duplicates
    seen = set()
    unique_recs = []
    for rec in recommendations:
        key = rec['skill'].lower()
        if key not in seen:
            seen.add(key)
            unique_recs.append(rec)
    
    return jsonify({
        'current_skills_count': len(current_skills),
        'total_psa_skills': len(skills_taxonomy),
        'recommended_skills': unique_recs[:15],
        'coverage_percentage': round(len(current_skills) / len(skills_taxonomy) * 100, 1)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_career():
    """AI-powered career analysis using PSA's Azure OpenAI API"""
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
    
    # Get skills taxonomy context - CONDENSED to reduce token usage
    relevant_skills = []
    current_dept = emp['employment_info']['department'].split(':')[0]
    
    for skill in skills_taxonomy:
        func = skill['Function / Unit / Skill']
        spec = skill['Specialisation / Unit']
        if (current_dept.lower() in func.lower() or 
            (target_role and any(word in func.lower() for word in target_role.lower().split() if len(word) > 3))):
            relevant_skills.append(spec)
    
    # Deduplicate and limit to 10 most relevant
    skills_context = ", ".join(list(set(relevant_skills))[:10]) if relevant_skills else "General PSA competencies"
    
    # SIMPLIFIED PROMPT to reduce token usage
    prompt = f"""You are a career advisor at PSA International (global port operator). Analyze this employee's career development.

Employee: {emp['personal_info']['name']}
Current: {emp['employment_info']['job_title']} in {emp['employment_info']['department'].split(':')[0]}
Experience: {years_at_psa} years at PSA
Skills: {', '.join(current_skills[:8])}
Strengths: {', '.join(competencies[:3])}

Target: {target_role if target_role else 'Career advancement'}

PSA Skills Available: {skills_context}

Create a JSON career plan:
{{
  "readiness_score": 75,
  "summary": "Two sentence assessment of readiness",
  "skill_gaps": [
    {{"skill": "Skill Name", "priority": "High", "why": "Brief reason"}},
    {{"skill": "Another Skill", "priority": "Medium", "why": "Brief reason"}},
    {{"skill": "Third Skill", "priority": "Low", "why": "Brief reason"}}
  ],
  "learning_path": [
    {{"step": 1, "skill": "Priority Skill", "action": "What to do", "timeline": "3 months", "resources": ["Course/Cert 1", "Course 2"]}},
    {{"step": 2, "skill": "Next Skill", "action": "Next action", "timeline": "2 months", "resources": ["Training", "Workshop"]}},
    {{"step": 3, "skill": "Third Skill", "action": "Follow-up", "timeline": "4 months", "resources": ["Certification"]}}
  ],
  "internal_opportunities": [
    "Specific PSA project (e.g., Tuas Port Automation team)",
    "Another PSA opportunity (e.g., PORTNET modernization)",
    "Cross-functional opportunity"
  ],
  "mentorship_match": "Type of mentor to seek at PSA and why",
  "next_30_days": [
    "Week 1: Specific action",
    "Week 2: Another action",
    "Week 3: Third action"
  ]
}}

Return ONLY valid JSON."""

    # Get API key - CRITICAL: Verify it's loaded
    api_key = TEST_API_KEY if TEST_API_KEY else os.getenv('AZURE_OPENAI_KEY')
    
    if not api_key:
        print("ERROR: No API key found!")
        return jsonify({'error': 'API key not configured. Check .env file.'}), 500
    
    # Construct API URL
    base_url = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION')
    
    if not base_url or not api_version:
        print("ERROR: Missing endpoint or API version!")
        return jsonify({'error': 'API configuration incomplete'}), 500
    
    api_url = f"{base_url}?api-version={api_version}"
    
    # Headers - TRY MULTIPLE FORMATS
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": api_key,
        "api-key": api_key,
        "Subscription-Key": api_key
    }
    
    # Request body
    body = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_completion_tokens": 3500
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"API CALL DEBUG")
        print(f"{'='*60}")
        print(f"Employee: {emp['personal_info']['name']}")
        print(f"Target: {target_role or 'Not specified'}")
        print(f"Prompt length: {len(prompt)} chars")
        print(f"API Key present: {bool(api_key)}")
        print(f"API Key length: {len(api_key)}")
        print(f"API Key starts: {api_key[:8]}...")
        print(f"Endpoint: {base_url}")
        print(f"Full URL: {api_url[:80]}...")
        print(f"Headers sent: {list(headers.keys())}")
        print(f"{'='*60}\n")
        
        # Make request
        response = requests.post(api_url, headers=headers, json=body, timeout=60)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            error_detail = response.text[:1000]
            print(f"\n{'='*60}")
            print(f"API ERROR DETAILS")
            print(f"{'='*60}")
            print(error_detail)
            print(f"{'='*60}\n")
            return jsonify({
                'error': f'API error {response.status_code}',
                'details': error_detail,
                'suggestion': 'Check API key in .env file. It should be 32 characters with no quotes or spaces.'
            }), 500
        
        # Parse response
        result_data = response.json()
        
        if 'choices' not in result_data or len(result_data['choices']) == 0:
            print(f"ERROR: Invalid response structure")
            return jsonify({'error': 'Invalid API response'}), 500
        
        choice = result_data['choices'][0]
        finish_reason = choice.get('finish_reason', 'unknown')
        content = choice.get('message', {}).get('content', '')
        
        print(f"Finish reason: {finish_reason}")
        print(f"Content length: {len(content)} chars")
        
        if not content:
            print(f"ERROR: Empty content - finish_reason: {finish_reason}")
            return jsonify({'error': 'AI returned empty response'}), 500
        
        if finish_reason == 'length':
            print(f"WARNING: Response truncated due to token limit")
        
        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        print(f"✓ Analysis completed successfully\n")
        
        return jsonify(result)
    
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
        return jsonify({'error': 'Request timeout. Try again.'}), 500
    
    except json.JSONDecodeError as e:
        print(f"JSON Error: {str(e)}")
        print(f"Content preview: {content[:300]}")
        return jsonify({'error': 'Invalid JSON from AI. Try again.'}), 500
    
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚢 PSA TalentFlow AI Backend Starting...")
    print("="*60)
    print(f"✓ Loaded {len(employees)} employee profiles")
    print(f"✓ Loaded {len(skills_taxonomy)} PSA skills")
    
    # Check API key on startup
    if TEST_API_KEY:
        print(f"⚠️  Using TEST_API_KEY (hardcoded)")
        print(f"    Key length: {len(TEST_API_KEY)}")
    else:
        key = os.getenv('AZURE_OPENAI_KEY')
        if key:
            print(f"✓ API key loaded from .env")
            print(f"    Key length: {len(key)}")
            print(f"    Key preview: {key[:8]}...")
        else:
            print(f"❌ WARNING: No API key found in .env!")
    
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    if endpoint:
        print(f"✓ Endpoint: {endpoint[:60]}...")
    else:
        print(f"❌ WARNING: No endpoint found!")
    
    print(f"✓ Server running on http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)