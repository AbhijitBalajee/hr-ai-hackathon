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
# Uncomment and paste your key here if .env isn't working
# TEST_API_KEY = "paste_your_actual_key_here"
TEST_API_KEY = None  # Set to None to use .env, or paste key as string for testing

# Load employee data
with open('../data/Employee_Profiles.json', 'r', encoding='utf-8') as f:
    employees = json.load(f)

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({"status": "Backend is running!", "total_employees": len(employees)})

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
    
    # Get recent projects/experiences
    recent_experience = ""
    if emp.get('experiences'):
        recent_experience = f"Recent experience: {emp['experiences'][0].get('focus', '')}"
    
    prompt = f"""You are an expert career advisor at PSA International, a global port operator specializing in container terminals and supply chain solutions.

Employee Profile:
- Name: {emp['personal_info']['name']}
- Current Role: {emp['employment_info']['job_title']}
- Department: {emp['employment_info']['department']}
- Years at PSA: {years_at_psa}
- Current Skills: {', '.join(current_skills[:10])}
- Competencies: {', '.join(competencies)}
{recent_experience}

Target Role: {target_role if target_role else 'Career advancement in their field'}

Provide a comprehensive career development plan in this EXACT JSON format:
{{
  "readiness_score": 75,
  "summary": "2-3 sentence assessment of their readiness and potential for the target role",
  "skill_gaps": [
    {{"skill": "Specific Skill Name", "priority": "High", "why": "Detailed explanation of why this skill is important for the target role"}},
    {{"skill": "Another Skill", "priority": "Medium", "why": "Reason this skill matters"}},
    {{"skill": "Third Skill", "priority": "Low", "why": "Why this is beneficial but not critical"}}
  ],
  "learning_path": [
    {{"step": 1, "skill": "First Priority Skill", "action": "Concrete action they should take", "timeline": "3 months", "resources": ["Specific Course Name", "Certification Name", "Book/Resource"]}},
    {{"step": 2, "skill": "Second Skill", "action": "Next specific action", "timeline": "2 months", "resources": ["Training program", "Workshop"]}},
    {{"step": 3, "skill": "Third Skill", "action": "Follow-up action", "timeline": "4 months", "resources": ["Advanced certification", "Mentorship"]}}
  ],
  "internal_opportunities": [
    "Specific PSA project or initiative they could join (e.g., 'Join the Tuas Port Automation Enhancement team')",
    "Another concrete internal opportunity (e.g., 'Lead the PORTNET API modernization workstream')",
    "Cross-functional opportunity (e.g., 'Participate in the Regional Digital Transformation Committee')"
  ],
  "mentorship_match": "Suggest a specific type of mentor they should seek at PSA and exactly why (e.g., 'Connect with a Senior Director in Operations who has experience in automation projects, as they can provide insights on bridging technical and operational leadership')",
  "next_30_days": [
    "Week 1: Specific actionable task",
    "Week 2: Another concrete step", 
    "Week 3: Third specific action"
  ]
}}

Guidelines:
- Be specific to PSA's operations: automated terminals, PORTNET platform, global port network, supply chain digitalization
- Reference real industry trends: AI in logistics, IoT in ports, sustainability in maritime
- Readiness score should be realistic (50-90 range based on skill gaps)
- All recommendations must be actionable and concrete, not generic
- Consider multi-generational workforce: tailor advice to their career stage"""

    # Get API key - use test key if set, otherwise from .env
    api_key = TEST_API_KEY if TEST_API_KEY else os.getenv('AZURE_OPENAI_KEY')
    
    if not api_key:
        return jsonify({'error': 'API key not configured. Check .env file.'}), 500
    
    # Construct full API URL
    base_url = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION')
    api_url = f"{base_url}?api-version={api_version}"
    
    # Headers for Azure API Management - trying multiple header formats
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": api_key,  # Standard Azure APIM header
        "api-key": api_key,                     # Alternative format
        "Subscription-Key": api_key,            # Another alternative
        "Authorization": f"Bearer {api_key}"    # OAuth style (just in case)
    }
    
    # Request body
    # Request body - using default parameters for gpt-5-mini
    body = {
    "messages": [
        {"role": "system", "content": "You are a career development expert specializing in the maritime and port logistics industry. Always respond with valid JSON."},
        {"role": "user", "content": prompt}
    ],
    "max_completion_tokens": 2500
}
    
    try:
        print(f"\n{'='*60}")
        print(f"API CALL DEBUG INFO")
        print(f"{'='*60}")
        print(f"URL: {api_url}")
        print(f"Using test key: {bool(TEST_API_KEY)}")
        print(f"Key present: {bool(api_key)}")
        print(f"Key length: {len(api_key) if api_key else 0}")
        print(f"Key starts with: {api_key[:8] if api_key else 'NONE'}...")
        print(f"Employee: {emp['personal_info']['name']}")
        print(f"Target role: {target_role or 'Not specified'}")
        print(f"Headers being sent: {list(headers.keys())}")
        print(f"{'='*60}\n")
        
        # Make the request
        response = requests.post(api_url, headers=headers, json=body, timeout=45)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}\n")
        
        # Check for errors
        if response.status_code != 200:
            error_detail = response.text[:1000]
            print(f"{'='*60}")
            print(f"API ERROR RESPONSE")
            print(f"{'='*60}")
            print(error_detail)
            print(f"{'='*60}\n")
            
            # Provide helpful error messages
            if response.status_code == 401:
                suggestion = "API key authentication failed. Possible issues:\n" \
                           "1. Wrong API key (check if you copied it correctly)\n" \
                           "2. Wrong header format (PSA may use a different header)\n" \
                           "3. Key not activated yet (check with PSA organizers)\n" \
                           "4. Try asking PSA for a working example"
            elif response.status_code == 403:
                suggestion = "Access forbidden. Your key may not have permission for this endpoint."
            elif response.status_code == 404:
                suggestion = "Endpoint not found. Check the URL format with PSA organizers."
            elif response.status_code == 429:
                suggestion = "Rate limit exceeded. Wait a moment and try again."
            else:
                suggestion = "Unknown error. Contact PSA organizers for support."
            
            return jsonify({
                'error': f'API returned status {response.status_code}',
                'details': error_detail,
                'suggestion': suggestion
            }), 500
        
        # Parse response
        result_data = response.json()
        
        # Check if response has the expected structure
        if 'choices' not in result_data or len(result_data['choices']) == 0:
            print(f"Unexpected response structure: {result_data}")
            return jsonify({'error': 'Unexpected API response structure'}), 500
        
        content = result_data['choices'][0]['message']['content']
        
        print(f"✓ AI Response received (length: {len(content)} chars)")
        
        # Try to extract JSON if wrapped in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse the JSON
        result = json.loads(content)
        
        # Validate the result has required fields
        required_fields = ['readiness_score', 'summary', 'skill_gaps', 'learning_path', 'internal_opportunities', 'mentorship_match', 'next_30_days']
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"Warning: Missing fields in AI response: {missing_fields}")
        
        print(f"✓ Analysis completed successfully")
        print(f"{'='*60}\n")
        
        return jsonify(result)
    
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
        return jsonify({'error': 'Request timed out after 45 seconds. Please try again.'}), 500
    
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection error - {str(e)}")
        return jsonify({'error': 'Could not connect to API. Check your internet connection and endpoint URL.'}), 500
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request exception - {str(e)}")
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parsing failed - {str(e)}")
        print(f"Content preview: {content[:300]}")
        return jsonify({
            'error': 'AI response was not valid JSON',
            'details': 'The AI generated text instead of structured data. Try again.'
        }), 500
    
    except KeyError as e:
        print(f"ERROR: Missing key in response - {str(e)}")
        return jsonify({'error': f'Response missing expected field: {str(e)}'}), 500
    
    except Exception as e:
        print(f"ERROR: Unexpected error - {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚢 PSA TalentFlow AI Backend Starting...")
    print("="*60)
    print(f"✓ Loaded {len(employees)} employee profiles")
    
    # Check configuration
    if TEST_API_KEY:
        print(f"⚠️  Using TEST_API_KEY (hardcoded)")
    else:
        key = os.getenv('AZURE_OPENAI_KEY')
        if key:
            print(f"✓ API key loaded from .env (length: {len(key)})")
        else:
            print(f"❌ WARNING: No API key found!")
    
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    if endpoint:
        print(f"✓ Endpoint: {endpoint[:50]}...")
    else:
        print(f"❌ WARNING: No endpoint configured!")
    
    print(f"✓ Server running on http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)