import streamlit as st
import google.generativeai as genai
import json
import time
from datetime import datetime, timedelta
import hashlib

# Page config
st.set_page_config(page_title="Adaptive Learning System", page_icon="🎓", layout="wide")

# Initialize session state
def init_session_state():
    defaults = {
        'logged_in': False,
        'user': None,
        'page': 'login',
        'subjects': None,
        'selected_subject': None,
        'test_type': None,
        'test_duration': None,
        'test_start_time': None,
        'questions': [],
        'current_question_idx': 0,
        'test_structure': None,
        'current_topic_idx': 0,
        'current_level': 'easy',
        'topic_scores': {},
        'answers_log': [],
        'test_completed': False,
        'questions_asked': 0,
        'correct_answers': 0,
        'wrong_answers': 0,
        'selected_answer': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Dummy users database (replace with actual database)
USERS_DB = {
    'student1': {'password': hashlib.sha256('pass123'.encode()).hexdigest(), 'name': 'John Doe', 'semester': 3},
    'student2': {'password': hashlib.sha256('pass456'.encode()).hexdigest(), 'name': 'Jane Smith', 'semester': 5}
}

# Subject structure based on semester
SUBJECTS_BY_SEMESTER = {
    3: ['C Programming', 'Data Structures', 'Database Management', 'Computer Networks'],
    5: ['Operating Systems', 'Compiler Design', 'Machine Learning', 'Web Technologies']
}

INTERVIEW_PREP = ['C Programming', 'Data Structures', 'Algorithms', 'DBMS', 'Operating Systems', 'Computer Networks']

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .subject-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        cursor: pointer;
        transition: transform 0.2s;
        margin: 0.5rem;
    }
    .subject-card:hover {
        transform: scale(1.05);
    }
    .timer {
        position: fixed;
        top: 80px;
        right: 20px;
        background: #ff6b6b;
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-size: 1.5rem;
        font-weight: bold;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .progress-tracker {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .level-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.2rem;
    }
    .easy { background: #d4edda; color: #155724; }
    .medium { background: #fff3cd; color: #856404; }
    .hard { background: #f8d7da; color: #721c24; }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def configure_gemini():
    """Configure Gemini API"""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("⚠️ Please set GEMINI_API_KEY in Streamlit secrets")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

model = configure_gemini()

def login_page():
    """Login page"""
    st.markdown('<div class="main-header"><h1>🎓 Adaptive Learning System</h1><p>Smart Assessment Platform</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔐 Student Login")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            hashed_pass = hashlib.sha256(password.encode()).hexdigest()
            if username in USERS_DB and USERS_DB[username]['password'] == hashed_pass:
                st.session_state.logged_in = True
                st.session_state.user = USERS_DB[username]
                st.session_state.user['username'] = username
                st.session_state.page = 'dashboard'
                st.rerun()
            else:
                st.error("Invalid credentials!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("Demo: username: student1, password: pass123")

def dashboard_page():
    """Main dashboard"""
    st.markdown(f'<div class="main-header"><h1>Welcome, {st.session_state.user["name"]}! 👋</h1><p>Semester {st.session_state.user["semester"]} | Choose your assessment</p></div>', unsafe_allow_html=True)
    
    # Logout button
    if st.button("🚪 Logout", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("### 📚 Select Assessment Type")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📖 Semester Subjects")
        subjects = SUBJECTS_BY_SEMESTER[st.session_state.user['semester']]
        for subject in subjects:
            if st.button(f"📌 {subject}", key=f"sem_{subject}", use_container_width=True):
                st.session_state.selected_subject = subject
                st.session_state.page = 'test_config'
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💼 Interview Preparation")
        for subject in INTERVIEW_PREP:
            if st.button(f"🎯 {subject}", key=f"int_{subject}", use_container_width=True):
                st.session_state.selected_subject = subject
                st.session_state.page = 'test_config'
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def test_config_page():
    """Test configuration page"""
    st.markdown(f'<div class="main-header"><h1>Configure Test: {st.session_state.selected_subject}</h1></div>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = 'dashboard'
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Test Type")
        test_type = st.radio("Select test type:", 
                            ["Grand Test (All Topics)", "Topic-wise Test"],
                            key="test_type_radio")
        st.session_state.test_type = test_type
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⏱️ Duration Mode")
        duration_mode = st.radio("Select duration:", 
                                ["Fixed Duration (5 min)", "Fixed Duration (60 min)", "Variable Duration"],
                                key="duration_radio")
        
        if "Fixed" in duration_mode:
            st.session_state.test_duration = 5 if "5" in duration_mode else 60
        else:
            st.session_state.test_duration = None
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Test Rules")
    st.markdown("""
    - Each topic has **Easy, Medium, and Hard** difficulty levels
    - Minimum **2 questions per level** before advancing
    - **Correct answers**: Move to next level/topic
    - **Wrong answers**: Move back or stay in current level
    - **Fixed duration**: Assessment includes speed and accuracy
    - **Variable duration**: Focus on comprehensive coverage
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🚀 Start Test", use_container_width=True, type="primary"):
        with st.spinner("🔄 Generating test structure..."):
            generate_test_structure()
            st.session_state.page = 'test'
            st.session_state.test_start_time = datetime.now()
            st.rerun()

def generate_test_structure():
    """Generate test structure with topics and subtopics"""
    prompt = f"""For the subject "{st.session_state.selected_subject}", create a comprehensive test structure.
    
    Return ONLY a JSON object with this structure:
    {{
        "topics": [
            {{
                "name": "Topic Name",
                "subtopics": ["subtopic1", "subtopic2", "subtopic3"]
            }}
        ]
    }}
    
    Include 5-8 major topics with 3-5 subtopics each. No markdown, no explanation."""
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
        content = content.strip()
        structure = json.loads(content)
        
        # Initialize tracking
        st.session_state.test_structure = structure
        st.session_state.topic_scores = {
            topic['name']: {'easy': {'asked': 0, 'correct': 0}, 
                          'medium': {'asked': 0, 'correct': 0}, 
                          'hard': {'asked': 0, 'correct': 0}}
            for topic in structure['topics']
        }
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.test_structure = {"topics": [{"name": st.session_state.selected_subject, "subtopics": ["General"]}]}

def generate_question(topic, subtopics, level):
    """Generate a single question"""
    subtopics_str = ', '.join(subtopics)
    prompt = f"""Generate 1 multiple-choice question for "{topic}" covering subtopics: {subtopics_str} at {level} difficulty.
    
    Return ONLY a JSON object:
    {{
        "question": "Question text?",
        "options": ["A", "B", "C", "D"],
        "correctAnswer": 0,
        "explanation": "Brief explanation"
    }}
    
    No markdown, no explanation."""
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
        content = content.strip()
        question = json.loads(content)
        question['topic'] = topic
        question['level'] = level
        return question
    except:
        return None

def check_time_remaining():
    """Check if time is remaining"""
    if st.session_state.test_duration:
        elapsed = (datetime.now() - st.session_state.test_start_time).total_seconds() / 60
        remaining = st.session_state.test_duration - elapsed
        if remaining <= 0:
            st.session_state.test_completed = True
            st.session_state.page = 'results'
            st.rerun()
        return remaining
    return None

def test_page():
    """Active test page"""
    # Check time
    time_remaining = check_time_remaining()
    
    # Display timer
    if time_remaining is not None:
        mins = int(time_remaining)
        secs = int((time_remaining - mins) * 60)
        st.markdown(f'<div class="timer">⏱️ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="main-header"><h1>{st.session_state.selected_subject} Test</h1></div>', unsafe_allow_html=True)
    
    # Progress tracker
    current_topic = st.session_state.test_structure['topics'][st.session_state.current_topic_idx]
    
    st.markdown('<div class="progress-tracker">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Questions", st.session_state.questions_asked)
    with col2:
        st.metric("Correct", st.session_state.correct_answers)
    with col3:
        st.metric("Wrong", st.session_state.wrong_answers)
    with col4:
        accuracy = 0 if st.session_state.questions_asked == 0 else round((st.session_state.correct_answers / st.session_state.questions_asked) * 100, 1)
        st.metric("Accuracy", f"{accuracy}%")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"**Current Topic:** {current_topic['name']} | **Level:** {st.session_state.current_level.upper()}")
    st.progress((st.session_state.current_topic_idx + 1) / len(st.session_state.test_structure['topics']))
    
    # Generate question if needed
    if st.session_state.selected_answer is None and len(st.session_state.questions) == st.session_state.current_question_idx:
        with st.spinner("Generating question..."):
            question = generate_question(
                current_topic['name'],
                current_topic['subtopics'],
                st.session_state.current_level
            )
            if question:
                st.session_state.questions.append(question)
                st.rerun()
    
    if len(st.session_state.questions) > st.session_state.current_question_idx:
        current_q = st.session_state.questions[st.session_state.current_question_idx]
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### Question {st.session_state.questions_asked + 1}")
        st.markdown(f"**{current_q['question']}**")
        
        # Display options
        for idx, option in enumerate(current_q['options']):
            if st.session_state.selected_answer is None:
                if st.button(option, key=f"opt_{idx}", use_container_width=True):
                    handle_answer(idx, current_q)
                    st.rerun()
            else:
                is_selected = idx == st.session_state.selected_answer
                is_correct = idx == current_q['correctAnswer']
                
                if is_selected and is_correct:
                    st.success(f"✅ {option}")
                elif is_selected and not is_correct:
                    st.error(f"❌ {option}")
                elif is_correct:
                    st.success(f"✅ {option}")
                else:
                    st.info(option)
        
        if st.session_state.selected_answer is not None:
            st.info(f"**Explanation:** {current_q.get('explanation', 'N/A')}")
            if st.button("Next Question ➡️", use_container_width=True, type="primary"):
                st.session_state.selected_answer = None
                st.session_state.current_question_idx += 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def handle_answer(selected_idx, question):
    """Handle answer submission and adaptive logic"""
    is_correct = selected_idx == question['correctAnswer']
    st.session_state.selected_answer = selected_idx
    st.session_state.questions_asked += 1
    
    topic = question['topic']
    level = question['level']
    
    # Update scores
    st.session_state.topic_scores[topic][level]['asked'] += 1
    
    if is_correct:
        st.session_state.correct_answers += 1
        st.session_state.topic_scores[topic][level]['correct'] += 1
        
        # Adaptive logic for correct answer
        if st.session_state.topic_scores[topic][level]['asked'] >= 2:
            # Move to next level or topic
            if level == 'easy':
                st.session_state.current_level = 'medium'
            elif level == 'medium':
                st.session_state.current_level = 'hard'
            else:  # hard level completed
                # Move to next topic
                if st.session_state.current_topic_idx < len(st.session_state.test_structure['topics']) - 1:
                    st.session_state.current_topic_idx += 1
                    st.session_state.current_level = 'easy'
                else:
                    # Test completed
                    st.session_state.test_completed = True
                    st.session_state.page = 'results'
    else:
        st.session_state.wrong_answers += 1
        
        # Adaptive logic for wrong answer
        if level == 'medium':
            st.session_state.current_level = 'easy'
        elif level == 'hard':
            st.session_state.current_level = 'medium'
        # Stay at easy if wrong
    
    # Log answer
    st.session_state.answers_log.append({
        'question': question['question'],
        'selected': question['options'][selected_idx],
        'correct': question['options'][question['correctAnswer']],
        'is_correct': is_correct,
        'topic': topic,
        'level': level,
        'time': datetime.now()
    })

def results_page():
    """Results and analytics page"""
    st.markdown('<div class="main-header"><h1>📊 Test Results</h1></div>', unsafe_allow_html=True)
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stats-card"><h2>{st.session_state.questions_asked}</h2><p>Total Questions</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stats-card"><h2>{st.session_state.correct_answers}</h2><p>Correct</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stats-card"><h2>{st.session_state.wrong_answers}</h2><p>Wrong</p></div>', unsafe_allow_html=True)
    with col4:
        accuracy = 0 if st.session_state.questions_asked == 0 else round((st.session_state.correct_answers / st.session_state.questions_asked) * 100, 1)
        st.markdown(f'<div class="stats-card"><h2>{accuracy}%</h2><p>Accuracy</p></div>', unsafe_allow_html=True)
    
    # Time taken
    if st.session_state.test_duration:
        elapsed = (datetime.now() - st.session_state.test_start_time).total_seconds() / 60
        st.info(f"⏱️ **Time Used:** {int(elapsed)} minutes out of {st.session_state.test_duration} minutes")
    else:
        elapsed = (datetime.now() - st.session_state.test_start_time).total_seconds() / 60
        st.info(f"⏱️ **Total Time Taken:** {int(elapsed)} minutes")
    
    # Topic-wise performance
    st.markdown("### 📈 Topic-wise Performance")
    for topic, scores in st.session_state.topic_scores.items():
        if any(scores[level]['asked'] > 0 for level in ['easy', 'medium', 'hard']):
            st.markdown(f"**{topic}**")
            cols = st.columns(3)
            for idx, level in enumerate(['easy', 'medium', 'hard']):
                with cols[idx]:
                    if scores[level]['asked'] > 0:
                        accuracy = round((scores[level]['correct'] / scores[level]['asked']) * 100, 1)
                        st.metric(f"{level.upper()}", f"{scores[level]['correct']}/{scores[level]['asked']} ({accuracy}%)")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    weak_topics = []
    for topic, scores in st.session_state.topic_scores.items():
        for level in ['easy', 'medium', 'hard']:
            if scores[level]['asked'] > 0:
                accuracy = (scores[level]['correct'] / scores[level]['asked']) * 100
                if accuracy < 60:
                    weak_topics.append(f"{topic} ({level})")
    
    if weak_topics:
        st.warning(f"📚 **Focus on these areas:** {', '.join(weak_topics)}")
    else:
        st.success("🎉 **Great performance across all topics!**")
    
    if st.button("🏠 Back to Dashboard", use_container_width=True, type="primary"):
        # Reset test state
        st.session_state.page = 'dashboard'
        st.session_state.selected_subject = None
        st.session_state.test_type = None
        st.session_state.questions = []
        st.session_state.current_question_idx = 0
        st.session_state.questions_asked = 0
        st.session_state.correct_answers = 0
        st.session_state.wrong_answers = 0
        st.session_state.selected_answer = None
        st.session_state.test_completed = False
        st.rerun()

# Main router
if not st.session_state.logged_in:
    login_page()
elif st.session_state.page == 'dashboard':
    dashboard_page()
elif st.session_state.page == 'test_config':
    test_config_page()
elif st.session_state.page == 'test':
    test_page()
elif st.session_state.page == 'results':
    results_page()