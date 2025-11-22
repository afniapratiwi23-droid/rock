import google.generativeai as genai
from prompts import SYSTEM_PROMPT, OUTLINE_PROMPT_TEMPLATE, CHAPTER_PROMPT_TEMPLATE
import streamlit as st

# Global state for API keys
api_keys = []
current_key_index = 0

def configure_genai(keys):
    global api_keys, current_key_index
    
    # Ensure keys is a list
    if isinstance(keys, str):
        keys = [keys]
        
    valid_keys = [k for k in keys if k and k.strip()]
    
    if not valid_keys:
        st.error("No valid API keys provided.")
        return False
        
    api_keys = valid_keys
    current_key_index = 0
    
    try:
        # Configure with the first key
        genai.configure(api_key=api_keys[current_key_index])
        
        # Debug: List available models
        print(f"Configured with API Key #{current_key_index + 1}")
        print("Checking available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Available model: {m.name}")
                
        return True
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}")
        return False

def rotate_api_key():
    global current_key_index
    
    if len(api_keys) <= 1:
        print("Only one API key available, cannot rotate.")
        return False
        
    # Move to next key
    current_key_index = (current_key_index + 1) % len(api_keys)
    new_key = api_keys[current_key_index]
    
    print(f"Rotating to API Key #{current_key_index + 1}...")
    try:
        genai.configure(api_key=new_key)
        return True
    except Exception as e:
        print(f"Failed to rotate key: {e}")
        return False

def generate_content_with_fallback(prompt):
    # Prioritize the SMARTEST models first
    models_to_try = [
        'gemini-2.5-pro-002',  # Latest and smartest
        'gemini-2.5-pro',
        'gemini-2.0-pro-exp',
        'gemini-2.5-flash',
        'gemini-2.0-flash-exp',
        'gemini-1.5-pro',
    ]
    
    # Generation config for better quality
    generation_config = {
        'temperature': 0.7,  # Balanced creativity and coherence
        'top_p': 0.95,
        'top_k': 40,
        'max_output_tokens': 8192,
    }
    
    # Safety settings to block as little as possible
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    for model_name in models_to_try:
        # Retry loop for API key rotation
        max_retries = len(api_keys) if api_keys else 1
        
        for attempt in range(max_retries):
            try:
                print(f"Trying model: {model_name} (Key #{current_key_index + 1})")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    safety_settings=safety_settings,
                    generation_config=generation_config
                )
                
                if response.text:
                    print(f"Success with model: {model_name}")
                    return response.text
                else:
                    print(f"Empty response from {model_name}, trying next...")
                    break # Break retry loop to try next model
                    
            except Exception as e:
                error_str = str(e)
                # Check for Quota Exceeded / Resource Exhausted (429)
                if "429" in error_str or "Resource has been exhausted" in error_str or "Quota exceeded" in error_str:
                    print(f"Quota exceeded for Key #{current_key_index + 1}. Rotating key...")
                    if rotate_api_key():
                        continue # Retry with new key
                    else:
                        print("Cannot rotate key (no more keys or rotation failed).")
                        break # Try next model
                
                print(f"Error with {model_name}: {e}")
                break # Try next model
    
    raise Exception("All models failed to generate content (or all keys exhausted)")

def generate_ebook_metadata(topic):
    try:
        prompt = f"""
        Analisis topik ebook ini: "{topic}"
        
        Berikan rekomendasi metadata dalam format JSON:
        {{
            "target_audience": "Siapa target pembaca spesifiknya?",
            "tone": "Pilih satu: Lucu, Santai, dan Mengena | Formal & Profesional | Motivasi Menggebu-gebu | Sarkas & Humoris | Empatik & Lembut",
            "core_problem": "Apa masalah utama yang diselesaikan (1-2 kalimat)?",
            "core_message": "Apa pesan utama ebook ini (1 kalimat)?",
            "case_study_type": "Pilih satu: Kantoran umum (HR, atasan, tim) | Bisnis Online / UMKM | Kehidupan Rumah Tangga | Mahasiswa / Akademik | Freelancer / Remote Work",
            "emotional_tone": "Pilih satu: Satir tajam (menyindir realitas) | Optimis & Membangun | Realistis & Logis | Provokatif & Menantang"
        }}
        """
        response = generate_content_with_fallback(prompt)
        
        # Simple JSON parsing (robustness improvement needed for prod)
        import json
        import re
        
        # Extract JSON from response
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        return None
    except Exception as e:
        st.error(f"Error generating metadata: {e}")
        return None

def generate_outline(topic, num_chapters=6):
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\n{OUTLINE_PROMPT_TEMPLATE.format(topic=topic, num_chapters=num_chapters)}"
        text_response = generate_content_with_fallback(full_prompt)
        
        print(f"DEBUG: Raw response for topic '{topic}':\n{text_response}") # Debug print

        if not text_response:
            print("DEBUG: Empty response received")
            return []

        # Robust parsing: look for lines starting with numbers, dashes, or 'Bab'/'Chapter'
        outline = []
        for line in text_response.split('\n'):
            clean_line = line.strip()
            # Remove markdown bolding for checking
            check_line = clean_line.replace('*', '').strip()
            
            if not check_line:
                continue

            # Check for various list formats
            is_list_item = (
                check_line[0].isdigit() or 
                check_line.startswith('-') or 
                check_line.lower().startswith('bab') or 
                check_line.lower().startswith('chapter')
            )
            
            if is_list_item:
                # Remove numbering, bullets, and "Bab X" prefixes
                import re
                # Remove leading markdown/bullets
                content = clean_line.lstrip('*1234567890.- ').strip()
                
                # Remove "Bab X:" or "Chapter X:" prefix if present
                if ':' in content:
                    parts = content.split(':', 1)
                    if len(parts[0]) < 15: 
                        content = parts[1].strip()
                
                # Final cleanup of bold markers
                content = content.replace('**', '').strip()
                
                if content:
                    outline.append(content)
        
        print(f"DEBUG: Parsed outline: {outline}")
        return outline
    except Exception as e:
        st.error(f"Error generating outline: {e}")
        return []

def generate_chapter(topic, chapter_title, params, chapter_num, outline):
    try:
        # Determine special instructions based on chapter number
        if chapter_num == 1:
            special_instruction = (
                "⚠️ KHUSUS BAB 1: FOKUS PADA 'PROBLEM AGITATION' & 'WHY'.\n"
                "- JANGAN berikan langkah-langkah teknis atau listicle (misal: 5 Cara, 7 Tips) di sini.\n"
                "- Gali keresahan/pain points pembaca sedalam-dalamnya. Buat mereka merasa 'Ini gue banget!'.\n"
                "- Jelaskan konsekuensi fatal jika masalah ini tidak diatasi (Hell Scenario).\n"
                "- Tujuannya: Membangun urgensi dan koneksi emosional sebelum masuk ke solusi di bab berikutnya."
            )
        else:
            special_instruction = (
                "FOKUS PADA SOLUSI PRAKTIS (HOW-TO).\n"
                "- Berikan langkah-langkah konkret yang bisa langsung dipraktikkan.\n"
                "- Gunakan studi kasus atau contoh nyata.\n"
                "- Pastikan pembaca tahu apa yang harus dilakukan setelah membaca bab ini."
            )

        detailed_prompt = CHAPTER_PROMPT_TEMPLATE.format(
            topic=topic,
            chapter_title=chapter_title,
            chapter_num=chapter_num,
            special_instruction=special_instruction,
            outline=outline,
            target_audience=params.get("target_audience", "Profesional Muda / Pemula"),
            tone=params.get("tone", "Profesional, Hangat, Memotivasi"),
            word_count=params.get("word_count", 800),
            case_study_type=params.get("case_study_type", "Studi Kasus Nyata"),
            perspective=params.get("perspective", "Otomatis"),
            core_problem=params.get("core_problem", ""),
            core_message=params.get("core_message", ""),
            emotional_tone=params.get("emotional_tone", "Netral")
        )
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{detailed_prompt}"
        content = generate_content_with_fallback(full_prompt)
        print(f"DEBUG: Content for chapter '{chapter_title}':\n{content[:200]}...") # Debug print
        return content
    except Exception as e:
        st.error(f"Error generating chapter '{chapter_title}': {e}")
        return ""

def generate_preface(topic, params):
    try:
        from prompts import PREFACE_PROMPT_TEMPLATE
        detailed_prompt = PREFACE_PROMPT_TEMPLATE.format(
            topic=topic,
            target_audience=params.get("target_audience", "Umum"),
            tone=params.get("tone", "Santai")
        )
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{detailed_prompt}"
        content = generate_content_with_fallback(full_prompt)
        print(f"DEBUG: Preface generated:\n{content[:200]}...")
        return content
    except Exception as e:
        st.error(f"Error generating preface: {e}")
        return ""

def generate_conclusion(topic, params):
    try:
        from prompts import CONCLUSION_PROMPT_TEMPLATE
        detailed_prompt = CONCLUSION_PROMPT_TEMPLATE.format(
            topic=topic,
            core_message=params.get("core_message", ""),
            tone=params.get("tone", "Santai")
        )
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{detailed_prompt}"
        content = generate_content_with_fallback(full_prompt)
        print(f"DEBUG: Conclusion generated:\n{content[:200]}...")
        return content
    except Exception as e:
        st.error(f"Error generating conclusion: {e}")
        return ""
