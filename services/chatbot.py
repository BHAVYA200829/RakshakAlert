# RakshakAlert - rule-based help assistant. No LLM, no external API.
# Answers come only from the safety guides and site help in this file.
# Multilingual (Extras): the greeting, quick questions, placeholder,
# fallback and the short summary line of each answer are translated
# into all 9 site languages. Full safety detail stays in English and
# is appended after the translated summary. If the question is not
# understood, the bot says so in the current language and points to
# the safety guide and helpline 112. No em dashes anywhere.

from services.safety import SAFETY

LANGS9 = ["en", "hi", "mr", "bn", "ta", "te", "gu", "kn", "ml"]

T = {
    "greeting": {
        "en": "Hi. Ask me about safety in a flood, earthquake or cyclone, or how to report and track a report. In an emergency, call 112.",
        "hi": "नमस्ते। बाढ़, भूकंप या चक्रवात में सुरक्षा, या रिपोर्ट करने और ट्रैक करने के बारे में पूछें। आपातकाल में 112 पर कॉल करें।",
        "mr": "नमस्कार. पूर, भूकंप किंवा चक्रीवादळातील सुरक्षा, किंवा तक्रार नोंदवणे आणि तपासणे याबद्दल विचारा. आणीबाणीत 112 वर कॉल करा.",
        "bn": "নমস্কার। বন্যা, ভূমিকম্প বা ঘূর্ণিঝড়ে নিরাপত্তা, বা রিপোর্ট করা ও দেখা সম্পর্কে জিজ্ঞাসা করুন। জরুরি অবস্থায় 112 নম্বরে কল করুন।",
        "ta": "வணக்கம். வெள்ளம், நிலநடுக்கம் அல்லது புயலில் பாதுகாப்பு, அல்லது புகாரளிப்பது மற்றும் கண்காணிப்பது பற்றி கேளுங்கள். அவசரத்தில் 112 ஐ அழைக்கவும்.",
        "te": "నమస్కారం. వరద, భూకంపం లేదా తుఫానులో భద్రత, లేదా రిపోర్ట్ చేయడం మరియు ట్రాక్ చేయడం గురించి అడగండి. అత్యవసరంలో 112కు కాల్ చేయండి.",
        "gu": "નમસ્તે. પૂર, ભૂકંપ કે ચક્રવાતમાં સલામતી, અથવા રિપોર્ટ કરવા અને તપાસવા વિશે પૂછો. કટોકટીમાં 112 પર કૉલ કરો.",
        "kn": "ನಮಸ್ಕಾರ. ಪ್ರವಾಹ, ಭೂಕಂಪ ಅಥವಾ ಚಂಡಮಾರುತದಲ್ಲಿ ಸುರಕ್ಷತೆ, ಅಥವಾ ವರದಿ ಮಾಡುವುದು ಮತ್ತು ಟ್ರ್ಯಾಕ್ ಮಾಡುವುದು ಬಗ್ಗೆ ಕೇಳಿ. ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "ml": "നമസ്കാരം. വെള്ളപ്പൊക്കം, ഭൂകമ്പം അല്ലെങ്കിൽ ചുഴലിക്കാറ്റിലെ സുരക്ഷ, അല്ലെങ്കിൽ റിപ്പോർട്ട് ചെയ്യുന്നതും പരിശോധിക്കുന്നതും സംബന്ധിച്ച് ചോദിക്കൂ. അടിയന്തരാവസ്ഥയിൽ 112 വിളിക്കൂ.",
    },
    "placeholder": {
        "en": "Type your question", "hi": "अपना सवाल लिखें", "mr": "तुमचा प्रश्न लिहा",
        "bn": "আপনার প্রশ্ন লিখুন", "ta": "உங்கள் கேள்வியை எழுதுங்கள்",
        "te": "మీ ప్రశ్నను టైప్ చేయండి", "gu": "તમારો પ્રશ્ન લખો",
        "kn": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ", "ml": "നിങ്ങളുടെ ചോദ്യം ടൈപ്പ് ചെയ്യുക",
    },
    "fallback": {
        "en": "I do not understand that question. I can help with safety in a flood, earthquake or cyclone, how to report and track a report, SOS, and helpline numbers. Try the Safety Guide or call 112 in an emergency.",
        "hi": "मैं यह सवाल समझ नहीं पाया। मैं बाढ़, भूकंप या चक्रवात में सुरक्षा, रिपोर्ट करने और ट्रैक करने, SOS और हेल्पलाइन नंबरों में मदद कर सकता हूँ। Safety Guide देखें या आपातकाल में 112 पर कॉल करें।",
        "mr": "मला हा प्रश्न समजला नाही. मी पूर, भूकंप किंवा चक्रीवादळातील सुरक्षा, तक्रार नोंदवणे आणि तपासणे, SOS आणि हेल्पलाइन क्रमांक यामध्ये मदत करू शकतो. Safety Guide पहा किंवा आणीबाणीत 112 वर कॉल करा.",
        "bn": "আমি এই প্রশ্নটি বুঝতে পারিনি। আমি বন্যা, ভূমিকম্প বা ঘূর্ণিঝড়ে নিরাপত্তা, রিপোর্ট করা ও দেখা, SOS এবং হেল্পলাইন নম্বর সম্পর্কে সাহায্য করতে পারি। Safety Guide দেখুন অথবা জরুরি অবস্থায় 112 নম্বরে কল করুন।",
        "ta": "இந்தக் கேள்வி எனக்குப் புரியவில்லை. வெள்ளம், நிலநடுக்கம் அல்லது புயலில் பாதுகாப்பு, புகாரளிப்பது மற்றும் கண்காணிப்பது, SOS மற்றும் உதவி எண்கள் பற்றி நான் உதவ முடியும். Safety Guide ஐப் பார்க்கவும் அல்லது அவசரத்தில் 112 ஐ அழைக்கவும்.",
        "te": "నాకు ఈ ప్రశ్న అర్థం కాలేదు. వరద, భూకంపం లేదా తుఫానులో భద్రత, రిపోర్ట్ చేయడం మరియు ట్రాక్ చేయడం, SOS మరియు హెల్ప్‌లైన్ నంబర్ల గురించి నేను సహాయం చేయగలను. Safety Guide చూడండి లేదా అత్యవసరంలో 112కు కాల్ చేయండి.",
        "gu": "મને આ પ્રશ્ન સમજાયો નથી. હું પૂર, ભૂકંપ કે ચક્રવાતમાં સલામતી, રિપોર્ટ કરવા અને તપાસવા, SOS અને હેલ્પલાઇન નંબરો વિશે મદદ કરી શકું છું. Safety Guide જુઓ અથવા કટોકટીમાં 112 પર કૉલ કરો.",
        "kn": "ಈ ಪ್ರಶ್ನೆ ನನಗೆ ಅರ್ಥವಾಗಲಿಲ್ಲ. ಪ್ರವಾಹ, ಭೂಕಂಪ ಅಥವಾ ಚಂಡಮಾರುತದಲ್ಲಿ ಸುರಕ್ಷತೆ, ವರದಿ ಮಾಡುವುದು ಮತ್ತು ಟ್ರ್ಯಾಕ್ ಮಾಡುವುದು, SOS ಮತ್ತು ಸಹಾಯವಾಣಿ ಸಂಖ್ಯೆಗಳ ಬಗ್ಗೆ ನಾನು ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. Safety Guide ನೋಡಿ ಅಥವಾ ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "ml": "എനിക്ക് ഈ ചോദ്യം മനസ്സിലായില്ല. വെള്ളപ്പൊക്കം, ഭൂകമ്പം അല്ലെങ്കിൽ ചുഴലിക്കാറ്റിലെ സുരക്ഷ, റിപ്പോർട്ട് ചെയ്യുന്നതും പരിശോധിക്കുന്നതും, SOS, ഹെൽപ്പ്‌ലൈൻ നമ്പറുകൾ എന്നിവയിൽ എനിക്ക് സഹായിക്കാനാകും. Safety Guide കാണുക അല്ലെങ്കിൽ അടിയന്തരാവസ്ഥയിൽ 112 വിളിക്കൂ.",
    },
    "listening": {
        "en": "Listening... tap Stop when done.", "hi": "सुन रहा हूँ... पूरा होने पर रुकें दबाएँ।",
        "mr": "ऐकत आहे... पूर्ण झाल्यावर थांबा दाबा.", "bn": "শুনছি... শেষ হলে থামুন চাপুন।",
        "ta": "கேட்கிறேன்... முடிந்ததும் நிறுத்து என்பதை அழுத்தவும்.",
        "te": "వింటున్నాను... పూర్తయిన తర్వాత ఆపు నొక్కండి.",
        "gu": "સાંભળી રહ્યો છું... પૂરું થાય ત્યારે બંધ કરો દબાવો.",
        "kn": "ಕೇಳುತ್ತಿದ್ದೇನೆ... ಮುಗಿದ ನಂತರ ನಿಲ್ಲಿಸಿ ಒತ್ತಿರಿ.",
        "ml": "കേൾക്കുന്നു... കഴിഞ്ഞാൽ നിർത്തുക അമർത്തുക.",
    },
    "voice_not_supported": {
        "en": "Voice input is not supported in this browser. Please type instead.",
        "hi": "इस ब्राउज़र में वॉइस इनपुट समर्थित नहीं है। कृपया टाइप करें।",
        "mr": "या ब्राउझरमध्ये आवाज इनपुट समर्थित नाही. कृपया टाइप करा.",
        "bn": "এই ব্রাউজারে ভয়েস ইনপুট সমর্থিত নয়। অনুগ্রহ করে টাইপ করুন।",
        "ta": "இந்த உலாவியில் குரல் உள்ளீடு ஆதரிக்கப்படவில்லை. தயவுசெய்து தட்டச்சு செய்யவும்.",
        "te": "ఈ బ్రౌజర్‌లో వాయిస్ ఇన్‌పుట్ మద్దతు లేదు. దయచేసి టైప్ చేయండి.",
        "gu": "આ બ્રાઉઝરમાં વોઇસ ઇનપુટ સપોર્ટેડ નથી. કૃપા કરીને ટાઇપ કરો.",
        "kn": "ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ಟೈಪ್ ಮಾಡಿ.",
        "ml": "ഈ ബ്രൗസറിൽ വോയ്‌സ് ഇൻപുട്ട് പിന്തുണയ്ക്കുന്നില്ല. ദയവായി ടൈപ്പ് ചെയ്യുക.",
    },
    "voice_denied": {
        "en": "Microphone permission was denied. Allow the microphone in your browser, or type instead.",
        "hi": "माइक्रोफ़ोन की अनुमति नहीं मिली। ब्राउज़र में माइक्रोफ़ोन की अनुमति दें, या टाइप करें।",
        "mr": "मायक्रोफोनची परवानगी नाकारली. ब्राउझरमध्ये मायक्रोफोनला परवानगी द्या, किंवा टाइप करा.",
        "bn": "মাইক্রোফোনের অনুমতি দেওয়া হয়নি। ব্রাউজারে মাইক্রোফোনের অনুমতি দিন, অথবা টাইপ করুন।",
        "ta": "ஒலிவாங்கி அனுமதி மறுக்கப்பட்டது. உலாவியில் ஒலிவாங்கியை அனுமதிக்கவும், அல்லது தட்டச்சு செய்யவும்.",
        "te": "మైక్రోఫోన్ అనుమతి నిరాకరించబడింది. బ్రౌజర్‌లో మైక్రోఫోన్‌ను అనుమతించండి, లేదా టైప్ చేయండి.",
        "gu": "માઇક્રોફોનની પરવાનગી નકારવામાં આવી. બ્રાઉઝરમાં માઇક્રોફોનને મંજૂરી આપો, અથવા ટાઇપ કરો.",
        "kn": "ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿಯನ್ನು ನಿರಾಕರಿಸಲಾಗಿದೆ. ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿಸಿ, ಅಥವಾ ಟೈಪ್ ಮಾಡಿ.",
        "ml": "മൈക്രോഫോൺ അനുമതി നിഷേധിച്ചു. ബ്രൗസറിൽ മൈക്രോഫോൺ അനുവദിക്കുക, അല്ലെങ്കിൽ ടൈപ്പ് ചെയ്യുക.",
    },
    "helpline": {
        "en": "Emergency helpline: 112. NDMA Helpline: 1078. Call 112 for police, fire or ambulance help in an emergency.",
        "hi": "आपातकालीन हेल्पलाइन: 112। NDMA हेल्पलाइन: 1078। आपातकाल में पुलिस, आग या एम्बुलेंस के लिए 112 पर कॉल करें।",
        "mr": "आणीबाणी हेल्पलाइन: 112. NDMA हेल्पलाइन: 1078. आणीबाणीत पोलिस, आग किंवा रुग्णवाहिकेसाठी 112 वर कॉल करा.",
        "bn": "জরুরি হেল্পলাইন: 112। NDMA হেল্পলাইন: 1078। জরুরি অবস্থায় পুলিশ, দমকল বা অ্যাম্বুলেন্সের জন্য 112 নম্বরে কল করুন।",
        "ta": "அவசர உதவி எண்: 112. NDMA உதவி எண்: 1078. அவசரத்தில் காவல், தீயணைப்பு அல்லது ஆம்புலன்ஸ் உதவிக்கு 112 ஐ அழைக்கவும்.",
        "te": "అత్యవసర హెల్ప్‌లైన్: 112. NDMA హెల్ప్‌లైన్: 1078. అత్యవసరంలో పోలీసు, అగ్నిమాపక లేదా అంబులెన్స్ సహాయం కోసం 112కు కాల్ చేయండి.",
        "gu": "કટોકટી હેલ્પલાઇન: 112. NDMA હેલ્પલાઇન: 1078. કટોકટીમાં પોલીસ, આગ કે એમ્બ્યુલન્સ માટે 112 પર કૉલ કરો.",
        "kn": "ತುರ್ತು ಸಹಾಯವಾಣಿ: 112. NDMA ಸಹಾಯವಾಣಿ: 1078. ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ಪೊಲೀಸ್, ಅಗ್ನಿಶಾಮಕ ಅಥವಾ ಆಂಬ್ಯುಲೆನ್ಸ್ ಸಹಾಯಕ್ಕಾಗಿ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "ml": "അടിയന്തര ഹെൽപ്പ്‌ലൈൻ: 112. NDMA ഹെൽപ്പ്‌ലൈൻ: 1078. അടിയന്തരാവസ്ഥയിൽ പോലീസ്, അഗ്നിശമന അല്ലെങ്കിൽ ആംബുലൻസ് സഹായത്തിന് 112 വിളിക്കൂ.",
    },
    "sos": {
        "en": "Tap the red SOS button on the home page. It sends your location and nearest tower to the admin at once. If you are in danger right now, call 112 first.",
        "hi": "होम पेज पर लाल SOS बटन दबाएँ। यह आपकी जगह और निकटतम टावर तुरंत एडमिन को भेजता है। अगर आप अभी खतरे में हैं, तो पहले 112 पर कॉल करें।",
        "mr": "होम पेजवरील लाल SOS बटण दाबा. ते तुमचे स्थान आणि जवळचा टॉवर लगेच अ‍ॅडमिनला पाठवते. तुम्ही आत्ता धोक्यात असाल, तर आधी 112 वर कॉल करा.",
        "bn": "হোম পেজে লাল SOS বোতাম চাপুন। এটি আপনার অবস্থান ও নিকটতম টাওয়ার সঙ্গে সঙ্গে অ্যাডমিনকে পাঠায়। আপনি এখনই বিপদে থাকলে আগে 112 নম্বরে কল করুন।",
        "ta": "முகப்புப் பக்கத்தில் சிவப்பு SOS பொத்தானை அழுத்தவும். இது உங்கள் இடம் மற்றும் அருகிலுள்ள கோபுரத்தை உடனடியாக நிர்வாகிக்கு அனுப்பும். நீங்கள் இப்போது ஆபத்தில் இருந்தால், முதலில் 112 ஐ அழைக்கவும்.",
        "te": "హోమ్ పేజీలో ఎరుపు SOS బటన్ నొక్కండి. ఇది మీ స్థానం మరియు సమీప టవర్‌ను వెంటనే అడ్మిన్‌కు పంపుతుంది. మీరు ఇప్పుడు ప్రమాదంలో ఉంటే, ముందుగా 112కు కాల్ చేయండి.",
        "gu": "હોમ પેજ પર લાલ SOS બટન દબાવો. તે તમારું સ્થાન અને નજીકનો ટાવર તરત જ એડમિનને મોકલે છે. જો તમે અત્યારે જોખમમાં હો, તો પહેલા 112 પર કૉલ કરો.",
        "kn": "ಮುಖಪುಟದಲ್ಲಿರುವ ಕೆಂಪು SOS ಬಟನ್ ಒತ್ತಿರಿ. ಇದು ನಿಮ್ಮ ಸ್ಥಳ ಮತ್ತು ಹತ್ತಿರದ ಗೋಪುರವನ್ನು ತಕ್ಷಣ ನಿರ್ವಾಹಕರಿಗೆ ಕಳುಹಿಸುತ್ತದೆ. ನೀವು ಈಗ ಅಪಾಯದಲ್ಲಿದ್ದರೆ, ಮೊದಲು 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "ml": "ഹോം പേജിലെ ചുവന്ന SOS ബട്ടൺ അമർത്തുക. ഇത് നിങ്ങളുടെ സ്ഥലവും അടുത്തുള്ള ടവറും ഉടൻ അഡ്മിനിലേക്ക് അയയ്ക്കുന്നു. നിങ്ങൾ ഇപ്പോൾ അപകടത്തിലാണെങ്കിൽ, ആദ്യം 112 വിളിക്കൂ.",
    },
    "report": {
        "en": "Go to Report Incident (top menu, no login needed). Pick the disaster type and your city, describe what you see, add a photo if you can, and send. You get a tracking ID like RA-00001.",
        "hi": "Report Incident पर जाएँ (ऊपर का मेनू, लॉगिन नहीं चाहिए)। आपदा का प्रकार और अपना शहर चुनें, जो दिख रहा है वह लिखें, हो सके तो फोटो जोड़ें, और भेजें। आपको RA-00001 जैसी ट्रैकिंग ID मिलेगी।",
        "mr": "Report Incident वर जा (वरील मेनू, लॉगिनची गरज नाही). आपत्तीचा प्रकार आणि तुमचे शहर निवडा, काय दिसते ते लिहा, शक्य असल्यास फोटो जोडा आणि पाठवा. तुम्हाला RA-00001 सारखी ट्रॅकिंग ID मिळेल.",
        "bn": "Report Incident-এ যান (উপরের মেনু, লগইন লাগে না)। দুর্যোগের ধরন ও আপনার শহর বেছে নিন, যা দেখছেন তা লিখুন, পারলে ছবি যোগ করুন, তারপর পাঠান। RA-00001-এর মতো একটি ট্র্যাকিং ID পাবেন।",
        "ta": "Report Incident பக்கத்திற்குச் செல்லவும் (மேல் மெனு, உள்நுழைவு தேவையில்லை). பேரழிவு வகை மற்றும் உங்கள் நகரத்தைத் தேர்ந்து, நீங்கள் காண்பதை எழுதி, முடிந்தால் புகைப்படம் சேர்த்து அனுப்பவும். RA-00001 போன்ற கண்காணிப்பு எண் கிடைக்கும்.",
        "te": "Report Incident కు వెళ్లండి (పై మెనూ, లాగిన్ అవసరం లేదు). విపత్తు రకం మరియు మీ నగరాన్ని ఎంచుకుని, మీరు చూసేది రాసి, వీలైతే ఫోటో జోడించి పంపండి. RA-00001 వంటి ట్రాకింగ్ ID లభిస్తుంది.",
        "gu": "Report Incident પર જાઓ (ઉપરનું મેનૂ, લોગિન જરૂરી નથી). આપત્તિનો પ્રકાર અને તમારું શહેર પસંદ કરો, જે દેખાય છે તે લખો, શક્ય હોય તો ફોટો ઉમેરો અને મોકલો. તમને RA-00001 જેવી ટ્રેકિંગ ID મળશે.",
        "kn": "Report Incident ಗೆ ಹೋಗಿ (ಮೇಲಿನ ಮೆನು, ಲಾಗಿನ್ ಅಗತ್ಯವಿಲ್ಲ). ವಿಪತ್ತಿನ ಪ್ರಕಾರ ಮತ್ತು ನಿಮ್ಮ ನಗರವನ್ನು ಆರಿಸಿ, ನೀವು ನೋಡುವುದನ್ನು ಬರೆದು, ಸಾಧ್ಯವಾದರೆ ಫೋಟೋ ಸೇರಿಸಿ ಕಳುಹಿಸಿ. RA-00001 ನಂತಹ ಟ್ರ್ಯಾಕಿಂಗ್ ID ಸಿಗುತ್ತದೆ.",
        "ml": "Report Incident ലേക്ക് പോകുക (മുകളിലെ മെനു, ലോഗിൻ ആവശ്യമില്ല). ദുരന്തത്തിന്റെ തരവും നിങ്ങളുടെ നഗരവും തിരഞ്ഞെടുക്കുക, നിങ്ങൾ കാണുന്നത് എഴുതുക, കഴിയുമെങ്കിൽ ഫോട്ടോ ചേർത്ത് അയയ്ക്കുക. RA-00001 പോലുള്ള ട്രാക്കിംഗ് ID ലഭിക്കും.",
    },
    "track": {
        "en": "Go to Track Report and enter your tracking ID, for example RA-00001. The status is Open, Acknowledged or Resolved.",
        "hi": "Track Report पर जाएँ और अपनी ट्रैकिंग ID डालें, जैसे RA-00001। स्थिति Open, Acknowledged या Resolved होती है।",
        "mr": "Track Report वर जा आणि तुमची ट्रॅकिंग ID टाका, उदाहरण RA-00001. स्थिती Open, Acknowledged किंवा Resolved असते.",
        "bn": "Track Report-এ যান এবং আপনার ট্র্যাকিং ID দিন, যেমন RA-00001। অবস্থা Open, Acknowledged অথবা Resolved হয়।",
        "ta": "Track Report பக்கத்திற்குச் சென்று உங்கள் கண்காணிப்பு எண்ணை உள்ளிடவும், எடுத்துக்காட்டாக RA-00001. நிலை Open, Acknowledged அல்லது Resolved ஆக இருக்கும்.",
        "te": "Track Report కు వెళ్లి మీ ట్రాకింగ్ ID నమోదు చేయండి, ఉదాహరణకు RA-00001. స్థితి Open, Acknowledged లేదా Resolved.",
        "gu": "Track Report પર જાઓ અને તમારી ટ્રેકિંગ ID નાખો, ઉદાહરણ RA-00001. સ્થિતિ Open, Acknowledged કે Resolved હોય છે.",
        "kn": "Track Report ಗೆ ಹೋಗಿ ನಿಮ್ಮ ಟ್ರ್ಯಾಕಿಂಗ್ ID ನಮೂದಿಸಿ, ಉದಾಹರಣೆಗೆ RA-00001. ಸ್ಥಿತಿ Open, Acknowledged ಅಥವಾ Resolved ಆಗಿರುತ್ತದೆ.",
        "ml": "Track Report ലേക്ക് പോയി നിങ്ങളുടെ ട്രാക്കിംഗ് ID നൽകുക, ഉദാഹരണത്തിന് RA-00001. നില Open, Acknowledged അല്ലെങ്കിൽ Resolved ആണ്.",
    },
    "admin": {
        "en": "Admin login is at /admin. Demo login: username admin, password admin123. Citizens never need to log in.",
        "hi": "एडमिन लॉगिन /admin पर है। डेमो लॉगिन: यूज़रनेम admin, पासवर्ड admin123। नागरिकों को लॉगिन की ज़रूरत कभी नहीं होती।",
        "mr": "अ‍ॅडमिन लॉगिन /admin वर आहे. डेमो लॉगिन: वापरकर्तानाव admin, पासवर्ड admin123. नागरिकांना कधीही लॉगिनची गरज नसते.",
        "bn": "অ্যাডমিন লগইন /admin-এ। ডেমো লগইন: ইউজারনেম admin, পাসওয়ার্ড admin123। নাগরিকদের কখনও লগইনের দরকার হয় না।",
        "ta": "நிர்வாக உள்நுழைவு /admin இல் உள்ளது. டெமோ உள்நுழைவு: பயனர்பெயர் admin, கடவுச்சொல் admin123. குடிமக்கள் ஒருபோதும் உள்நுழையத் தேவையில்லை.",
        "te": "అడ్మిన్ లాగిన్ /admin లో ఉంది. డెమో లాగిన్: యూజర్‌నేమ్ admin, పాస్‌వర్డ్ admin123. పౌరులు ఎప్పుడూ లాగిన్ అవసరం లేదు.",
        "gu": "એડમિન લોગિન /admin પર છે. ડેમો લોગિન: યુઝરનેમ admin, પાસવર્ડ admin123. નાગરિકોને ક્યારેય લોગિનની જરૂર નથી.",
        "kn": "ನಿರ್ವಾಹಕ ಲಾಗಿನ್ /admin ನಲ್ಲಿದೆ. ಡೆಮೊ ಲಾಗಿನ್: ಬಳಕೆದಾರ ಹೆಸರು admin, ಪಾಸ್‌ವರ್ಡ್ admin123. ನಾಗರಿಕರು ಎಂದಿಗೂ ಲಾಗಿನ್ ಮಾಡಬೇಕಾಗಿಲ್ಲ.",
        "ml": "അഡ്മിൻ ലോഗിൻ /admin ൽ ആണ്. ഡെമോ ലോഗിൻ: ഉപയോക്തൃനാമം admin, പാസ്‌വേഡ് admin123. പൗരന്മാർക്ക് ഒരിക്കലും ലോഗിൻ ആവശ്യമില്ല.",
    },
    "safety_intro": {
        "en": "Safety guide. Read the short steps below in English, then open the full guide.",
        "hi": "सुरक्षा मार्गदर्शिका। नीचे दिए गए छोटे कदम अंग्रेज़ी में पढ़ें, फिर पूरी गाइड खोलें।",
        "mr": "सुरक्षा मार्गदर्शिका. खालील लहान पायऱ्या इंग्रजीत वाचा, मग पूर्ण मार्गदर्शिका उघडा.",
        "bn": "নিরাপত্তা নির্দেশিকা। নীচের ছোট ধাপগুলো ইংরেজিতে পড়ুন, তারপর পুরো নির্দেশিকা খুলুন।",
        "ta": "பாதுகாப்பு வழிகாட்டி. கீழே உள்ள குறுகிய படிகளை ஆங்கிலத்தில் படித்து, பின் முழு வழிகாட்டியைத் திறக்கவும்.",
        "te": "భద్రతా మార్గదర్శి. క్రింద ఉన్న చిన్న దశలను ఆంగ్లంలో చదివి, ఆపై పూర్తి మార్గదర్శిని తెరవండి.",
        "gu": "સલામતી માર્ગદર્શિકા. નીચેના ટૂંકા પગલાં અંગ્રેજીમાં વાંચો, પછી સંપૂર્ણ માર્ગદર્શિકા ખોલો.",
        "kn": "ಸುರಕ್ಷತಾ ಮಾರ್ಗದರ್ಶಿ. ಕೆಳಗಿನ ಸಣ್ಣ ಹಂತಗಳನ್ನು ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಓದಿ, ನಂತರ ಪೂರ್ಣ ಮಾರ್ಗದರ್ಶಿಯನ್ನು ತೆರೆಯಿರಿ.",
        "ml": "സുരക്ഷാ ഗൈഡ്. താഴെയുള്ള ചെറിയ ഘട്ടങ്ങൾ ഇംഗ്ലീഷിൽ വായിച്ച്, തുടർന്ന് പൂർണ്ണ ഗൈഡ് തുറക്കുക.",
    },
    "ask_city": {
        "en": "Tell me your city, for example 'Is Mira Road safe?', and I will check the active alerts for that tower.",
        "hi": "अपना शहर बताएँ, जैसे 'क्या Mira Road सुरक्षित है?', और मैं उस टावर के सक्रिय अलर्ट देखूँगा।",
        "mr": "तुमचे शहर सांगा, उदाहरण 'Mira Road सुरक्षित आहे का?', आणि मी त्या टॉवरचे सक्रिय इशारे तपासेन.",
        "bn": "আপনার শহরের নাম বলুন, যেমন 'Mira Road কি নিরাপদ?', আমি সেই টাওয়ারের সক্রিয় সতর্কতা দেখব।",
        "ta": "உங்கள் நகரத்தைச் சொல்லுங்கள், எடுத்துக்காட்டாக 'Mira Road பாதுகாப்பானதா?', அந்தக் கோபுரத்தின் செயலில் உள்ள எச்சரிக்கைகளை நான் பார்ப்பேன்.",
        "te": "మీ నగరం చెప్పండి, ఉదాహరణకు 'Mira Road సురక్షితమా?', ఆ టవర్‌లోని క్రియాశీల హెచ్చరికలను నేను చూస్తాను.",
        "gu": "તમારું શહેર કહો, ઉદાહરણ 'શું Mira Road સુરક્ષિત છે?', અને હું તે ટાવરની સક્રિય ચેતવણીઓ તપાસીશ.",
        "kn": "ನಿಮ್ಮ ನಗರವನ್ನು ಹೇಳಿ, ಉದಾಹರಣೆಗೆ 'Mira Road ಸುರಕ್ಷಿತವೇ?', ಆ ಗೋಪುರದ ಸಕ್ರಿಯ ಎಚ್ಚರಿಕೆಗಳನ್ನು ನಾನು ಪರಿಶೀಲಿಸುತ್ತೇನೆ.",
        "ml": "നിങ്ങളുടെ നഗരം പറയൂ, ഉദാഹരണത്തിന് 'Mira Road സുരക്ഷിതമാണോ?', ആ ടവറിലെ സജീവ മുന്നറിയിപ്പുകൾ ഞാൻ പരിശോധിക്കും.",
    },
}

QUICK_QUESTIONS = {
    "en": ["What to do in a flood?", "How do I report an incident?", "How do I track my report?", "Is my area safe?", "What is the emergency helpline?"],
    "hi": ["बाढ़ में क्या करें?", "मैं घटना की रिपोर्ट कैसे करूँ?", "मैं अपनी रिपोर्ट कैसे ट्रैक करूँ?", "क्या मेरा इलाका सुरक्षित है?", "आपातकालीन हेल्पलाइन क्या है?"],
    "mr": ["पुरात काय करावे?", "मी घटना कशी नोंदवू?", "मी माझी तक्रार कशी तपासू?", "माझा भाग सुरक्षित आहे का?", "आणीबाणी हेल्पलाइन कोणती?"],
    "bn": ["বন্যায় কী করব?", "আমি কীভাবে ঘটনা জানাব?", "আমি কীভাবে আমার রিপোর্ট দেখব?", "আমার এলাকা কি নিরাপদ?", "জরুরি হেল্পলাইন কী?"],
    "ta": ["வெள்ளத்தில் என்ன செய்வது?", "சம்பவத்தை எப்படி புகாரளிப்பது?", "என் புகாரை எப்படி கண்காணிப்பது?", "என் பகுதி பாதுகாப்பானதா?", "அவசர உதவி எண் என்ன?"],
    "te": ["వరదలో ఏమి చేయాలి?", "సంఘటనను ఎలా నివేదించాలి?", "నా రిపోర్ట్‌ను ఎలా ట్రాక్ చేయాలి?", "నా ప్రాంతం సురక్షితమా?", "అత్యవసర హెల్ప్‌లైన్ ఏమిటి?"],
    "gu": ["પૂરમાં શું કરવું?", "ઘટનાની જાણ કેવી રીતે કરવી?", "મારો રિપોર્ટ કેવી રીતે તપાસવો?", "શું મારો વિસ્તાર સુરક્ષિત છે?", "કટોકટી હેલ્પલાઇન કઈ છે?"],
    "kn": ["ಪ್ರವಾಹದಲ್ಲಿ ಏನು ಮಾಡಬೇಕು?", "ಘಟನೆಯನ್ನು ಹೇಗೆ ವರದಿ ಮಾಡುವುದು?", "ನನ್ನ ವರದಿಯನ್ನು ಹೇಗೆ ಟ್ರ್ಯಾಕ್ ಮಾಡುವುದು?", "ನನ್ನ ಪ್ರದೇಶ ಸುರಕ್ಷಿತವೇ?", "ತುರ್ತು ಸಹಾಯವಾಣಿ ಯಾವುದು?"],
    "ml": ["വെള്ളപ്പൊക്കത്തിൽ എന്തുചെയ്യണം?", "സംഭവം എങ്ങനെ റിപ്പോർട്ട് ചെയ്യാം?", "എന്റെ റിപ്പോർട്ട് എങ്ങനെ പരിശോധിക്കാം?", "എന്റെ പ്രദേശം സുരക്ഷിതമാണോ?", "അടിയന്തര ഹെൽപ്പ്‌ലൈൻ ഏതാണ്?"],
}

def _t(lang, key):
    return T.get(key, {}).get(lang) or T.get(key, {}).get("en") or key

def ui_strings(lang):
    if lang not in LANGS9:
        lang = "en"
    return {
        "greeting": _t(lang, "greeting"),
        "placeholder": _t(lang, "placeholder"),
        "fallback": _t(lang, "fallback"),
        "listening": _t(lang, "listening"),
        "voice_not_supported": _t(lang, "voice_not_supported"),
        "voice_denied": _t(lang, "voice_denied"),
        "questions": QUICK_QUESTIONS.get(lang, QUICK_QUESTIONS["en"]),
    }

def _slug(item):
    for k, v in SAFETY.items():
        if v is item:
            return k
    return "flood"

def _safety_answer(item, lang):
    lines = []
    lines.append("Before: " + " ".join(item["before"][:2]))
    lines.append("During: " + " ".join(item["during"][:2]))
    lines.append("After: " + " ".join(item["after"][:1]))
    lines.append("Full guide: /safety/" + _slug(item) + " . Helpline: 112, NDMA 1078.")
    return _t(lang, "safety_intro") + " " + item["title"] + ".\n" + "\n".join(lines)

def answer(message, db=None, lang="en"):
    if lang not in LANGS9:
        lang = "en"
    q = (message or "").strip().lower()
    if not q:
        return {"answer": _t(lang, "greeting"), "links": ["/safety"]}
    if "helpline" in q or "emergency number" in q or "112" in q or "1078" in q:
        return {"answer": _t(lang, "helpline"), "links": []}
    if "sos" in q or "i need help" in q or "help me" in q or "mujhe madad" in q:
        return {"answer": _t(lang, "sos"), "links": ["/"]}
    if "track" in q or "tracking" in q:
        return {"answer": _t(lang, "track"), "links": ["/track"]}
    if "report" in q:
        return {"answer": _t(lang, "report"), "links": ["/report"]}
    if "admin" in q and ("login" in q or "password" in q or "username" in q):
        return {"answer": _t(lang, "admin"), "links": ["/admin"]}
    if "push" in q or "notification" in q or "enable alert" in q:
        return {"answer": "Tap Enable alerts on the home page and allow notifications in your browser. You will get alerts on this device. This demo uses simulated push.", "links": ["/"]}
    if "language" in q or "hindi" in q or "marathi" in q:
        return {"answer": "Use the Language menu in the top bar. You can pick English, Hindi, Marathi, Bengali, Tamil, Telugu, Gujarati, Kannada or Malayalam for the main screens.", "links": ["/"]}
    if db is not None and ("safe" in q or "area" in q or "mira" in q or "nashik" in q or "surakshit" in q):
        cities = db.execute("SELECT city FROM towers").fetchall()
        for row in cities:
            city = row["city"].lower()
            if city in q:
                alerts = db.execute(
                    "SELECT a.title, a.severity FROM alerts a JOIN alert_towers at ON at.alert_id = a.id "
                    "JOIN towers t ON t.id = at.tower_id WHERE lower(t.city) = ?", (city,)).fetchall()
                if alerts:
                    names = ", ".join(a["title"] + " (" + a["severity"] + ")" for a in alerts)
                    return {"answer": "There is an active alert for " + row["city"] + ": " + names + ". Follow the safety guide and stay indoors if advised.", "links": ["/safety"]}
                return {"answer": "No active alert for " + row["city"] + " right now. The map shows the latest alerts for your tower.", "links": ["/"]}
        if "safe" in q or "surakshit" in q:
            return {"answer": _t(lang, "ask_city"), "links": ["/"]}
    keywords = {
        "flood": ["flood", "baadh", "badh", "paani", "water rising"],
        "earthquake": ["earthquake", "bhukamp", "tremor", "shaking"],
        "cyclone": ["cyclone", "toofan", "storm", "chakravat"],
        "landslide": ["landslide", "bhooskhalan"],
        "wildfire": ["wildfire", "fire", "aag", "forest fire"],
        "heatwave": ["heatwave", "heat", "garmi", "loo"],
        "tsunami": ["tsunami", "sunami"],
        "heavy-rainfall": ["heavy rain", "rainfall", "baarish", "heavy rainfall"],
    }
    for slug, words in keywords.items():
        if any(w in q for w in words):
            return {"answer": _safety_answer(SAFETY[slug], lang), "links": ["/safety/" + slug]}
    if "safety" in q or "what to do" in q or "how to stay safe" in q:
        return {"answer": _t(lang, "safety_intro") + " Pick Flood, Earthquake, Cyclone, Landslide, Wildfire, Heatwave, Tsunami or Heavy Rainfall.", "links": ["/safety"]}
    if "wind" in q or "map" in q:
        return {"answer": "The home page map shows all 60 towers. Red, orange, yellow or green pins mean an active alert. Wind arrows show wind direction and speed. The map refreshes every 60 seconds.", "links": ["/"]}
    return {"answer": _t(lang, "fallback"), "links": ["/safety"]}
