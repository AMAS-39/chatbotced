from flask import Flask, request, jsonify, render_template
import anthropic
import os
from datetime import datetime
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
from knowledge_base import encode_knowledge_base
from sentence_transformers import SentenceTransformer

knowledge_base_embeddings = encode_knowledge_base()
model = SentenceTransformer('all-MiniLM-L6-v2')



app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY')
)
def setup_app():
    print("Starting CED Chatbot server...")
    
    # Initialize database
    try:
        init_db()
        print("Database initialized successfully")
        
        # Test database connection
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM messages')
        count = c.fetchone()[0]
        conn.close()
        print(f"Current message count in database: {count}")
        
    except Exception as e:
        print(f"Error during startup: {e}")
        raise

# Initialize database
def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    
    # Create messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            language TEXT NOT NULL,
            categories TEXT,
            question_type TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
init_db()
def save_message(user_message, bot_response, language, categories=None, question_type=None):
    """Save a message exchange to the database"""
    try:
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        categories_str = ','.join(categories) if categories else None
        
        print(f"Attempting to save message:")
        print(f"Timestamp: {timestamp}")
        print(f"User message: {user_message}")
        print(f"Bot response: {bot_response}")
        print(f"Language: {language}")
        print(f"Categories: {categories_str}")
        
        c.execute('''
            INSERT INTO messages (timestamp, user_message, bot_response, language, categories, question_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, user_message, bot_response, language, categories_str, question_type))
        
        conn.commit()
        row_id = c.lastrowid
        conn.close()
        print(f"Message saved successfully with ID: {row_id}")
        return row_id
        
    except Exception as e:
        print(f"Error saving message: {str(e)}")
        raise

def get_chat_history(limit=100):
    """Retrieve chat history from database"""
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT id, timestamp, user_message, bot_response, language, categories, question_type
        FROM messages
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    history = c.fetchall()
    conn.close()
    
    return history

# Department Information in both languages
# Update the DEPARTMENT_INFO_BILINGUAL dictionary with the new content
DEPARTMENT_INFO_BILINGUAL = {
    'en': """
Computer Education Department

**Contact Information:**
- Email: ced@tiu.edu.iq
- Faculty Phone: +964 750 330 24 92
- Campus Phones:
  - +964 (0) 750 835 7525
  - +964 (0) 750 705 0211
- Address: 100 Meter Street and Mosul Road, Erbil, Kurdistan Region, Iraq
- Building: Education Building

**Department Comparison:**
- Focus: Unlike IT or Computer Engineering, our department specializes in preparing skilled computer teachers while also providing comprehensive software development education.
- Career Path: Primary focus on producing qualified computer education teachers, with additional competency in software development.
- Entry Requirements: No English exam required, unlike IT and Computer Engineering departments.
- Financial Benefits: Unique discount system (25-90% based on grades) not available in IT or Computer Engineering departments.
- Educational Approach: Combines pedagogical training with technical computer science skills.

**Admissions Requirements:**
- Academic score required: Students who scored above 55 out of 100 in 12th grade are eligible.
- Entrance exams: No entrance exams required for Computer Education, including Computer and English skills.
- Prerequisite courses: None.
- Application deadline: December 12, 2024.
- Application process: Visit TIU to collect a form, fill it out, select Computer Education, and submit to the Ministry of Education.

**Curriculum & Courses:**
First Year:
- Fall Semester (20 credits, 30 ECTS):
  - Computer Skills I
  - Mathematics for Computer Science I
  - Basic courses
- Spring Semester (21 credits, 30 ECTS):
  - Computer Skills II
  - Mathematics for Computer Science II
  - Advanced skills

Second Year:
- Fall Semester (18 credits, 30 ECTS):
  - Introduction to Programming
  - Databases
- Spring Semester (18 credits, 30 ECTS):
  - Advanced Programming
  - Database Management

Third Year:
- Fall Semester (17 credits, 30 ECTS):
  - Hardware and Web Development
- Spring Semester (17 credits, 30 ECTS):
  - Networking and Teaching Methodology

Fourth Year:
- Fall Semester (16 credits, 30 ECTS):
  - Project Management and Research
- Spring Semester (21 credits, 30 ECTS):
  - Teaching Practice and Final Projects

Total Program Statistics:
- Total Credit Hours: 148
- Total ECTS: 240
- Duration: 8 semesters
- Balanced theoretical and practical components

**Faculty:**
- Led by Dr. Muhammed Anwar
- Teachers are Ms. Slver Abdulazeez, Ms. Narmin Mohammed, Ms. Saia Hasan, Mr. Rebin M. Ahmed, and Mr. Imad Rafeeq
- Assistant teachers are Mr Ahmad Ali, Ms Yara Arjuman, Ms Firdaus, Mr Abdulrahman
- Expertise: Web development, mobile applications, AI, computer vision, R&D, programming
- Accessibility: Dedicated office hours, weekly advisor hours, training sessions, workshops

**Facilities:**
- Labs: Robotics Lab, General Computer Lab
- Library: Accessible to all students
- Computer access: Available outside class hours
- Additional facilities: No specific study rooms or common areas

**Career Opportunities:**
Teaching Positions:
- Computer Language Teacher
- Senior Teacher
- Lab Assistant/Instructor
- Teacher Trainer
- Educational Consultant

Potential Employers:
- Government Schools
- Private Schools
- Universities and Institutes
- Government Offices
- Private Companies

**Student Life:**
- Clubs and organizations: Managed by the Dean of Students
- Regular events: Robotics workshops, AI workshops, cultural festivals, Nayric event
- Community culture: Close-knit, family-like

**Department Activities (2024-2025):**
- Training and Workshops:
  - Experience and Insights Workshop (11/09/2024)
  - National Educational Technology Integration Workshop (28/09/2024)
- Community Projects:
  - Orphanage Courses (09/2024-06/2025)
  - Student Social Activities
  - K-12 Course Poster Exhibition
""",
    
     'ku': """
بەشی پەروەردەی کۆمپیوتەر

**زانیاری پەیوەندی:**
- ئیمەیڵ: ced@tiu.edu.iq
- تەلەفۆنی فاکەڵتی: +964 750 330 24 92
- تەلەفۆنەکانی کەمپەس:
  - +964 (0) 750 835 7525
  - +964 (0) 750 705 0211
- ناونیشان: شەقامی 100 مەتری و ڕێگای موسڵ، هەولێر، هەرێمی کوردستان، عێراق
- بینا: بینای پەروەردە

**بەراوردی بەش:**
- ئامانج: جیاواز لە IT یان ئەندازیاری کۆمپیوتەر، بەشەکەمان تایبەتمەندە لە ئامادەکردنی مامۆستایانی شارەزای کۆمپیوتەر لەگەڵ پێدانی پەروەردەیەکی تەواو لە گەشەپێدانی سۆفتوێر.
- ڕێڕەوی پیشەیی: سەرەکی تەرکیز دەکاتە سەر بەرهەمهێنانی مامۆستایانی شارەزای پەروەردەی کۆمپیوتەر، لەگەڵ لێهاتوویی زیادە لە گەشەپێدانی سۆفتوێر.
- مەرجەکانی وەرگرتن: پێویست بە تاقیکردنەوەی ئینگلیزی ناکات، بە پێچەوانەی بەشەکانی IT و ئەندازیاری کۆمپیوتەر.
- سوودە داراییەکان: سیستەمی داشکاندنی تایبەت (٢٥-٩٠٪ بەپێی نمرەکان) کە لە بەشەکانی IT و ئەندازیاری کۆمپیوتەر بەردەست نییە.
- شێوازی پەروەردەیی: تێکەڵکردنی ڕاهێنانی پەروەردەیی لەگەڵ شارەزاییەکانی زانستی کۆمپیوتەر.

**مەرجەکانی وەرگرتن:**
- نمرەی ئەکادیمی پێویست: قوتابیانی کە نمرەی ٥٥٪‌یان لە پۆلی ١٢ بەدەست هێناوە
- تاقیکردنەوەی وەرگرتن: پێویست بە هیچ تاقیکردنەوەیەک ناکات بۆ بەشی کۆمپیوتەر
- کۆرسی پێشوەخت: هیچ
- دوا وادەی پێشکەشکردن: ١٢ی کانونی یەکەم، ٢٠٢٤
- پرۆسەی پێشکەشکردن: سەردانی TIU بکە بۆ وەرگرتنی فۆرم، پڕی بکەرەوە و پێشکەشی وەزارەتی پەروەردەی بکە

**پرۆگرامی خوێندن و کۆرسەکان:**
ساڵی یەکەم:
- وەرزی پایز (٢٠ کرێدت، ٣٠ ECTS):
  - کارامەیی کۆمپیوتەر I
  - بیرکاری بۆ زانستی کۆمپیوتەر I
  - کۆرسە سەرەتاییەکان
- وەرزی بەهار (٢١ کرێدت، ٣٠ ECTS):
  - کارامەیی کۆمپیوتەر II
  - بیرکاری بۆ زانستی کۆمپیوتەر II
  - کارامەیی پێشکەوتوو

ساڵی دووەم:
- وەرزی پایز (١٨ کرێدت، ٣٠ ECTS):
  - ناساندنی بەرنامەسازی
  - داتابەیسەکان
- وەرزی بەهار (١٨ کرێدت، ٣٠ ECTS):
  - بەرنامەسازی پێشکەوتوو
  - بەڕێوەبردنی داتابەیس

ساڵی سێیەم:
- وەرزی پایز (١٧ کرێدت، ٣٠ ECTS):
  - پەرەپێدانی ڕەقەکاڵا و وێب
- وەرزی بەهار (١٧ کرێدت، ٣٠ ECTS):
  - تۆڕکردن و شێوازی وانەوتنەوە

ساڵی چوارەم:
- وەرزی پایز (١٦ کرێدت، ٣٠ ECTS):
  - بەڕێوەبردنی پرۆژە و توێژینەوە
- وەرزی بەهار (٢١ کرێدت، ٣٠ ECTS):
  - پراکتیکی وانەوتنەوە و پڕۆژەی کۆتایی

کۆی گشتی ئاماری پرۆگرامەکە:
- کۆی گشتی کرێدت: ١٤٨
- کۆی گشتی ECTS: ٢٤٠
- ماوە: ٨ وەرز
- پێکهاتەی تیۆری و پراکتیکی هاوسەنگ

**ستافی ئەکادیمی:**
- بەڕێوەبردن لەلایەن د. محەمەد ئەنوەر
- مامۆستایان بریتین لە خاتوو سلڤەر عەبدولعەزیز، خاتوو نەرمین محەمەد، خاتوو سایا حەسەن، کاک ڕێبین م.ئەحمەد، و کاک عیماد ڕەفیق
- مامۆستای یاریدەدەر بریتین لە بەڕێز ئەحمەد عەلی، خاتوو یارا ئەرجومان، خاتوو فیردەوس، کاک عەبدولڕەحمان
- پسپۆڕی: گەشەپێدانی وێب، ئەپڵیکەیشنی مۆبایل، AI، بینینی کۆمپیوتەر، R&D، پرۆگرامینگ
- دەستگەیشتن: کاتژمێری تایبەتی ئۆفیس، کاتی ڕاوێژکاری هەفتانە، خولی ڕاهێنان، وۆرکشۆپ

**ئامرازەکان:**
- تاقیگەکان: تاقیگەی ڕۆبۆتیکس، تاقیگەی گشتی کۆمپیوتەر
- کتێبخانە: کراوەیە بۆ هەموو قوتابیان
- دەستگەیشتن بە کۆمپیوتەر: بەردەستە لە دەرەوەی کاتی وانەکان
- ئامرازە زیادەکان: ژووری تایبەتی خوێندن یان شوێنی گشتی نییە

**هەلی کار:**
پۆستەکانی وانەوتنەوە:
- مامۆستای زمانی کۆمپیوتەر
- مامۆستای باڵا
- یاریدەدەری تاقیگە/ڕاهێنەر
- ڕاهێنەری مامۆستا
- ڕاوێژکاری پەروەردەیی

خاوەنکارە ئەگەرییەکان:
- قوتابخانە حکومییەکان
- قوتابخانە ئەهلیەکان
- زانکۆ و پەیمانگاکان
- فەرمانگەکانی دەوڵەت
- کۆمپانیا تایبەتەکان

**ژیانی قوتابیان:**
- یانە و ڕێکخراوەکان: بەڕێوەدەبرێت لەلایەن ڕاگری قوتابیان
- چالاکییە بەردەوامەکان: وۆرکشۆپی ڕۆبۆتیکس، وۆرکشۆپی AI، فێستیڤاڵی کلتووری، ڕووداوی نەیریک
- کلتووری کۆمەڵگا: نزیک و خێزان-ئاسا
**چالاکییەکانی بەش (٢٠٢٤-٢٠٢٥):**
- ڕاهێنان و وۆرکشۆپ:
  - وۆرکشۆپی ئەزموون و تێڕوانینەکان (11/09/2024)
  - وۆرکشۆپی نیشتمانی یەکخستنی تەکنەلۆژیای پەروەردەیی (28/09/2024)
- پڕۆژەی کۆمەڵایەتی:
  - خولی ماڵی هەتیوەکان (09/2024-06/2025)
  - چالاکی کۆمەڵایەتی قوتابیان
  - پێشانگای پۆستەری خولی K-12
- چالاکی ئەکادیمی:
  - سەردانی قوتابخانەکان لە کەرکوک
  - سەردانی کۆمپانیاکان
  - پێشبڕکێی ڕۆبۆتیک/OOP

**وۆرکشۆپی نێودەوڵەتی:**
- وۆرکشۆپی ئاسایشی IoT:
  - فۆکەس لەسەر ئاسایشی ئینتەرنێتی شتەکان
  - پانتایی نێودەوڵەتی
  - کارامەیی پەیوەندیدار بە پیشەسازی
  - دەرفەتی گەشەپێدانی پیشەیی
""",

    'ar': """
قسم تعليم الحاسوب

**معلومات الاتصال:**
- البريد الإلكتروني: ced@tiu.edu.iq
- هاتف الكلية: +964 750 330 24 92
- هواتف الحرم الجامعي:
  - +964 (0) 750 835 7525
  - +964 (0) 750 705 0211
- العنوان: شارع 100 متر وطريق الموصل، أربيل، إقليم كردستان، العراق
- المبنى: مبنى التربية

**مقارنة القسم:**
- التركيز: على عكس تكنولوجيا المعلومات أو هندسة الحاسوب، يتخصص قسمنا في إعداد معلمي حاسوب ماهرين مع تقديم تعليم شامل في تطوير البرمجيات.
- المسار المهني: التركيز الأساسي على إنتاج معلمين مؤهلين لتعليم الحاسوب، مع كفاءة إضافية في تطوير البرمجيات.
- متطلبات القبول: لا يشترط امتحان اللغة الإنجليزية، على عكس أقسام تكنولوجيا المعلومات وهندسة الحاسوب.
- المزايا المالية: نظام خصم فريد (25-90% حسب الدرجات) غير متوفر في أقسام تكنولوجيا المعلومات وهندسة الحاسوب.
- النهج التعليمي: يجمع بين التدريب التربوي ومهارات علوم الحاسوب.

**متطلبات القبول:**
- الدرجة الأكاديمية المطلوبة: الطلاب الحاصلون على درجة أعلى من 55 من 100 في الصف الثاني عشر مؤهلون.
- امتحانات القبول: لا توجد امتحانات قبول مطلوبة لتعليم الحاسوب.
- المتطلبات المسبقة: لا يوجد.
- الموعد النهائي للتقديم: 12 ديسمبر 2024.
- عملية التقديم: زيارة TIU للحصول على استمارة، ملؤها، اختيار تعليم الحاسوب، وتقديمها إلى وزارة التربية.

**المنهج والمواد الدراسية:**
السنة الأولى:
- الفصل الخريفي (20 ساعة معتمدة، 30 ECTS):
  - مهارات الحاسوب I
  - الرياضيات لعلوم الحاسوب I
  - المواد الأساسية
- الفصل الربيعي (21 ساعة معتمدة، 30 ECTS):
  - مهارات الحاسوب II
  - الرياضيات لعلوم الحاسوب II
  - المهارات المتقدمة

السنة الثانية:
- الفصل الخريفي (18 ساعة معتمدة، 30 ECTS):
  - مقدمة في البرمجة
  - قواعد البيانات
- الفصل الربيعي (18 ساعة معتمدة، 30 ECTS):
  - البرمجة المتقدمة
  - إدارة قواعد البيانات

السنة الثالثة:
- الفصل الخريفي (17 ساعة معتمدة، 30 ECTS):
  - تطوير الأجهزة والويب
- الفصل الربيعي (17 ساعة معتمدة، 30 ECTS):
  - الشبكات ومنهجية التدريس

السنة الرابعة:
- الفصل الخريفي (16 ساعة معتمدة، 30 ECTS):
  - إدارة المشاريع والبحث
- الفصل الربيعي (21 ساعة معتمدة، 30 ECTS):
  - التدريب العملي والمشاريع النهائية

إحصائيات البرنامج الإجمالية:
- مجموع الساعات المعتمدة: 148
- مجموع ECTS: 240
- المدة: 8 فصول دراسية
- توازن بين المكونات النظرية والعملية

**هيئة التدريس:**
- يقود القسم الدكتور محمد أنور
- المدرسون هم السيدة سلفار عبد العزيز، السيدة نرمين محمد، السيدة سايا حسن، السيد ريبين م. أحمد، والسيد عماد رفيق
- المدرسون المساعدون هم السيد أحمد علي، السيدة يارا أرجومان، السيدة فردوس، السيد عبد الرحمن
- الخبرات: تطوير الويب، تطبيقات الموبايل، الذكاء الاصطناعي، رؤية الحاسوب، البحث والتطوير، البرمجة
- إمكانية الوصول: ساعات مكتبية مخصصة، ساعات استشارية أسبوعية، دورات تدريبية، ورش عمل

**المرافق:**
- المختبرات: مختبر الروبوتات، مختبر الحاسوب العام
- المكتبة: متاحة لجميع الطلاب
- الوصول إلى الحاسوب: متاح خارج ساعات الدراسة
- المرافق الإضافية: لا توجد غرف دراسة خاصة أو مناطق عامة محددة

**الفرص المهنية:**
المناصب التدريسية:
- معلم لغة الحاسوب
- معلم أول
- مساعد مختبر/مدرب
- مدرب المعلمين
- مستشار تربوي

جهات التوظيف المحتملة:
- المدارس الحكومية
- المدارس الخاصة
- الجامعات والمعاهد
- المكاتب الحكومية
- الشركات الخاصة

**الحياة الطلابية:**
- النوادي والمنظمات: تدار من قبل عميد شؤون الطلاب
- الفعاليات المنتظمة: ورش عمل الروبوتات، ورش عمل الذكاء الاصطناعي، المهرجانات الثقافية، فعالية نايريك
- ثقافة المجتمع: مترابطة وعائلية

**أنشطة القسم (2024-2025):**
- التدريب وورش العمل:
  - ورشة عمل الخبرات والرؤى (11/09/2024)
  - ورشة عمل وطنية حول تكامل التكنولوجيا التعليمية (28/09/2024)
- المشاريع المجتمعية:
  - دورات دار الأيتام (09/2024-06/2025)
  - الأنشطة الاجتماعية للطلاب
  - معرض ملصقات الدورات K-12
- الأنشطة الأكاديمية:
  - زيارات المدارس في كركوك
  - زيارات الشركات
  - مسابقات الروبوتات/البرمجة الكائنية

**ورش العمل الدولية:**
- ورشة عمل أمن إنترنت الأشياء:
  - التركيز على أمن إنترنت الأشياء
  - النطاق الدولي
  - المهارات المرتبطة بالصناعة
  - فرصة التطوير المهني
"""
}


CHATBOT_IDENTITY = {
    'en': {
        'introduction': """I am the AI assistant for the Computer Education Department at TISHK International University. I can help you with:
- Information about our academic programs and courses
- Admission requirements and application process
- Department facilities and resources
- Faculty and staff information
- Career opportunities and job prospects
- Student life and activities
- Upcoming events and workshops
- Contact information and general inquiries""",
        
        'capabilities': """I can assist you with:
1. Answering questions about the Computer Education Department
2. Providing detailed information about courses and curriculum
3. Explaining admission requirements and discounts
4. Sharing faculty and staff information
5. Describing facilities and resources
6. Informing about career opportunities
7. Providing information about student activities and events
8. Offering guidance about the application process
9. Sharing contact information and directions

Feel free to ask any questions in English, Kurdish (کوردی), or Arabic (العربية)!""",
        
        'greetings': {
            'hello': "Hello! I'm the Computer Education Department's AI assistant. How can I help you today?",
            'hi': "Hi there! I'm here to help you with information about the Computer Education Department. What would you like to know?",
            'hey': "Hey! I'm the department's AI assistant. How can I assist you?",
            'good_morning': "Good morning! I'm here to help with any questions about the Computer Education Department.",
            'good_afternoon': "Good afternoon! How can I assist you with information about our department?",
            'good_evening': "Good evening! I'm here to help with any questions about the Computer Education Department."
        }
    },
    
    'ku': {
        'introduction': """من یاریدەدەری زیرەکی دەستکردم بۆ بەشی پەروەردەی کۆمپیوتەر لە زانکۆی نێودەوڵەتی تیشک. دەتوانم یارمەتیت بدەم سەبارەت بە:
- زانیاری دەربارەی پرۆگرامە ئەکادیمی و کۆرسەکانمان
- مەرجەکانی وەرگرتن و پرۆسەی پێشکەشکردن
- ئامرازەکان و سەرچاوەکانی بەش
- زانیاری مامۆستایان و ستاف
- دەرفەتەکانی کار و ئایندەی پیشەیی
- ژیانی قوتابیان و چالاکییەکان
- ڕووداو و وۆرکشۆپە داهاتووەکان
- زانیاری پەیوەندی و پرسیارە گشتییەکان""",
        
        'capabilities': """دەتوانم یارمەتیت بدەم لە:
١. وەڵامدانەوەی پرسیارەکان دەربارەی بەشی پەروەردەی کۆمپیوتەر
٢. پێدانی زانیاری ورد دەربارەی کۆرسەکان و مەنهەج
٣. ڕوونکردنەوەی مەرجەکانی وەرگرتن و داشکاندنەکان
٤. هاوبەشکردنی زانیاری مامۆستایان و ستاف
٥. وەسفکردنی ئامرازەکان و سەرچاوەکان
٦. ئاگادارکردنەوە دەربارەی دەرفەتەکانی کار
٧. پێدانی زانیاری دەربارەی چالاکییەکانی قوتابیان و ڕووداوەکان
٨. پێشکەشکردنی ڕێنمایی دەربارەی پرۆسەی پێشکەشکردن
٩. هاوبەشکردنی زانیاری پەیوەندی و ئاراستەکان

دەتوانیت پرسیار بکەیت بە زمانی کوردی، ئینگلیزی، یان عەرەبی!""",
        
        'greetings': {
            'hello': "سڵاو! من یاریدەدەری زیرەکی دەستکردی بەشی پەروەردەی کۆمپیوتەرم. چۆن دەتوانم یارمەتیت بدەم ئەمڕۆ؟",
            'hi': "سڵاو! من لێرەم بۆ یارمەتیدانت دەربارەی زانیاری بەشی پەروەردەی کۆمپیوتەر. چی دەتەوێت بزانیت؟",
            'good_morning': "بەیانیت باش! من لێرەم بۆ وەڵامدانەوەی هەر پرسیارێک دەربارەی بەشی پەروەردەی کۆمپیوتەر.",
            'good_afternoon': "ڕۆژباش! چۆن دەتوانم یارمەتیت بدەم سەبارەت بە زانیاری بەشەکەمان؟",
            'good_evening': "ئێوارەتان باش! من لێرەم بۆ یارمەتیدان لە هەر پرسیارێک دەربارەی بەشی پەروەردەی کۆمپیوتەر."
        }
    },
    
    'ar': {
        'introduction': """أنا المساعد الذكي لقسم تعليم الحاسوب في جامعة تيشك الدولية. يمكنني مساعدتك في:
- معلومات عن برامجنا الأكاديمية والمقررات
- متطلبات القبول وعملية التقديم
- مرافق وموارد القسم
- معلومات عن أعضاء هيئة التدريس والموظفين
- الفرص المهنية وآفاق العمل
- الحياة الطلابية والأنشطة
- الفعاليات وورش العمل القادمة
- معلومات الاتصال والاستفسارات العامة""",
        
        'capabilities': """يمكنني المساعدة في:
١. الإجابة عن الأسئلة حول قسم تعليم الحاسوب
٢. تقديم معلومات مفصلة عن المقررات والمنهج
٣. شرح متطلبات القبول والخصومات
٤. مشاركة معلومات أعضاء هيئة التدريس والموظفين
٥. وصف المرافق والموارد
٦. الإعلام عن الفرص المهنية
٧. تقديم معلومات عن الأنشطة الطلابية والفعاليات
٨. تقديم التوجيه حول عملية التقديم
٩. مشاركة معلومات الاتصال والاتجاهات

يمكنك طرح الأسئلة باللغة العربية أو الكردية أو الإنجليزية!""",
        
        'greetings': {
            'hello': "مرحباً! أنا المساعد الذكي لقسم تعليم الحاسوب. كيف يمكنني مساعدتك اليوم؟",
            'hi': "أهلاً! أنا هنا لمساعدتك بالمعلومات عن قسم تعليم الحاسوب. ماذا تريد أن تعرف؟",
            'good_morning': "صباح الخير! أنا هنا للمساعدة في أي أسئلة عن قسم تعليم الحاسوب.",
            'good_afternoon': "مساء الخير! كيف يمكنني مساعدتك بمعلومات عن قسمنا؟",
            'good_evening': "مساء الخير! أنا هنا للمساعدة في أي أسئلة عن قسم تعليم الحاسوب."
        }
    }
}

# Add this function to detect greeting and identity questions
def detect_question_type(question, language):
    # Convert question to lowercase for easier matching
    question_lower = question.lower()
    
    # Common patterns for each language
    patterns = {
         'en': {
            'identity': [
                'who are you', 'what are you', 'who is this', 'what is this', 
                'introduce yourself', 'who am i talking to', 'what do you do',
                'tell me about yourself', 'what kind of assistant'
            ],
            'capabilities': [
                'what can you do', 'how can you help', 'what do you do', 
                'what are your capabilities', 'what are you able to', 'help me with',
                'what kind of questions', 'what type of information'
            ],
            'greetings': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
                'good evening', 'greetings', 'howdy', 'hi there'
            ]
        },
        'ku': {
            'identity': ['تۆ کێیت', 'ئەتو کێیت', 'خۆت بناسێنە', 'خۆت پێ بناسێنە'],
            'capabilities': ['چی دەتوانیت', 'چۆن دەتوانیت یارمەتی بدەیت', 'چی دەکەیت'],
            'greetings': ['سڵاو', 'بەیانی باش', 'ڕۆژباش', 'ئێوارە باش']
        },
        'ar': {
            'identity': ['من أنت', 'ما هذا', 'عرف عن نفسك', 'من انت'],
            'capabilities': ['ماذا تستطيع أن تفعل', 'كيف يمكنك المساعدة', 'ما هي قدراتك'],
            'greetings': ['مرحبا', 'السلام عليكم', 'صباح الخير', 'مساء الخير']
        }
    }
    
    # Check each pattern
    for question_type, pattern_list in patterns.get(language, patterns['en']).items():
        if any(pattern in question_lower for pattern in pattern_list):
            return question_type
            
    return None

# Enhanced FAQ data with more questions and categories
FAQ_DATA = {
    'en': [
        {
            'category': 'admission',
            'question': 'What are the admission requirements?',
            'answer': 'Students need to score above 55 out of 100 in 12th grade. No entrance exams are required.'
        },
        {
            'category': 'admission',
            'question': 'What discounts are available?',
            'answer': '25% discount for marks 55-60, 75% for marks 60-75, and 90% for marks above 75.'
        },
        {
            'category': 'courses',
            'question': 'How long is the program?',
            'answer': 'The program is 4 years long, with different specialized courses each year.'
        },
        {
            'category': 'facilities',
            'question': 'What facilities are available?',
            'answer': 'We have Robotics Lab, General Computer Lab, and library facilities.'
        },
        {
    'category': 'comparison',
    'question': 'How is this department different from IT or Computer Engineering?',
    'answer': 'Our department focuses on preparing computer teachers while also providing software development education. We don\'t require English exams for admission and offer unique grade-based discounts (25-90%). Our program combines teaching skills with technical computer knowledge.'
}
    ],
    'ku': [
        {
            'category': 'admission',
            'question': 'مەرجەکانی وەرگرتن چین؟',
            'answer': 'قوتابیان پێویستە نمرەی سەرو ٥٥٪‌یان لە پۆلی ١٢ هەبێت. پێویست بە هیچ تاقیکردنەوەیەکی وەرگرتن ناکات.'
        },
        {
            'category': 'admission',
            'question': 'چ داشکاندنێک هەیە؟',
            'answer': '٢٥٪ داشکاندن بۆ نمرەی ٥٥-٦٠، ٧٥٪ بۆ نمرەی ٦٠-٧٥، و ٩٠٪ بۆ نمرەی سەروو ٧٥.'
        },
        {
            'category': 'courses',
            'question': 'ماوەی خوێندن چەندە؟',
            'answer': 'بەرنامەکە ٤ ساڵە، لەگەڵ کۆرسی تایبەت لە هەر ساڵێکدا.'
        },
        {
            'category': 'facilities',
            'question': 'چ ئامرازێک هەیە؟',
            'answer': 'تاقیگەی ڕۆبۆتیکس، تاقیگەی گشتی کۆمپیوتەر، و کتێبخانەمان هەیە.'
        },
        {
            'category': 'staff',
            'question': 'مامۆستایەکان لەم بەشە کێن؟',
            'answer': ' خاتوو سلڤەر عەبدولعەزیز، خاتوو نەرمین محەمەد، خاتوو سایا حەسەن، کاک ڕێبین م.ئەحمەد، و کاک عیماد ڕەفیق.'
        },
         {
            'category': 'staff',
            'question': 'سەرۆک بەش کێیە؟',
            'answer': 'دکتۆر محمد انور'
        },
         {
            'category': 'staff',
            'question': 'یاریدەدەری مامۆستایەکان کێن؟',
            'answer': '- مامۆستای یاریدەدەر بریتین لە بەڕێز ئەحمەد عەلی، خاتوو یارا ئەرجومان، خاتوو فیردەوس ، کاک عەبدولڕەحمان'
        },
        {
    'category': 'comparison',
    'question': 'جیاوازی ئەم بەشە لەگەڵ IT یان ئەندازیاری کۆمپیوتەر چییە؟',
    'answer': 'بەشەکەمان تەرکیز دەکاتە سەر ئامادەکردنی مامۆستایانی کۆمپیوتەر لەگەڵ پێدانی خوێندنی گەشەپێدانی سۆفتوێر. پێویستمان بە تاقیکردنەوەی ئینگلیزی نییە بۆ وەرگرتن و داشکاندنی تایبەتمان هەیە بەپێی نمرە (٢٥-٩٠٪). پرۆگرامەکەمان شارەزایی وانەوتنەوە لەگەڵ زانیاری تەکنیکی کۆمپیوتەر تێکەڵ دەکات.'
},
{
    'category': 'faculty',
    'question': 'مامۆستایەکان لەم بەشە کێن؟',
    'answer': ' خاتوو سلڤەر عەبدولعەزیز، خاتوو نەرمین محەمەد، خاتوو سایا حەسەن، کاک ڕێبین م.ئەحمەد، و کاک عیماد ڕەفیق.'
}

    ],
     'ar': [
        {
            'category': 'admission',
            'question': 'ما هي متطلبات القبول؟',
            'answer': 'يحتاج الطلاب إلى درجة أعلى من 55 من 100 في الصف الثاني عشر. لا توجد امتحانات قبول مطلوبة.'
        },
        {
            'category': 'admission',
            'question': 'ما هي الخصومات المتاحة؟',
            'answer': 'خصم 25٪ للدرجات 55-60، 75٪ للدرجات 60-75، و90٪ للدرجات فوق 75.'
        },
        {
            'category': 'courses',
            'question': 'كم مدة البرنامج؟',
            'answer': 'البرنامج مدته 4 سنوات، مع مواد متخصصة مختلفة في كل سنة.'
        },
        {
            'category': 'facilities',
            'question': 'ما هي المرافق المتوفرة؟',
            'answer': 'لدينا مختبر الروبوتات، مختبر الحاسوب العام، والمكتبة.'
        },
        {
            'category': 'comparison',
            'question': 'ما الفرق بين هذا القسم وأقسام تكنولوجيا المعلومات أو هندسة الحاسوب؟',
            'answer': 'يركز قسمنا على إعداد معلمي الحاسوب مع تقديم تعليم تطوير البرمجيات. لا نشترط امتحانات اللغة الإنجليزية للقبول ونقدم خصومات فريدة حسب الدرجات (25-90%). يجمع برنامجنا بين مهارات التدريس والمعرفة التقنية بالحاسوب.'
        }
    ]
}

def get_intent(question, language):
    # Categories with related keywords
    categories = {
        'en': {
            'admission': ['admission', 'requirements', 'apply', 'score', 'grade', 'deadline', 'discount', 'fee', 'tuition', 'cost', 'price'],
            'comparison': ['difference', 'different', 'compare', 'compared', 'vs', 'versus', 'IT', 'engineering', 'better', 'computer engineering'],
            'courses': ['course', 'subject', 'year', 'study', 'curriculum', 'programming', 'database', 'classes', 'learn'],
            'faculty': ['teacher', 'professor', 'dr', 'mrs', 'mr', 'staff', 'faculty', 'instructor', 'teach'],
            'facilities': ['lab', 'library', 'computer', 'room', 'facility', 'equipment', 'building', 'class'],
            'career': ['job', 'work', 'career', 'opportunity', 'internship', 'company', 'future', 'employment'],
            'student_life': ['club', 'event', 'activity', 'workshop', 'festival', 'social', 'student']
        },
        'ku': {
            'admission': ['وەرگرتن', 'مەرج', 'پێشکەشکردن', 'نمرە', 'کۆنمرە', 'داشکاندن', 'پارە', 'کرێ', 'تێچوو'],
            'courses': ['وانە', 'بابەت', 'ساڵ', 'خوێندن', 'پرۆگرام', 'کۆرس', 'فێربوون'],
            'comparison': ['جیاوازی', 'جیاواز', 'بەراورد', 'باشتر', 'ئەندازیاری', 'ئای تی'],
            'faculty': ['مامۆستا', 'دکتۆر', 'خاتوو', 'کاک', 'ستاف', 'وانەبێژ', 'پرۆفیسۆر'],
            'facilities': ['تاقیگە', 'کتێبخانە', 'کۆمپیوتەر', 'ژوور', 'ئامراز', 'بینا', 'پۆل'],
            'career': ['کار', 'وەزیفە', 'دەرفەت', 'ڕاهێنان', 'کۆمپانیا', 'داهاتوو', 'دامەزراندن'],
           'faculty': ['مامۆستا', 'دکتۆر', 'خاتوو', 'کاک', 'ستاف', 'وانەبێژ', 'پرۆفیسۆر'],
            'student_life': ['یانە', 'چالاکی', 'وۆرکشۆپ', 'فێستیڤاڵ', 'کۆمەڵایەتی', 'قوتابی']
        },
        'ar': {
            'admission': ['قبول', 'متطلبات', 'تقديم', 'درجة', 'علامة', 'موعد', 'خصم', 'رسوم', 'تكلفة', 'سعر'],
            'courses': ['مادة', 'موضوع', 'سنة', 'دراسة', 'منهج', 'برمجة', 'قواعد البيانات', 'صف', 'تعلم'],
            'faculty': ['مدرس', 'دكتور', 'سيد', 'سيدة', 'طاقم', 'كلية', 'محاضر', 'تدريس'],
            'facilities': ['مختبر', 'مكتبة', 'حاسوب', 'غرفة', 'مرفق', 'معدات', 'مبنى', 'صف'],
            'career': ['وظيفة', 'عمل', 'مهنة', 'فرصة', 'تدريب', 'شركة', 'مستقبل', 'توظيف'],
            'comparison': ['فرق', 'مقارنة', 'مختلف', 'أفضل', 'هندسة', 'تكنولوجيا المعلومات'],
            'student_life': ['نادي', 'فعالية', 'نشاط', 'ورشة', 'مهرجان', 'اجتماعي', 'طالب']
        }
    }
    
    question_lower = question.lower()
    detected_categories = []
    
    # Detect categories from question
    for category, keywords in categories[language].items():
        if any(keyword.lower() in question_lower for keyword in keywords):
            detected_categories.append(category)
    
    return detected_categories

def get_focused_answer(question, categories, department_data, language):
    if not categories:
        return None
        
    focused_data = ""
    
    # Map categories to sections in the department data
    section_mapping = {
        'admission': ['**Admissions Requirements:**', '**Tuition Discounts:**'],
        'courses': ['**Curriculum & Courses:**'],
        'faculty': ['**Faculty:**'],
        'faculty': ['**ستافی ئەکادیمی:**'],
        'facilities': ['**Facilities:**'],
        'career': ['**Career Opportunities:**'],
        'student_life': ['**Student Life:**', '**Unique Programs:**']
    }
    
    # Extract relevant sections based on detected categories
    for category in categories:
        sections = section_mapping.get(category, [])
        for section in sections:
            if section in department_data:
                section_start = department_data.find(section)
                next_section = department_data.find('**', section_start + len(section))
                if next_section == -1:
                    section_content = department_data[section_start:]
                else:
                    section_content = department_data[section_start:next_section]
                focused_data += section_content + "\n\n"
    
    return focused_data.strip()

def get_relevant_faqs(question, categories, language):
    relevant_faqs = []
    for faq in FAQ_DATA[language]:
        if faq['category'] in categories:
            relevant_faqs.append(f"Q: {faq['question']}\nA: {faq['answer']}")
    return "\n\n".join(relevant_faqs)

def log_interaction(question, answer, language, categories=None):
    """Log interactions with categories"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] [{language}]")
        if categories:
            f.write(f" [Categories: {', '.join(categories)}]")
        f.write(f"\nQ: {question}\nA: {answer}\n{'='*50}")

@app.route('/')
def index():
    return render_template('index.html')

# Modified ask_claude route to include database integration
# app.py
from knowledge_base import encode_knowledge_base

# Initialize the knowledge base embeddings

@app.route('/ask-claude', methods=['POST'])
def ask_claude():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        language = data.get("language", "en")

        if not question:
            error_messages = {
                "en": "Please provide a question.",
                "ku": "تکایە پرسیارێک بنووسە.",
                "ar": "الرجاء طرح سؤال."
            }
            return jsonify({"response": error_messages[language]}), 400

        # Encode the user's question
        question_embedding = model.encode([question])[0]

        # Use the RAG model to retrieve relevant information
        rag_response = client.create_chat_completion(
            model="claude-v1-rag",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": question}
            ],
            knowledge_base=knowledge_base_embeddings,
            query_embedding=question_embedding
        )

        # Combine the RAG-retrieved information with the language model's generation
        final_response = f"{rag_response.choices[0].message.content}\n\n{response.content[0].text}"

        # Save the message to the database
        save_message(question, final_response, language, None, None)
        log_interaction(question, final_response, language)

        return jsonify({"response": final_response})

    except Exception as e:
        print(f"Error in ask_claude: {str(e)}")
        error_messages = {
            "en": f"Error: {str(e)}",
            "ku": f"هەڵە: {str(e)}",
            "ar": f"خطأ: {str(e)}"
        }
        return jsonify({"response": error_messages.get(language, error_messages["en"])}), 500

# New dashboard routes# Add this updated dashboard route to your code
@app.route('/dashboard')
def dashboard():
    try:
        conn = sqlite3.connect('chatbot.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        c = conn.cursor()
        
        # Get message statistics
        c.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT CASE WHEN language = 'en' THEN id END) as en_count,
                COUNT(DISTINCT CASE WHEN language = 'ku' THEN id END) as ku_count,
                COUNT(DISTINCT CASE WHEN language = 'ar' THEN id END) as ar_count,
                COUNT(DISTINCT DATE(timestamp)) as days_active
            FROM messages
        ''')
        stats = c.fetchone()
        
        # Get recent messages
        c.execute('''
            SELECT id, timestamp, user_message, bot_response, language, categories, question_type
            FROM messages
            ORDER BY timestamp DESC
        ''')
        messages = c.fetchall()
        
        conn.close()
        
        return render_template(
            'dashboard.html',
            messages=messages,
            stats={
                'total': stats['total'],
                'en_count': stats['en_count'],
                'ku_count': stats['ku_count'],
                'ar_count': stats['ar_count'],
                'days_active': stats['days_active']
            }
        )
        
    except Exception as e:
        print(f"Error in dashboard: {str(e)}")
        return str(e)

# Also add this debug route to check if CHATBOT_IDENTITY is properly loaded
@app.route('/debug-identity', methods=['GET'])
def debug_identity():
    return jsonify({
        "status": "ok",
        "chatbot_identity": CHATBOT_IDENTITY
    })
@app.route('/delete-message/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    try:
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        c.execute('DELETE FROM messages WHERE id = ?', (message_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# Add this function to your code to create the content prompt
def create_content_prompt(question, detected_categories, department_data, language):
    """Create the content prompt for Claude based on detected categories"""
    if detected_categories:
        focused_content = get_focused_answer(question, detected_categories, department_data, language)
        relevant_faqs = get_relevant_faqs(question, detected_categories, language)
        
        return f"""
        Department Information:
        {focused_content}
        
        Relevant FAQs:
        {relevant_faqs}
        
        Question: {question}
        
        Please provide a focused answer to the question using the above information."""
    else:
        return f"""
        General Question: {question}
        
        Please provide a helpful response based on the department information."""
# Replace your chat history route with this updated version
@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    try:
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        
        # Get all messages ordered by timestamp
        c.execute('''
            SELECT id, timestamp, user_message, bot_response, language, categories, question_type
            FROM messages
            ORDER BY timestamp DESC
        ''')
        
        # Fetch all rows and convert to list of dicts
        rows = c.fetchall()
        formatted_messages = []
        
        for row in rows:
            formatted_messages.append({
                'id': row[0],
                'timestamp': row[1],
                'user_message': row[2],
                'bot_response': row[3],
                'language': row[4],
                'categories': row[5].split(',') if row[5] else [],
                'question_type': row[6]
            })
        
        conn.close()
        
        print("Sending messages:", formatted_messages) # Debug print
        return jsonify({'history': formatted_messages})
    
    except Exception as e:
        print(f"Error in get_chat_history: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    
    
# Modify your initialization code at the bottom of the file:
if __name__ == '__main__':
    setup_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"Server starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)  