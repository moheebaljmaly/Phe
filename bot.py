import os
import time
import telebot
from telebot import types
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import io
import logging

# إعداد التسجيل (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تكوين إعادة المحاولات لطلبات HTTP
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http_session = requests.Session()
http_session.mount("https://", adapter)
http_session.mount("http://", adapter)
telebot.apihelper.SESSION = http_session

# تعيين مهلة أطول للاتصال
telebot.apihelper.READ_TIMEOUT = 120
telebot.apihelper.CONNECT_TIMEOUT = 120

TOKEN = "7897641659:AAHazUeZDIRJaf5HlTSehwKKtT-m84NLXTg"  # ضع هنا توكن البوت الخاص بك
bot = telebot.TeleBot(TOKEN)

# معرف المالك
OWNER_ID = 7080150296
OWNER_USERNAME = "@YI_IB"

# تعريف هيكل المجلدات والأقسام
BASE_FOLDER = "pdfs"
DEPARTMENTS = {
    "تكنولوجيا المعلومات": "it"
}
YEARS = {
    "السنة الأولى": "1",
    "السنة الثانية": "2",
    "السنة الثالثة": "3",
    "السنة الرابعة": "4"
}

# إضافة قائمة المواد الدراسية
SUBJECTS = {
    "it": {  # تكنولوجيا المعلومات
        "1": {  # السنة الأولى
            "c++": "cpp",
            "رياضيات": "math",
            "كتابة": "writing",
            "تصميم منطقي": "logic_design",
            "محادثة": "speaking",
            "ثقافة إسلامية": "islamic"
        },
        "2": {  # السنة الثانية
            "برمجة الويب": "web",
            "قواعد البيانات": "database",
            "هياكل البيانات": "data_structures",
            "نظم التشغيل": "os",
            "شبكات الحاسوب": "networks"
        },
        "3": {  # السنة الثالثة
            "تطوير تطبيقات الجوال": "mobile",
            "الذكاء الاصطناعي": "ai",
            "أمن المعلومات": "security",
            "تطوير برمجيات": "software_eng",
            "نظم موزعة": "distributed_systems"
        },
        "4": {  # السنة الرابعة
            "مشروع التخرج": "graduation_project",
            "تعلم الآلة": "machine_learning",
            "الحوسبة السحابية": "cloud_computing",
            "تحليل البيانات": "data_analysis",
            "أخلاقيات الحاسوب": "computer_ethics"
        }
    }
}

# حد أقصى لحجم الملف (50 ميجابايت)
MAX_FILE_SIZE = 50 * 1024 * 1024

# قائمة امتدادات الملفات المدعومة
SUPPORTED_EXTENSIONS = {
    'pdf': 'ملف PDF 📄',
    'doc': 'ملف Word 📝',
    'docx': 'ملف Word 📝',
    'xls': 'ملف Excel 📊',
    'xlsx': 'ملف Excel 📊',
    'ppt': 'ملف PowerPoint 📊',
    'pptx': 'ملف PowerPoint 📊',
    'txt': 'ملف نصي 📝',
    'jpg': 'صورة 🖼️',
    'jpeg': 'صورة 🖼️',
    'png': 'صورة 🖼️',
    'gif': 'صورة متحركة 🖼️',
    'mp3': 'ملف صوتي 🔊',
    'mp4': 'ملف فيديو 🎬',
    'zip': 'ملف مضغوط 📦',
    'rar': 'ملف مضغوط 📦'
}

# إنشاء هيكل المجلدات إذا لم يكن موجوداً
def create_folder_structure():
    if not os.path.exists(BASE_FOLDER):
        os.makedirs(BASE_FOLDER)
    
    for dept_name, dept_code in DEPARTMENTS.items():
        dept_path = os.path.join(BASE_FOLDER, dept_code)
        if not os.path.exists(dept_path):
            os.makedirs(dept_path)
        
        for year_name, year_code in YEARS.items():
            year_path = os.path.join(dept_path, year_code)
            if not os.path.exists(year_path):
                os.makedirs(year_path)
            
            # إنشاء مجلدات المواد داخل كل سنة دراسية
            for subject_name, subject_code in SUBJECTS[dept_code][year_code].items():
                subject_path = os.path.join(year_path, subject_code)
                if not os.path.exists(subject_path):
                    os.makedirs(subject_path)
                    logger.info(f"تم إنشاء مجلد المادة: {subject_path}")
                    
# دالة لإعادة تسمية المجلدات في السنوات 2، 3، 4
def rename_folders():
    try:
        logger.info("بدء عملية إعادة تسمية المجلدات...")
        
        for dept_name, dept_code in DEPARTMENTS.items():
            dept_path = os.path.join(BASE_FOLDER, dept_code)
            if os.path.exists(dept_path):
                # فقط السنوات 2، 3، 4
                for year_name, year_code in [(name, code) for name, code in YEARS.items() if code != "1"]:
                    year_path = os.path.join(dept_path, year_code)
                    if os.path.exists(year_path):
                        logger.info(f"معالجة مجلد: {year_path}")
                        
                        # نقوم بإنشاء المجلدات الجديدة أولاً
                        for subject_name, subject_code in SUBJECTS[dept_code][year_code].items():
                            subject_path = os.path.join(year_path, subject_code)
                            if not os.path.exists(subject_path):
                                os.makedirs(subject_path)
                                logger.info(f"تم إنشاء مجلد المادة: {subject_path}")
                        
                        # نحدد قائمة بأسماء المجلدات القديمة التي يجب حذفها (مثل cpp, speaking, islamic في السنوات 2، 3، 4)
                        # المجلدات غير المستخدمة في هذه السنة الدراسية
                        current_folders = os.listdir(year_path)
                        valid_subject_codes = [code for code in SUBJECTS[dept_code][year_code].values()]
                        
                        # نحذف المجلدات القديمة غير المستخدمة
                        for folder in current_folders:
                            folder_path = os.path.join(year_path, folder)
                            if os.path.isdir(folder_path) and folder not in valid_subject_codes:
                                # نتحقق إذا كان هناك ملفات في المجلد
                                if not os.listdir(folder_path):
                                    # المجلد فارغ، يمكن حذفه بأمان
                                    os.rmdir(folder_path)
                                    logger.info(f"تم حذف المجلد الفارغ: {folder_path}")
                                else:
                                    # المجلد يحتوي على ملفات، لا يمكن حذفه
                                    logger.warning(f"المجلد {folder_path} يحتوي على ملفات ولن يتم حذفه")
        
        logger.info("اكتملت عملية إعادة تسمية المجلدات بنجاح!")
        return True
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إعادة تسمية المجلدات: {e}")
        return False

# إنشاء هيكل المجلدات وإعادة تسمية المجلدات
create_folder_structure()
rename_folders()

# دالة مساعدة لإنشاء لوحة المفاتيح الرئيسية
def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    dept_btn = types.KeyboardButton("الأقسام 🏫")
    list_btn = types.KeyboardButton("قائمة الملفات 📚")
    search_btn = types.KeyboardButton("بحث عن ملف 🔍")
    help_btn = types.KeyboardButton("مساعدة ❓")
    markup.add(dept_btn, list_btn, search_btn, help_btn)
    return markup

# دالة لإنشاء لوحة مفاتيح الأقسام
def create_departments_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    for dept_name in DEPARTMENTS.keys():
        markup.add(types.KeyboardButton(dept_name))
    
    back_btn = types.KeyboardButton("العودة للقائمة الرئيسية 🔙")
    markup.add(back_btn)
    
    return markup

# دالة لإنشاء لوحة مفاتيح السنوات الدراسية
def create_years_keyboard(department):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    for year_name in YEARS.keys():
        markup.add(types.KeyboardButton(f"{year_name} - {department}"))
    
    back_btn = types.KeyboardButton("العودة للأقسام 🔙")
    home_btn = types.KeyboardButton("العودة للقائمة الرئيسية 🏠")
    markup.add(back_btn, home_btn)
    
    return markup

# دالة لإرسال رسائل مع التعامل مع الأخطاء
def safe_send_message(chat_id, text, reply_markup=None):
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إرسال الرسالة: {e}")
        time.sleep(3)  # انتظار قبل إعادة المحاولة
        try:
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
        except Exception as retry_e:
            logger.error(f"فشلت إعادة محاولة إرسال الرسالة: {retry_e}")
            return None

@bot.message_handler(commands=['start', 'keyboard'])
def send_welcome(message):
    markup = create_main_keyboard()
    
    welcome_msg = (
        f"مرحبًا {message.from_user.first_name}! 👋\n"
        "أنا بوت إرسال الملفات PDF والكتب والملخصات 📑\n\n"
        "يمكنك تصفح الملفات عبر الأقسام والسنوات الدراسية أو البحث عن ملف معين."
    )
    safe_send_message(message.chat.id, welcome_msg, reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_help(message):
    markup = create_main_keyboard()
    help_text = (
        "طريقة استخدام البوت:\n\n"
        "• اضغط على زر 'الأقسام' للتصفح حسب القسم والسنة الدراسية\n"
        "• اضغط على زر 'قائمة الملفات' لعرض جميع الملفات المتوفرة\n"
        "• استخدم زر 'بحث عن ملف' للبحث عن ملف معين\n"
        "• يمكنك أيضًا كتابة اسم الملف مباشرة للحصول عليه\n\n"
        "• استخدم /keyboard لإظهار لوحة المفاتيح إذا اختفت\n\n"
        f"للتواصل مع المسؤول للمساعدة: {OWNER_USERNAME}"
    )
    safe_send_message(message.chat.id, help_text, reply_markup=markup)

# معالج زر "الأقسام"
@bot.message_handler(func=lambda message: message.text == "الأقسام 🏫")
def show_departments(message):
    markup = create_departments_keyboard()
    safe_send_message(message.chat.id, "اختر القسم:", reply_markup=markup)

# معالج زر "العودة للقائمة الرئيسية"
@bot.message_handler(func=lambda message: message.text in ["العودة للقائمة الرئيسية 🔙", "العودة للقائمة الرئيسية 🏠"])
def back_to_main(message):
    markup = create_main_keyboard()
    safe_send_message(message.chat.id, "القائمة الرئيسية:", reply_markup=markup)

# معالج زر "العودة للأقسام"
@bot.message_handler(func=lambda message: message.text == "العودة للأقسام 🔙")
def back_to_departments(message):
    markup = create_departments_keyboard()
    safe_send_message(message.chat.id, "اختر القسم:", reply_markup=markup)

# معالج اختيار القسم
@bot.message_handler(func=lambda message: message.text in DEPARTMENTS.keys())
def show_years(message):
    department = message.text
    # تخزين القسم المختار
    if message.chat.id not in user_selections:
        user_selections[message.chat.id] = {}
    user_selections[message.chat.id]['department'] = department
    
    markup = create_years_keyboard(department)
    safe_send_message(message.chat.id, f"اختر السنة الدراسية لقسم {department}:", reply_markup=markup)

# معالج اختيار السنة الدراسية
@bot.message_handler(func=lambda message: check_year(message.text))
def show_department_year_subjects(message):
    # استخراج القسم والسنة من النص
    parts = message.text.split(" - ")
    if len(parts) >= 2:
        year_name = parts[0]
        department = parts[1]
        
        if year_name in YEARS and department in DEPARTMENTS:
            # تخزين السنة المختارة
            if message.chat.id not in user_selections:
                user_selections[message.chat.id] = {}
            user_selections[message.chat.id]['department'] = department
            user_selections[message.chat.id]['year'] = year_name
            
            # عرض المواد الدراسية لهذا القسم والسنة
            markup = create_subjects_keyboard(department, year_name)
            safe_send_message(
                message.chat.id, 
                f"اختر المادة الدراسية لقسم {department} - {year_name}:", 
                reply_markup=markup
            )

# دالة للتحقق من أن النص يحتوي على سنة دراسية
def check_year(text):
    for year_name in YEARS.keys():
        if f"{year_name} - " in text:
            return True
    return False

# معالج اختيار المادة الدراسية
@bot.message_handler(func=lambda message: check_subject(message.text))
def show_subject_files(message):
    # الحصول على المادة من النص مباشرة
    subject_name = message.text
    
    # التحقق من أن المستخدم قد اختار قسمًا وسنة
    if message.chat.id in user_selections and 'department' in user_selections[message.chat.id] and 'year' in user_selections[message.chat.id]:
        department = user_selections[message.chat.id]['department']
        year_name = user_selections[message.chat.id]['year']
        dept_code = DEPARTMENTS[department]
        year_code = YEARS[year_name]
        
        # التحقق مما إذا كانت المادة موجودة في هذا القسم والسنة
        if subject_name in SUBJECTS[dept_code][year_code]:
            subject_code = SUBJECTS[dept_code][year_code][subject_name]
            
            folder_path = os.path.join(BASE_FOLDER, dept_code, year_code, subject_code)
            
            # التأكد من وجود المجلد
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            markup = create_main_keyboard()
            list_files_in_folder(message, folder_path, f"ملفات {subject_name} - {department} - {year_name}", markup)
        else:
            markup = create_main_keyboard()
            safe_send_message(message.chat.id, f"المادة '{subject_name}' غير متوفرة في قسم {department} - {year_name}", reply_markup=markup)
    else:
        # إذا لم يختر المستخدم قسمًا وسنة، نعرض رسالة مناسبة
        markup = create_main_keyboard()
        safe_send_message(message.chat.id, "الرجاء اختيار القسم والسنة الدراسية أولاً.", reply_markup=markup)

# دالة للتحقق من أن النص يحتوي على مادة دراسية
def check_subject(text):
    # نتحقق لكل قسم وسنة
    for dept_code in DEPARTMENTS.values():
        for year_code in YEARS.values():
            if text in SUBJECTS[dept_code][year_code]:
                return True
    return False

# دالة لعرض الملفات في مجلد معين كأزرار
def list_files_in_folder(message, folder_path, title, markup=None):
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        # الحصول على جميع الملفات (وليس فقط PDF)
        all_files = os.listdir(folder_path)
        files = []
        file_paths = []  # لتخزين مسارات الملفات
        
        # تصفية الملفات التي لها امتدادات مدعومة فقط
        for file in all_files:
            extension = file.split('.')[-1].lower() if '.' in file else ''
            if extension in SUPPORTED_EXTENSIONS:
                files.append(file)
                file_paths.append(os.path.join(folder_path, file))
        
        if not files:
            safe_send_message(message.chat.id, f"لا توجد ملفات متوفرة في {title} حالياً.", reply_markup=markup)
            return
        
        # تخزين معلومات القسم والسنة والمادة الحالية للمستخدم
        # استخراج معلومات المسار
        path_parts = folder_path.split(os.path.sep)
        if len(path_parts) >= 3:
            try:
                dept_code = path_parts[-3]
                year_code = path_parts[-2]
                subject_code = path_parts[-1]
                
                # تخزين المعلومات في user_selections
                if message.chat.id not in user_selections:
                    user_selections[message.chat.id] = {}
                
                user_selections[message.chat.id]['current_folder'] = folder_path
                user_selections[message.chat.id]['dept_code'] = dept_code
                user_selections[message.chat.id]['year_code'] = year_code
                user_selections[message.chat.id]['subject_code'] = subject_code
                
                # تخزين مسارات الملفات المعروضة للرجوع إليها لاحقاً
                user_selections[message.chat.id]['displayed_files'] = file_paths
            except Exception as e:
                logger.error(f"خطأ في استخراج معلومات المسار: {e}")
        
        # إنشاء لوحة مفاتيح تحتوي على أزرار للملفات
        files_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        
        # إضافة أزرار للملفات
        for file in files:
            file_name = os.path.splitext(file)[0]
            extension = file.split('.')[-1].lower()
            file_type = SUPPORTED_EXTENSIONS.get(extension, "ملف")
            
            # إضافة اسم الملف كزر مع نوع الملف
            files_markup.add(types.KeyboardButton(f"{file_name}"))
        
        # إضافة أزرار للعودة
        back_btn = types.KeyboardButton("العودة للمواد 🔙")
        dept_btn = types.KeyboardButton("العودة للأقسام 🔙")
        home_btn = types.KeyboardButton("العودة للقائمة الرئيسية 🏠")
        files_markup.add(back_btn, dept_btn, home_btn)
        
        # إرسال رسالة مع لوحة المفاتيح الجديدة
        safe_send_message(message.chat.id, f"اختر ملفًا من {title}:", reply_markup=files_markup)
        
        # إرسال قائمة بالملفات المتاحة وأحجامها وأنواعها كرسالة إضافية
        file_list = f"الملفات المتوفرة في {title}:\n\n"
        for i, file in enumerate(files, 1):
            file_name = os.path.splitext(file)[0]
            extension = file.split('.')[-1].lower()
            file_type = SUPPORTED_EXTENSIONS.get(extension, "ملف")
            file_size = os.path.getsize(os.path.join(folder_path, file))
            file_size_mb = round(file_size / 1024 / 1024, 2)
            file_list += f"{i}. {file_name} - {file_type} ({file_size_mb} MB)\n"
        
        # إضافة تعليمات للمستخدم
        file_list += "\nيمكنك تنزيل الملف بكتابة اسمه أو رقمه في القائمة."
        
        safe_send_message(message.chat.id, file_list)
    except Exception as e:
        logger.error(f"خطأ في عرض الملفات: {e}")
        safe_send_message(message.chat.id, "حدث خطأ أثناء عرض الملفات.", reply_markup=markup)

# دالة لإنشاء لوحة مفاتيح المواد الدراسية
def create_subjects_keyboard(department, year):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # إضافة المواد الدراسية بشكل مباشر بدون إضافة اسم القسم والسنة
    dept_code = DEPARTMENTS[department]
    year_code = YEARS[year]
    
    for subject_name in SUBJECTS[dept_code][year_code].keys():
        markup.add(types.KeyboardButton(subject_name))
    
    back_btn = types.KeyboardButton("العودة للسنوات الدراسية 🔙")
    home_btn = types.KeyboardButton("العودة للقائمة الرئيسية 🏠")
    markup.add(back_btn, home_btn)
    
    return markup

@bot.message_handler(commands=['list'])
def list_files(message):
    markup = create_main_keyboard()
    list_all_files(message, markup)

def list_all_files(message, markup=None):
    all_files = []
    
    try:
        # جمع جميع الملفات من جميع المجلدات
        for dept_name, dept_code in DEPARTMENTS.items():
            for year_name, year_code in YEARS.items():
                for subject_name, subject_code in SUBJECTS[dept_code][year_code].items():
                    folder_path = os.path.join(BASE_FOLDER, dept_code, year_code, subject_code)
                    if os.path.exists(folder_path):
                        for file in os.listdir(folder_path):
                            extension = file.split('.')[-1].lower() if '.' in file else ''
                            if extension in SUPPORTED_EXTENSIONS:
                                file_path = os.path.join(folder_path, file)
                                file_size = os.path.getsize(file_path)
                                file_type = SUPPORTED_EXTENSIONS.get(extension, "ملف")
                                all_files.append({
                                    'name': os.path.splitext(file)[0],
                                    'path': file_path,
                                    'department': dept_name,
                                    'year': year_name,
                                    'subject': subject_name,
                                    'size': round(file_size / 1024 / 1024, 2),
                                    'type': file_type
                                })
        
        if not all_files:
            safe_send_message(message.chat.id, "لا توجد ملفات متوفرة حالياً.", reply_markup=markup)
            return
        
        file_list = "جميع الملفات المتوفرة:\n\n"
        for i, file in enumerate(all_files, 1):
            file_list += f"{i}. {file['name']} - {file['type']} - {file['subject']} - {file['department']} - {file['year']} ({file['size']} MB)\n"
            # تقسيم الرسالة إذا كانت طويلة جدًا
            if i % 50 == 0 and i < len(all_files):
                safe_send_message(message.chat.id, file_list)
                file_list = ""
        
        if file_list:
            file_list += "\nاكتب اسم الملف الذي تريد للحصول عليه."
            safe_send_message(message.chat.id, file_list, reply_markup=markup)
    except Exception as e:
        logger.error(f"خطأ في قائمة الملفات: {e}")
        safe_send_message(message.chat.id, "حدث خطأ أثناء قراءة قائمة الملفات.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "قائمة الملفات 📚")
def button_list_files(message):
    markup = create_main_keyboard()
    list_all_files(message, markup)

@bot.message_handler(commands=['search'])
def search_files(message):
    markup = create_main_keyboard()
    try:
        query = message.text.split(' ', 1)[1].strip()
        perform_search(message, query, markup)
    except IndexError:
        safe_send_message(message.chat.id, "الرجاء إدخال كلمة للبحث. مثال: /search شبكات", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "بحث عن ملف 🔍")
def button_search_prompt(message):
    markup = create_main_keyboard()
    search_msg = safe_send_message(message.chat.id, "أدخل كلمة للبحث:", reply_markup=markup)
    if search_msg:
        bot.register_next_step_handler(message, process_search_query)

def process_search_query(message):
    markup = create_main_keyboard()
    query = message.text.strip()
    perform_search(message, query, markup)

# دالة لحساب درجة التشابه بين نصين (تحسين للبحث الجزئي)
def calculate_similarity(text1, text2):
    # تحويل النصوص إلى حروف صغيرة
    text1 = text1.lower()
    text2 = text2.lower()
    
    # التحقق من الاحتواء المباشر (إذا كان النص الأول موجود في النص الثاني)
    if text1 in text2:
        # إذا كان النص الأول موجود بالكامل في النص الثاني، نعطي درجة تشابه عالية
        # كلما كان النص الأول أقرب في الطول من النص الثاني، كلما كانت درجة التشابه أعلى
        return 0.7 + 0.3 * (len(text1) / max(len(text2), 1))
    
    # إذا كانت كل كلمة من كلمات النص الأول موجودة في النص الثاني
    words1 = text1.split()
    if words1 and all(word in text2 for word in words1):
        return 0.6 + 0.2 * (len(text1) / max(len(text2), 1))
    
    # حساب التشابه باستخدام معامل جاكارد للأحرف
    set1 = set(text1)
    set2 = set(text2)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        return 0
    
    jaccard_similarity = intersection / union
    
    # حساب نسبة الأحرف المشتركة
    common_chars = sum(1 for c in text1 if c in text2)
    char_ratio = common_chars / max(len(text1), 1)
    
    # الجمع بين المقاييس المختلفة مع إعطاء وزن أكبر للأحرف المشتركة
    return 0.4 * jaccard_similarity + 0.6 * char_ratio

def perform_search(message, query, markup=None):
    try:
        global search_results
        all_files = []
        query = query.lower()
        min_similarity = 0.2  # تخفيض الحد الأدنى للتشابه لإظهار المزيد من النتائج
        
        # البحث في جميع المجلدات
        for dept_name, dept_code in DEPARTMENTS.items():
            for year_name, year_code in YEARS.items():
                for subject_name, subject_code in SUBJECTS[dept_code][year_code].items():
                    folder_path = os.path.join(BASE_FOLDER, dept_code, year_code, subject_code)
                    if os.path.exists(folder_path):
                        for file in os.listdir(folder_path):
                            file_name = os.path.splitext(file)[0].lower()
                            extension = file.split('.')[-1].lower() if '.' in file else ''
                            
                            # البحث المباشر (إذا كانت كلمة البحث موجودة في اسم الملف)
                            direct_match = query in file_name
                            
                            # حساب درجة التشابه بين كلمة البحث واسم الملف
                            similarity = calculate_similarity(query, file_name)
                            
                            # إضافة الملف إذا كان هناك تطابق مباشر أو درجة تشابه كافية
                            if extension in SUPPORTED_EXTENSIONS and (direct_match or similarity >= min_similarity):
                                file_path = os.path.join(folder_path, file)
                                file_size = os.path.getsize(file_path)
                                file_type = SUPPORTED_EXTENSIONS.get(extension, "ملف")
                                all_files.append({
                                    'name': file_name,
                                    'path': file_path,
                                    'department': dept_name,
                                    'year': year_name,
                                    'subject': subject_name,
                                    'size': round(file_size / 1024 / 1024, 2),
                                    'type': file_type,
                                    'similarity': similarity,
                                    'direct_match': direct_match
                                })
        
        # ترتيب النتائج حسب التطابق المباشر أولاً ثم حسب درجة التشابه
        all_files.sort(key=lambda x: (-x['direct_match'], -x['similarity']))
        
        # تخزين نتائج البحث للاستخدام اللاحق
        search_results = all_files
        
        # تخزين مسارات الملفات في user_selections
        if message.chat.id not in user_selections:
            user_selections[message.chat.id] = {}
        
        # تخزين مسارات الملفات فقط (ليس كل المعلومات)
        file_paths = [file_info['path'] for file_info in all_files]
        user_selections[message.chat.id]['displayed_files'] = file_paths
        
        if not all_files:
            safe_send_message(message.chat.id, f"لم يتم العثور على نتائج لـ '{query}'", reply_markup=markup)
            return
        
        # إنشاء لوحة مفاتيح تحتوي على أزرار للملفات
        files_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        
        # إضافة أزرار للملفات
        for file in all_files:
            # إضافة اسم الملف كزر
            files_markup.add(types.KeyboardButton(f"{file['name']}"))
        
        # إضافة زر للعودة
        home_btn = types.KeyboardButton("العودة للقائمة الرئيسية 🏠")
        files_markup.add(home_btn)
        
        # إرسال رسالة مع لوحة المفاتيح الجديدة
        safe_send_message(message.chat.id, f"نتائج البحث عن '{query}'، اختر ملفًا:", reply_markup=files_markup)
        
        # إرسال قائمة مفصلة بالملفات المتاحة وأحجامها وأنواعها كرسالة إضافية
        result_text = f"نتائج البحث عن '{query}':\n\n"
        
        for i, file in enumerate(all_files, 1):
            # إضافة علامة نجمة للنتائج ذات التطابق المباشر وإظهار درجة التشابه للنتائج الأخرى
            match_indicator = "⭐" if file['direct_match'] else f"(تشابه: {round(file['similarity'] * 100)}%)"
            result_text += f"{i}. {file['name']} {match_indicator} - {file['type']} - {file['subject']} - {file['department']} - {file['year']} ({file['size']} MB)\n"
        
        safe_send_message(message.chat.id, result_text)
    except Exception as e:
        logger.error(f"خطأ في البحث: {e}")
        safe_send_message(message.chat.id, "حدث خطأ أثناء البحث عن الملفات.", reply_markup=markup)

# إضافة متغير عام لتخزين نتائج البحث
search_results = []

# قاموس لتخزين آخر قسم وسنة لكل مستخدم
user_selections = {}

@bot.message_handler(func=lambda message: message.text == "مساعدة ❓")
def button_help(message):
    markup = create_main_keyboard()
    send_help(message)

# دالة لإرسال الملفات مع التعامل مع الأخطاء
def safe_send_document(chat_id, file_data, caption=None, reply_markup=None):
    try:
        return bot.send_document(chat_id, file_data, caption=caption, reply_markup=reply_markup)
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"خطأ API تيليجرام: {e}")
        return None
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إرسال الملف: {e}")
        time.sleep(3)  # انتظار قبل إعادة المحاولة
        try:
            return bot.send_document(chat_id, file_data, caption=caption, reply_markup=reply_markup)
        except Exception as retry_e:
            logger.error(f"فشلت إعادة محاولة إرسال الملف: {retry_e}")
            return None

# البحث عن ملف في جميع المجلدات
def find_file(filename):
    filename = filename.lower()
    
    # البحث عن تطابق كامل أولًا مع أي امتداد مدعوم
    for dept_code in DEPARTMENTS.values():
        for year_code in YEARS.values():
            for subject_name, subject_code in SUBJECTS[dept_code][year_code].items():
                folder_path = os.path.join(BASE_FOLDER, dept_code, year_code, subject_code)
                if os.path.exists(folder_path):
                    for extension in SUPPORTED_EXTENSIONS.keys():
                        file_path = os.path.join(folder_path, f"{filename}.{extension}")
                        if os.path.exists(file_path):
                            return file_path
    
    # البحث عن تطابق جزئي
    matching_files = []
    partial_matches = []
    
    for dept_code in DEPARTMENTS.values():
        for year_code in YEARS.values():
            for subject_name, subject_code in SUBJECTS[dept_code][year_code].items():
                folder_path = os.path.join(BASE_FOLDER, dept_code, year_code, subject_code)
                if os.path.exists(folder_path):
                    for file in os.listdir(folder_path):
                        file_name_without_ext = os.path.splitext(file)[0].lower()
                        extension = file.split('.')[-1].lower() if '.' in file else ''
                        
                        # تطابق تام (الكلمة موجودة في اسم الملف)
                        if extension in SUPPORTED_EXTENSIONS and filename in file_name_without_ext:
                            matching_files.append(os.path.join(folder_path, file))
                        # تطابق جزئي (بعض الأحرف متتالية موجودة)
                        elif extension in SUPPORTED_EXTENSIONS:
                            # حساب درجة التشابه باستخدام الدالة المحسنة
                            similarity = calculate_similarity(filename, file_name_without_ext)
                            if similarity >= 0.2:  # نفس الحد الأدنى المستخدم في دالة البحث
                                partial_matches.append({
                                    'path': os.path.join(folder_path, file),
                                    'similarity': similarity
                                })
    
    # إذا وجدنا تطابقات مباشرة، نستخدمها
    if matching_files:
        return matching_files
    
    # إذا لم نجد تطابقات مباشرة، نستخدم التطابقات الجزئية مرتبة حسب درجة التشابه
    if partial_matches:
        # ترتيب النتائج حسب درجة التشابه (من الأعلى للأقل)
        partial_matches.sort(key=lambda x: -x['similarity'])
        # إرجاع المسارات فقط
        return [match['path'] for match in partial_matches]
    
    if len(matching_files) == 1:
        return matching_files[0]
    elif len(matching_files) > 1:
        return matching_files
    
    return None

# التحقق من صحة الملف قبل إرساله
def validate_file(file_path):
    # التحقق من وجود الملف
    if not os.path.exists(file_path):
        return False, "الملف غير موجود"
    
    # التحقق من حجم الملف
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return False, "الملف فارغ"
    
    if file_size > MAX_FILE_SIZE:
        return False, f"حجم الملف كبير جدًا ({round(file_size/1024/1024, 2)} MB). الحد الأقصى هو {MAX_FILE_SIZE/1024/1024} MB"
    
    return True, "الملف صالح"

@bot.message_handler(func=lambda message: message.text == "العودة للمواد 🔙")
def back_to_subjects(message):
    if message.chat.id in user_selections and 'department' in user_selections[message.chat.id] and 'year' in user_selections[message.chat.id]:
        department = user_selections[message.chat.id]['department']
        year_name = user_selections[message.chat.id]['year']
        
        # إنشاء لوحة مفاتيح المواد
        markup = create_subjects_keyboard(department, year_name)
        safe_send_message(
            message.chat.id, 
            f"اختر المادة الدراسية لقسم {department} - {year_name}:", 
            reply_markup=markup
        )
    else:
        # إذا لم تكن هناك معلومات عن آخر قسم/سنة، نعود للقائمة الرئيسية
        markup = create_main_keyboard()
        safe_send_message(message.chat.id, "العودة للقائمة الرئيسية", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_query(message):
    markup = create_main_keyboard()
    subject = message.text.strip()
    
    # التحقق إذا كان المستخدم في مجلد محدد (يعرض ملفات مادة محددة)
    current_folder = None
    if message.chat.id in user_selections and 'current_folder' in user_selections[message.chat.id]:
        current_folder = user_selections[message.chat.id]['current_folder']
    
    # نتحقق إذا كان النص رقمًا، وسنفترض أنه رقم ملف من القائمة
    if subject.isdigit():
        file_idx = int(subject) - 1  # تحويل إلى فهرس (يبدأ من 0)
        
        # تخزين قائمة الملفات المعروضة آخر مرة للمستخدم
        displayed_files = None
        if message.chat.id in user_selections and 'displayed_files' in user_selections[message.chat.id]:
            displayed_files = user_selections[message.chat.id]['displayed_files']
            
            # استخدام القائمة المخزنة مباشرة
            if displayed_files and 0 <= file_idx < len(displayed_files):
                file_path = displayed_files[file_idx]
                # التحقق من صحة الملف قبل إرساله
                is_valid, error_msg = validate_file(file_path)
                if not is_valid:
                    safe_send_message(message.chat.id, f"عذرًا، {error_msg}", reply_markup=markup)
                    return
                
                # إرسال الملف
                send_file_to_user(message.chat.id, file_path)
                return
        
        # إذا لم تكن هناك قائمة مخزنة، نبحث في المجلد الحالي
        elif current_folder and os.path.exists(current_folder):
            try:
                # البحث عن الملف في المجلد الحالي فقط
                files = []
                file_paths = []
                for file in os.listdir(current_folder):
                    extension = file.split('.')[-1].lower() if '.' in file else ''
                    if extension in SUPPORTED_EXTENSIONS:
                        files.append(file)
                        file_paths.append(os.path.join(current_folder, file))
                
                # تخزين القائمة للاستخدام المستقبلي
                if message.chat.id not in user_selections:
                    user_selections[message.chat.id] = {}
                user_selections[message.chat.id]['displayed_files'] = file_paths
                
                if 0 <= file_idx < len(files):
                    file_path = os.path.join(current_folder, files[file_idx])
                    # التحقق من صحة الملف قبل إرساله
                    is_valid, error_msg = validate_file(file_path)
                    if not is_valid:
                        safe_send_message(message.chat.id, f"عذرًا، {error_msg}", reply_markup=markup)
                        return
                    
                    # إرسال الملف
                    send_file_to_user(message.chat.id, file_path)
                    return
            except Exception as e:
                logger.error(f"خطأ في العثور على الملف في المجلد الحالي: {e}")
        
        # إذا لم نجد الملف في المجلد الحالي، نبحث في آخر نتائج البحث
        global search_results
        if search_results and 0 <= file_idx < len(search_results):
            try:
                file_info = search_results[file_idx]
                file_path = file_info['path']
                
                # التحقق من صحة الملف قبل إرساله
                is_valid, error_msg = validate_file(file_path)
                if not is_valid:
                    safe_send_message(message.chat.id, f"عذرًا، {error_msg}", reply_markup=markup)
                    return
                
                # إرسال الملف
                send_file_to_user(message.chat.id, file_path)
                return
            except Exception as e:
                logger.error(f"خطأ في استخدام نتائج البحث: {e}")
        
        # كأخر حل، نبحث في جميع المجلدات
        all_files = []
        try:
            # جمع كل الملفات من جميع الأقسام والسنوات والمواد
            for dept_name, dept_code in DEPARTMENTS.items():
                for year_name, year_code in YEARS.items():
                    for subject_name, subject_code in SUBJECTS[dept_code][year_code].items():
                        folder_path = os.path.join(BASE_FOLDER, dept_code, year_code, subject_code)
                        if os.path.exists(folder_path):
                            for file in os.listdir(folder_path):
                                extension = file.split('.')[-1].lower() if '.' in file else ''
                                if extension in SUPPORTED_EXTENSIONS:
                                    file_path = os.path.join(folder_path, file)
                                    all_files.append(file_path)
            
            # تخزين القائمة للاستخدام المستقبلي
            if message.chat.id not in user_selections:
                user_selections[message.chat.id] = {}
            user_selections[message.chat.id]['displayed_files'] = all_files
            
            if 0 <= file_idx < len(all_files):
                file_path = all_files[file_idx]
                # التحقق من صحة الملف قبل إرساله
                is_valid, error_msg = validate_file(file_path)
                if not is_valid:
                    safe_send_message(message.chat.id, f"عذرًا، {error_msg}", reply_markup=markup)
                    return
                
                # إرسال الملف
                send_file_to_user(message.chat.id, file_path)
                return
            else:
                safe_send_message(message.chat.id, f"عذرًا، الرقم المدخل ({subject}) غير صحيح. يجب أن يكون رقمًا من قائمة الملفات.", reply_markup=markup)
                return
        except Exception as e:
            logger.error(f"خطأ في العثور على الملف برقم {subject}: {e}")
            safe_send_message(message.chat.id, "حدث خطأ أثناء البحث عن الملف. يرجى المحاولة مرة أخرى.", reply_markup=markup)
            return
    
    # البحث عن الملف في المجلد الحالي أولاً إذا كان موجودًا
    if current_folder and os.path.exists(current_folder):
        for file in os.listdir(current_folder):
            file_name = os.path.splitext(file)[0]
            if subject.lower() == file_name.lower():
                file_path = os.path.join(current_folder, file)
                # التحقق من صحة الملف قبل إرساله
                is_valid, error_msg = validate_file(file_path)
                if not is_valid:
                    safe_send_message(message.chat.id, f"عذرًا، {error_msg}", reply_markup=markup)
                    return
                
                # إرسال الملف
                send_file_to_user(message.chat.id, file_path)
                return
    
    # البحث عن الملف في جميع المجلدات
    file_result = find_file(subject)
    
    # إذا وجدنا عدة ملفات متطابقة
    if isinstance(file_result, list):
        result_text = "وجدت عدة ملفات متطابقة:\n\n"
        
        # تخزين القائمة للاستخدام المستقبلي
        if message.chat.id not in user_selections:
            user_selections[message.chat.id] = {}
        user_selections[message.chat.id]['displayed_files'] = file_result
        
        for i, file_path in enumerate(file_result, 1):
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            file_size = os.path.getsize(file_path)
            file_size_mb = round(file_size / 1024 / 1024, 2)
            
            # استخراج القسم والسنة من المسار
            path_parts = file_path.split(os.path.sep)
            if len(path_parts) >= 4:
                dept_code = path_parts[-4]
                year_code = path_parts[-3]
                subject_code = path_parts[-2]
                
                # العثور على اسم القسم والسنة والمادة
                dept_name = next((name for name, code in DEPARTMENTS.items() if code == dept_code), "")
                year_name = next((name for name, code in YEARS.items() if code == year_code), "")
                subject_name = next((name for name, code in SUBJECTS[dept_code][year_code].items() if code == subject_code), "")
                
                result_text += f"{i}. {file_name} - {subject_name} - {dept_name} - {year_name} ({file_size_mb} MB)\n"
            else:
                result_text += f"{i}. {file_name} ({file_size_mb} MB)\n"
        
        result_text += "\nالرجاء اختيار ملف واحد بكتابة اسمه بالكامل أو رقمه من القائمة."
        safe_send_message(message.chat.id, result_text, reply_markup=markup)
        return
    
    # إذا لم نجد الملف
    if not file_result:
        safe_send_message(message.chat.id, f"عذرًا، لم أجد ملفاً باسم '{subject}'", reply_markup=markup)
        safe_send_message(message.chat.id, "يمكنك استخدام أمر /search للبحث أو تصفح الأقسام والسنوات الدراسية.")
        return

# معالج للأزرار الضغطية (Callback Queries)
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        # تقسيم بيانات الاستدعاء
        data_parts = call.data.split(':')
        action = data_parts[0]
        
        if action == "dept" and len(data_parts) >= 2:
            # اختيار قسم
            dept_code = data_parts[1]
            dept_name = next((name for name, code in DEPARTMENTS.items() if code == dept_code), "")
            
            if dept_name:
                # عرض السنوات الدراسية لهذا القسم
                markup = types.InlineKeyboardMarkup(row_width=1)
                for year_name, year_code in YEARS.items():
                    markup.add(types.InlineKeyboardButton(
                        year_name, 
                        callback_data=f"year:{dept_code}:{year_code}"
                    ))
                markup.add(types.InlineKeyboardButton("العودة للأقسام 🔙", callback_data="backtodepts"))
                
                bot.edit_message_text(
                    f"اختر السنة الدراسية لقسم {dept_name}:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )
        
        elif action == "year" and len(data_parts) >= 3:
            # اختيار سنة دراسية
            dept_code = data_parts[1]
            year_code = data_parts[2]
            
            dept_name = next((name for name, code in DEPARTMENTS.items() if code == dept_code), "")
            year_name = next((name for name, code in YEARS.items() if code == year_code), "")
            
            if dept_name and year_name:
                # إنشاء أزرار للمواد الدراسية
                markup = types.InlineKeyboardMarkup(row_width=1)
                for subject_name, subject_code in SUBJECTS[dept_code][year_code].items():
                    markup.add(types.InlineKeyboardButton(
                        subject_name,
                        callback_data=f"subject:{dept_code}:{year_code}:{subject_code}"
                    ))
                
                # إضافة زر للعودة
                markup.add(types.InlineKeyboardButton("العودة للسنوات الدراسية 🔙", callback_data=f"dept:{dept_code}"))
                
                bot.edit_message_text(
                    f"اختر المادة الدراسية لقسم {dept_name} - {year_name}:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )
        
        elif action == "subject" and len(data_parts) >= 4:
            # اختيار مادة دراسية
            dept_code = data_parts[1]
            year_code = data_parts[2]
            subject_code = data_parts[3]
            
            dept_name = next((name for name, code in DEPARTMENTS.items() if code == dept_code), "")
            year_name = next((name for name, code in YEARS.items() if code == year_code), "")
            subject_name = next((name for name, code in SUBJECTS[dept_code][year_code].items() if code == subject_code), "")
            
            if dept_name and year_name and subject_name:
                folder_path = os.path.join(BASE_FOLDER, dept_code, year_code, subject_code)
                
                # التأكد من وجود المجلد
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                # عرض الملفات في هذه المادة
                files = []
                for file in os.listdir(folder_path):
                    extension = file.split('.')[-1].lower() if '.' in file else ''
                    if extension in SUPPORTED_EXTENSIONS:
                        files.append(file)
                
                if not files:
                    bot.answer_callback_query(call.id, f"لا توجد ملفات في {subject_name} - {dept_name} - {year_name}")
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("العودة للمواد الدراسية 🔙", callback_data=f"year:{dept_code}:{year_code}"))
                    bot.edit_message_text(
                        f"لا توجد ملفات متوفرة في {subject_name} - {dept_name} - {year_name} حالياً.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=markup
                    )
                    return
                
                # إنشاء أزرار للملفات
                markup = types.InlineKeyboardMarkup(row_width=1)
                
                for i, file in enumerate(files):
                    file_name = os.path.splitext(file)[0]
                    extension = file.split('.')[-1].lower()
                    file_type = SUPPORTED_EXTENSIONS.get(extension, "ملف")
                    file_size = os.path.getsize(os.path.join(folder_path, file))
                    file_size_mb = round(file_size / 1024 / 1024, 2)
                    
                    # إضافة زر لكل ملف
                    callback_data = f"fileidx:{folder_path}:{i}"
                    
                    markup.add(types.InlineKeyboardButton(
                        f"{file_name} ({file_size_mb} MB)", 
                        callback_data=callback_data
                    ))
                
                # إضافة زر للعودة
                markup.add(types.InlineKeyboardButton("العودة للمواد الدراسية 🔙", callback_data=f"year:{dept_code}:{year_code}"))
                
                bot.edit_message_text(
                    f"ملفات {subject_name} - {dept_name} - {year_name}:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )
        
        elif action == "fileidx" and len(data_parts) >= 3:
            # استدعاء ملف عن طريق مؤشر في قائمة الملفات
            folder_path = data_parts[1]
            try:
                file_idx = int(data_parts[2])
                # الحصول على جميع الملفات المدعومة وليس فقط PDF
                files = []
                for file in os.listdir(folder_path):
                    extension = file.split('.')[-1].lower() if '.' in file else ''
                    if extension in SUPPORTED_EXTENSIONS:
                        files.append(file)
                
                if 0 <= file_idx < len(files):
                    file_path = os.path.join(folder_path, files[file_idx])
                    
                    # إرسال إشعار للمستخدم
                    bot.answer_callback_query(call.id, "جاري تحضير الملف...")
                    
                    # إرسال الملف
                    send_file_to_user(call.message.chat.id, file_path)
                else:
                    bot.answer_callback_query(call.id, "عذراً، الملف غير موجود")
            except (ValueError, IndexError) as e:
                bot.answer_callback_query(call.id, "حدث خطأ في اختيار الملف")
        
        elif action == "file" and len(data_parts) >= 3:
            # استدعاء ملف مباشرة
            folder_path = data_parts[1]
            file_name = data_parts[2]
            file_path = os.path.join(folder_path, file_name)
            
            # التحقق من وجود الملف وإرساله
            if os.path.exists(file_path):
                # إرسال إشعار للمستخدم
                bot.answer_callback_query(call.id, "جاري تحضير الملف...")
                
                # إرسال الملف
                send_file_to_user(call.message.chat.id, file_path)
            else:
                bot.answer_callback_query(call.id, "عذراً، الملف غير موجود")
        
        elif action == "backtodepts":
            # العودة إلى قائمة الأقسام
            markup = types.InlineKeyboardMarkup(row_width=1)
            for dept_name, dept_code in DEPARTMENTS.items():
                markup.add(types.InlineKeyboardButton(dept_name, callback_data=f"dept:{dept_code}"))
            
            bot.edit_message_text(
                "اختر القسم:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
        
        elif action == "back" and len(data_parts) >= 2:
            # استخراج المسار وتحديد العملية المناسبة
            path_parts = data_parts[1].split('/')
            
            if len(path_parts) >= 3:
                dept_code = path_parts[-3] if len(path_parts) >= 3 else ""
                
                # العودة إلى صفحة السنوات الدراسية للقسم
                if dept_code:
                    dept_name = next((name for name, code in DEPARTMENTS.items() if code == dept_code), "")
                    if dept_name:
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        for year_name, year_code in YEARS.items():
                            markup.add(types.InlineKeyboardButton(
                                year_name, 
                                callback_data=f"year:{dept_code}:{year_code}"
                            ))
                        markup.add(types.InlineKeyboardButton("العودة للأقسام 🔙", callback_data="backtodepts"))
                        
                        bot.edit_message_text(
                            f"اختر السنة الدراسية لقسم {dept_name}:",
                            call.message.chat.id,
                            call.message.message_id,
                            reply_markup=markup
                        )
                    else:
                        # العودة إلى صفحة الأقسام
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        for dept_name, dept_code in DEPARTMENTS.items():
                            markup.add(types.InlineKeyboardButton(dept_name, callback_data=f"dept:{dept_code}"))
                        
                        bot.edit_message_text(
                            "اختر القسم:",
                            call.message.chat.id,
                            call.message.message_id,
                            reply_markup=markup
                        )
            else:
                # العودة إلى القائمة الرئيسية
                markup = create_main_keyboard()
                bot.send_message(call.message.chat.id, "القائمة الرئيسية:", reply_markup=markup)
        
        elif action == "search_file" and len(data_parts) >= 2:
            try:
                file_idx = int(data_parts[1])
                if 0 <= file_idx < len(search_results):
                    file_info = search_results[file_idx]
                    file_path = file_info['path']
                    
                    # إرسال إشعار للمستخدم
                    bot.answer_callback_query(call.id, "جاري تحضير الملف...")
                    
                    # إرسال الملف
                    send_file_to_user(call.message.chat.id, file_path)
                else:
                    bot.answer_callback_query(call.id, "عذراً، الملف غير موجود")
            except (ValueError, IndexError) as e:
                bot.answer_callback_query(call.id, "حدث خطأ في اختيار الملف")
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الاستدعاء: {e}")
        bot.answer_callback_query(call.id, "حدث خطأ في معالجة الطلب")

# دالة لإرسال ملف إلى المستخدم
def send_file_to_user(chat_id, file_path):
    markup = create_main_keyboard()
    
    try:
        # التحقق من وجود الملف
        if not os.path.exists(file_path):
            safe_send_message(chat_id, "عذرًا، الملف غير موجود.", reply_markup=markup)
            return
        
        # الحصول على حجم الملف
        file_size = os.path.getsize(file_path)
        file_size_mb = round(file_size / 1024 / 1024, 2)
        
        # الحصول على اسم الملف ونوعه
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
        file_type = SUPPORTED_EXTENSIONS.get(extension, "ملف")
        
        # استخراج معلومات القسم والسنة ونوع الملف من المسار
        path_parts = file_path.split(os.path.sep)
        file_info = ""
        
        if len(path_parts) >= 4:
            dept_code = path_parts[-4]
            year_code = path_parts[-3]
            subject_code = path_parts[-2]
            
            # العثور على اسم القسم والسنة والمادة من الكود
            dept_name = next((name for name, code in DEPARTMENTS.items() if code == dept_code), "")
            year_name = next((name for name, code in YEARS.items() if code == year_code), "")
            
            # البحث عن اسم المادة من الكود
            subject_name = ""
            if dept_code in SUBJECTS and year_code in SUBJECTS[dept_code]:
                subject_name = next((name for name, code in SUBJECTS[dept_code][year_code].items() if code == subject_code), "")
            
            if dept_name and year_name and subject_name:
                file_info = f" ({subject_name} - {dept_name} - {year_name})"
        
        # التحقق مما إذا كان الملف فارغًا
        if file_size == 0:
            safe_send_message(chat_id, "عذرًا، الملف فارغ.", reply_markup=markup)
            return
        
        # إرسال رسالة "جاري التحميل"
        loading_msg = safe_send_message(chat_id, "جاري تحميل الملف... ⏳")
        
        # التحقق مما إذا كان الملف كبيرًا جدًا (أكبر من 50 ميجابايت)
        if file_size > MAX_FILE_SIZE:
            # إرسال رسالة للمستخدم حول حجم الملف
            info_message = (
                f"⚠️ الملف {file_name_without_ext} كبير ({file_size_mb} MB) ويتجاوز حد تيليجرام (50 MB).\n\n"
                f"سيتم تقسيم الملف إلى أجزاء وإرسالها لك بشكل منفصل."
            )
            safe_send_message(chat_id, info_message)
            
            if loading_msg:
                try:
                    bot.delete_message(chat_id, loading_msg.message_id)
                except Exception:
                    pass
            
            # تقسيم الملف وإرسال الأجزاء
            chunk_size = 49 * 1024 * 1024  # 49MB لكل جزء (للتأكد من البقاء أقل من الحد)
            total_chunks = (file_size + chunk_size - 1) // chunk_size  # عدد الأجزاء المطلوبة
            
            with open(file_path, "rb") as f:
                for i in range(total_chunks):
                    # إرسال رسالة حالة التقدم
                    progress_msg = safe_send_message(chat_id, f"جاري تحميل الجزء {i+1} من {total_chunks}... ⏳")
                    
                    # قراءة قطعة (جزء) من الملف
                    chunk = f.read(chunk_size)
                    
                    # إرسال الجزء كملف منفصل
                    chunk_data = io.BytesIO(chunk)
                    chunk_data.name = f"{file_name_without_ext}_part{i+1}of{total_chunks}.{extension}"
                    
                    # إرسال الجزء
                    success = safe_send_document(chat_id, chunk_data)
                    
                    # حذف رسالة التقدم
                    if progress_msg:
                        try:
                            bot.delete_message(chat_id, progress_msg.message_id)
                        except Exception:
                            pass
                    
                    if not success:
                        safe_send_message(chat_id, f"فشل إرسال الجزء {i+1} من {total_chunks}. يرجى المحاولة مرة أخرى.", reply_markup=markup)
                        return
            
            # إرسال رسالة نجاح بعد الانتهاء من إرسال جميع الأجزاء
            safe_send_message(
                chat_id, 
                f"تم إرسال {file_type} {file_name_without_ext}{file_info} بنجاح ✅\n"
                f"حجم الملف: {file_size_mb} MB (تم تقسيمه إلى {total_chunks} أجزاء)", 
                reply_markup=markup
            )
            return
        
        # قراءة الملف مرة واحدة إلى الذاكرة (للملفات الأصغر من 50MB)
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        if not file_content:
            if loading_msg:
                try:
                    bot.delete_message(chat_id, loading_msg.message_id)
                except Exception:
                    pass
            safe_send_message(chat_id, "عذرًا، الملف فارغ أو تعذرت قراءته.", reply_markup=markup)
            return
        
        # إنشاء كائن BytesIO لإرسال البيانات من الذاكرة
        file_data = io.BytesIO(file_content)
        file_data.name = file_name
        
        # إرسال الملف
        success = False
        
        try:
            # إرسال الملفات حسب نوعها
            if extension in ['jpg', 'jpeg', 'png', 'gif'] and file_size_mb <= 10:
                # إرسال كصورة (الحد الأقصى 10MB)
                try:
                    bot.send_photo(chat_id, file_data)
                    success = True
                except Exception as e:
                    logger.error(f"خطأ في إرسال الصورة: {e}")
                    # إعادة تهيئة file_data لإرساله كمستند
                    file_data.seek(0)
                    success = safe_send_document(chat_id, file_data)
            elif extension in ['mp3'] and file_size_mb <= 20:
                # إرسال كملف صوتي (الحد الأقصى 20MB)
                try:
                    bot.send_audio(chat_id, file_data)
                    success = True
                except Exception as e:
                    logger.error(f"خطأ في إرسال الملف الصوتي: {e}")
                    # إعادة تهيئة file_data لإرساله كمستند
                    file_data.seek(0)
                    success = safe_send_document(chat_id, file_data)
            elif extension in ['mp4'] and file_size_mb <= 20:
                # إرسال كفيديو (الحد الأقصى 20MB)
                try:
                    bot.send_video(chat_id, file_data)
                    success = True
                except Exception as e:
                    logger.error(f"خطأ في إرسال الفيديو: {e}")
                    # إعادة تهيئة file_data لإرساله كمستند
                    file_data.seek(0)
                    success = safe_send_document(chat_id, file_data)
            else:
                # إرسال كملف عادي (الحد الأقصى 50MB)
                success = safe_send_document(chat_id, file_data)
        except Exception as e:
            logger.error(f"خطأ في إرسال الملف: {e}")
            # محاولة إرسال كملف عادي كخطة بديلة
            try:
                # إعادة تهيئة file_data لإرساله مرة أخرى
                file_data.seek(0)
                success = safe_send_document(chat_id, file_data)
            except Exception as doc_e:
                logger.error(f"خطأ في إرسال الملف كمستند: {doc_e}")
        
        # حذف رسالة "جاري التحميل"
        if loading_msg:
            try:
                bot.delete_message(chat_id, loading_msg.message_id)
            except Exception:
                pass
        
        if success:
            safe_send_message(
                chat_id, 
                f"تم إرسال {file_type} {file_name_without_ext}{file_info} بنجاح ✅\nحجم الملف: {file_size_mb} MB", 
                reply_markup=markup
            )
        else:
            error_msg = f"حدث خطأ أثناء إرسال الملف {file_name_without_ext}. حجم الملف: {file_size_mb} MB."
            safe_send_message(chat_id, error_msg, reply_markup=markup)
            
    except Exception as e:
        logger.error(f"خطأ أثناء قراءة أو إرسال الملف: {e}")
        if 'loading_msg' in locals() and loading_msg:
            try:
                bot.delete_message(chat_id, loading_msg.message_id)
            except Exception:
                pass
        safe_send_message(chat_id, f"حدث خطأ أثناء تحميل الملف: {str(e)}", reply_markup=markup)

logger.info("تم تشغيل البوت!")
print("تم تشغيل البوت!")

# استخدام معامل محاولة إعادة اتصال أفضل
while True:
    try:
        bot.infinity_polling(timeout=120, long_polling_timeout=120)
    except Exception as e:
        logger.error(f"حدث خطأ في البوت: {e}")
        print(f"حدث خطأ في البوت: {e}")
        time.sleep(10)
        logger.info("جاري إعادة تشغيل البوت...")
        print("جاري إعادة تشغيل البوت...")