================================================================================
                    🚢 SkillsVoyage - PSA Career Development Platform
================================================================================

A comprehensive AI-powered career development platform for PSA International 
employees, featuring personalized learning roadmaps, skills analysis, resume 
parsing, and an anonymous community forum.

Built for PSA Code Sprint 2025 • Problem Statement 4 

Built by Abhijit Balajee and Rajan Praveen

================================================================================
                                    FEATURES
================================================================================

✨ CORE FEATURES:
  • AI-Powered Career Analysis - Generate personalized career roadmaps using 
    Azure OpenAI
  • Skills Gap Identification - Identify missing skills for career progression
  • Learning Path Generator - Week-by-week detailed learning plans
  • PSA Skills Framework Coverage - Track skills against PSA's 107-skill taxonomy
  • Career Readiness Score - Quantify readiness for target roles
  • ROI Calculator - Show business impact of career development

🎯 OPPORTUNITY MATCHING:
  • SkillsMatch - Tinder-style swipeable interface for internal opportunities
  • Compatibility Scoring - Match employees to projects based on skills
  • Focused Learning Paths - Generate targeted plans for specific opportunities
  • High-Compatibility Detection - Smart suggestions when >90% ready

📄 RESUME INTELLIGENCE:
  • Resume Upload - Drag & drop or file selection (PDF, DOC, DOCX, TXT)
  • AI Skills Extraction - Automatically extract skills from resumes
  • Profile Auto-Update - Seamlessly add new skills to employee profiles
  • Visual Feedback - Clear indication of new vs existing skills

💬 COMMUNITY FORUM:
  • Anonymous Posting - Share questions/experiences with anonymous identities
  • Category-Based Organization - Career, Skills, Mentorship, Projects, General
  • Threaded Discussions - Reply to posts with full conversation threading
  • Post Filtering - Filter by category for targeted browsing
  • Like & Engage - Show support for helpful posts

🎨 USER EXPERIENCE:
  • Dark Mode - Easy on the eyes for extended use
  • Responsive Design - Works on desktop, tablet, and mobile
  • Interactive UI - Smooth animations and transitions
  • Progress Tracking - Visual indicators of learning progress
  • Achievement System - Gamified milestones and badges

================================================================================
                                  TECH STACK
================================================================================

FRONTEND:
  • HTML5 + Vanilla JavaScript
  • Tailwind CSS (via CDN)
  • Font Awesome Icons
  • Modern ES6+ features

BACKEND:
  • Python 3.8+
  • Flask - Web framework
  • Flask-CORS - Cross-origin support
  • Azure OpenAI API - AI-powered analysis
  • Requests - HTTP library
  • Python-dotenv - Environment management

DATA:
  • Employee_Profiles.json - 5 sample employee profiles
  • skills_taxonomy.json - PSA's 107 core competencies

================================================================================
                              GETTING STARTED
================================================================================

PREREQUISITES:
  • Python 3.8 or higher
  • Azure OpenAI API access (or compatible endpoint)
  • Modern web browser (Chrome, Firefox, Edge, Safari)
  • Git

INSTALLATION:

1. Clone the Repository
```
   git clone <repository-url>
   cd skillsvoyage
```

2. Set Up Backend

   a. Navigate to backend directory:
```
      cd backend
```

   b. Create virtual environment:
```
      python -m venv venv
```

   c. Activate virtual environment:
      • Windows: venv\Scripts\activate
      • Mac/Linux: source venv/bin/activate

   d. Install dependencies:
```
      pip install flask flask-cors python-dotenv requests
```

   e. Create .env file in backend folder:
```
      AZURE_OPENAI_KEY=your-api-key-here
      AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/openai/deployments/your-deployment/chat/completions
      AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

      IMPORTANT: Replace with your actual Azure OpenAI credentials
      • No quotes around values
      • No spaces
      • API key is typically 32 characters

   f. Verify setup:
```
      python app.py
```
      You should see:
      ✓ Loaded 5 employee profiles
      ✓ Loaded 107 PSA skills
      ✓ API key loaded from .env
      ✓ Server running on http://127.0.0.1:5001

3. Set Up Frontend

   a. Open new terminal (keep backend running)

   b. Navigate to frontend directory:
```
      cd frontend
```

   c. Open index.html in browser:
      • Double-click index.html, OR
      • Use Live Server extension in VS Code, OR
      • Use Python: python -m http.server 8000

   d. Access application:
      • If using Python server: http://localhost:8000
      • Otherwise: Open index.html directly

================================================================================
                                 CONFIGURATION
================================================================================

BACKEND CONFIGURATION (.env file):

AZURE_OPENAI_KEY=
  • Your Azure OpenAI subscription key
  • 32 characters, no quotes
  • Get from Azure Portal > Cognitive Services > Keys

AZURE_OPENAI_ENDPOINT=
  • Full deployment URL including model name
  • Format: https://<resource>.openai.azure.com/openai/deployments/<model>/chat/completions

AZURE_OPENAI_API_VERSION=
  • API version (recommended: 2024-02-15-preview)
  • Check Azure docs for latest version

FRONTEND CONFIGURATION (index.html):

API_URL constant (line ~1070):
  • Default: http://localhost:5001/api
  • Change if backend runs on different port/host

================================================================================
                                  API ENDPOINTS
================================================================================

EMPLOYEE MANAGEMENT:
  GET  /api/employees           - List all employees
  GET  /api/employee/<id>       - Get employee profile
  GET  /api/skills-taxonomy     - Get PSA skills framework
  GET  /api/match-skills/<id>   - Match employee skills to taxonomy

CAREER ANALYSIS:
  POST /api/analyze             - Generate career roadmap
       Body: { employee_id, target_role }
  
  POST /api/analyze-opportunity - Generate opportunity-focused plan
       Body: { employee_id, opportunity_title, missing_skills[] }

  POST /api/learning-detail     - Get detailed weekly breakdown
       Body: { skill, timeline, action, resources[] }

RESUME PROCESSING:
  POST /api/upload-resume       - Parse resume and extract skills
       Form Data: { resume: file, employee_id: string }

FORUM (Future Enhancement):
  GET  /api/forum/posts         - Get all forum posts
  POST /api/forum/posts         - Create new post
  GET  /api/forum/posts/<id>    - Get post details
  POST /api/forum/posts/<id>/reply - Add reply to post

UTILITY:
  GET  /api/test                - Test backend connectivity
  GET  /api/debug               - Debug API configuration

================================================================================
                                    USAGE
================================================================================

BASIC WORKFLOW:

1. Select Employee
   • Choose from dropdown at top of page
   • View employee stats and current profile

2. Upload Resume (Optional)
   • Drag & drop resume file or click to browse
   • AI automatically extracts and adds skills
   • Profile updates in real-time

3. Generate Career Roadmap
   • Enter target role (e.g., "Chief Technology Officer")
   • Click "Generate AI Career Roadmap"
   • Review readiness score and skill gaps

4. Explore Learning Path
   • Click any learning step for detailed weekly breakdown
   • View resources, activities, and deliverables
   • Track success metrics

5. Discover Opportunities
   • Click "Discover Your Next Opportunity"
   • Swipe through matched opportunities
   • Generate focused learning path when highly compatible

6. Join Community
   • Click chat icon in header
   • Browse posts by category
   • Create anonymous posts
   • Reply to discussions

================================================================================
                              PROJECT STRUCTURE
================================================================================

skillsvoyage/
├── frontend/
│   └── index.html              # Main application (complete SPA)
├── backend/
│   ├── app.py                  # Flask API server
│   ├── .env                    # Environment variables (not in git)
│   └── requirements.txt        # Python dependencies (create this)
├── data/
│   ├── Employee_Profiles.json  # Sample employee data (5 profiles)
│   └── skills_taxonomy.json    # PSA skills framework (107 skills)
└── README.txt                  # This file

================================================================================
                             SAMPLE EMPLOYEE DATA
================================================================================

5 employees across various roles:
  • EMP-20001 - Samantha Lee (Cloud Solutions Architect)
  • EMP-20002 - Nur Aisyah Binte Rahman (Cybersecurity Analyst)
  • EMP-20003 - Rohan Mehta (Finance Manager - FP&A)
  • EMP-20004 - Grace Lee (Senior HR Manager)
  • EMP-20005 - Felicia Goh (Treasury Analyst)

Each profile includes:
  • Personal information (name, email, location, languages)
  • Employment details (job title, department, hire date)
  • Skills aligned to PSA's taxonomy
  • Core competencies and proficiency levels
  • Work experiences and rotations
  • Position history with focus areas
  • Project contributions and outcomes
  • Educational background

================================================================================
                                TROUBLESHOOTING
================================================================================

ISSUE: Backend won't start
SOLUTION: 
  • Check Python version (3.8+): python --version
  • Verify all dependencies installed: pip list
  • Check .env file exists in backend folder
  • Verify .env has no quotes around values

ISSUE: API key error / 401 Unauthorized
SOLUTION:
  • Verify AZURE_OPENAI_KEY in .env is correct (32 chars)
  • Check key has no extra spaces or quotes
  • Confirm key is active in Azure Portal
  • Try the /api/debug endpoint to see key status

ISSUE: Frontend can't connect to backend
SOLUTION:
  • Verify backend is running (check terminal)
  • Check API_URL in index.html matches backend address
  • Disable browser CORS extensions
  • Clear browser cache

ISSUE: AI responses are empty or truncated
SOLUTION:
  • Check Azure OpenAI quota/limits
  • Verify API version is correct
  • Check for content filters blocking responses
  • Review backend terminal for detailed error logs

ISSUE: Resume upload not working
SOLUTION:
  • Ensure file is PDF, DOC, DOCX, or TXT
  • Check file size (< 10MB recommended)
  • Verify employee is selected first
  • Check browser console for errors

ISSUE: Dark mode styles broken
SOLUTION:
  • Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
  • Check Tailwind CDN is loading
  • Verify no browser extensions interfering with styles

ISSUE: "Employee not found" error
SOLUTION:
  • Verify employee IDs match format: EMP-20001 to EMP-20005
  • Check Employee_Profiles.json is in correct location (data folder)
  • Restart backend server after any data changes

================================================================================
                            DEVELOPMENT NOTES
================================================================================

SECURITY CONSIDERATIONS:
  • Never commit .env file to Git (add to .gitignore)
  • API keys should be kept secret
  • In production, use proper authentication/authorization
  • Forum posts should have moderation in production
  • Resume uploads should be scanned for security

PERFORMANCE OPTIMIZATIONS:
  • AI calls cached for 5 minutes (add caching in production)
  • Skills taxonomy loaded once on startup
  • Frontend uses vanilla JS for minimal overhead
  • Consider CDN for production deployment

KNOWN LIMITATIONS:
  • Resume parsing returns mock data (needs AI integration)
  • Forum data not persisted (needs database)
  • No user authentication (uses employee selector)
  • Limited to 5 sample employees
  • AI responses depend on Azure OpenAI availability
  • Sample opportunities in SkillsMatch are hardcoded

FUTURE ENHANCEMENTS:
  • Real resume parsing with OCR and NLP
  • Database integration (PostgreSQL)
  • User authentication and session management
  • Email notifications for forum replies
  • Calendar integration for learning schedules
  • Manager dashboard for team oversight
  • Mobile app version
  • Integration with PSA's existing HR systems
  • Advanced analytics and reporting
  • Multi-language support
  • Expand employee profiles dataset
  • Dynamic opportunity matching from real job postings

================================================================================
                              CONTRIBUTING
================================================================================

To contribute to this project:

1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add AmazingFeature')
4. Push to branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

CODE STYLE:
  • Python: Follow PEP 8
  • JavaScript: Use ES6+ features, semicolons optional
  • HTML: Semantic tags, proper indentation
  • CSS: Tailwind utility classes preferred

================================================================================
                                  TESTING
================================================================================

BACKEND TESTING:
  1. Start backend: python app.py
  2. Test endpoint: curl http://localhost:5001/api/test
  3. Expected: {"status": "Backend is running!", "total_employees": 5, ...}
  4. Debug config: curl http://localhost:5001/api/debug

FRONTEND TESTING:
  1. Open browser developer tools (F12)
  2. Check Console for errors
  3. Test employee selection
  4. Test career analysis with known employee
  5. Verify all modals open/close properly

INTEGRATION TESTING:
  1. Select employee → should load profile
  2. Generate roadmap → should return AI analysis
  3. Upload resume → should extract skills
  4. Open forum → should show/create posts
  5. Test dark mode toggle
  6. Test SkillsMatch swipe interface

TEST EMPLOYEE IDs:
  • EMP-20001 - IT/Cloud focus
  • EMP-20002 - Cybersecurity focus
  • EMP-20003 - Finance focus
  • EMP-20004 - Human Resources focus
  • EMP-20005 - Treasury/Finance focus

================================================================================
                                  LICENSE
================================================================================

This project was created for PSA Code Sprint 2025.
All rights reserved by the development team.

For educational and internal PSA use only.

================================================================================
                                  SUPPORT
================================================================================

For questions or issues:
  • Check Troubleshooting section above
  • Review backend terminal logs for detailed errors
  • Use /api/debug endpoint to verify configuration
  • Check browser console for frontend errors

Technical Requirements:
  • Backend: Python 3.8+, Flask, Azure OpenAI access
  • Frontend: Modern browser with JavaScript enabled
  • Network: Internet connection for AI API calls

================================================================================
                                ACKNOWLEDGMENTS
================================================================================

Built with:
  • Azure OpenAI - AI-powered career analysis
  • Tailwind CSS - Styling framework
  • Font Awesome - Icon library
  • Flask - Python web framework

Special thanks to:
  • PSA International for the Code Sprint 2025 opportunity
  • Azure OpenAI team for powerful AI capabilities
  • Open source community for excellent tools and libraries

================================================================================

Last Updated: January 2025
Version: 1.0.0

🚢 Empowering PSA's Future-Ready Workforce

================================================================================