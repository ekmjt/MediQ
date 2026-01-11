import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable is required. "
        "Please create a .env file in the backend directory with: GEMINI_API_KEY=your_key_here"
    )
genai.configure(api_key=api_key)


def get_available_model():
    """Get an available Gemini model, trying multiple options"""
    # List of models to try in order of preference (newer models first)
    model_names = [
        'gemini-2.5-flash',  # Fastest and most cost-effective
        'gemini-2.5-pro',   # More capable for complex tasks
        'gemini-2.0-flash',  # Fallback option
        'gemini-2.0-flash-exp',  # Experimental fallback
        'gemini-1.5-flash',  # Older versions as last resort
        'gemini-1.5-pro',
        'gemini-pro',
    ]
    
    # Try to list available models first
    try:
        available_models = [m.name for m in genai.list_models()]
        print(f"Available models: {available_models}")
        
        # Extract model names (they might be in format 'models/gemini-2.5-flash')
        model_base_names = [m.split('/')[-1] if '/' in m else m for m in available_models]
        
        # Check if any of our preferred models are available
        for preferred_model in model_names:
            if preferred_model in model_base_names:
                print(f"Found available model: {preferred_model}")
                return preferred_model
        
        # If none of our preferred models found, use the first available gemini model
        gemini_models = [m for m in model_base_names if 'gemini' in m.lower() and 'embedding' not in m.lower()]
        if gemini_models:
            selected = gemini_models[0]
            print(f"Using first available Gemini model: {selected}")
            return selected
    except Exception as e:
        print(f"Could not list models: {e}, will try direct initialization")
    
    # If listing failed, try direct initialization with newest model
    return 'gemini-2.5-flash'


class GeminiService:
    def __init__(self):
        # Get an available model
        model_name = get_available_model()
        try:
            self.model = genai.GenerativeModel(model_name)
            self.model_name = model_name  # Store model name for reference
            print(f"Successfully initialized Gemini model: {model_name}")
        except Exception as e:
            # If initialization fails, try to list available models and show helpful error
            try:
                available_models = [m.name for m in genai.list_models()]
                available_model_names = [m.split('/')[-1] if '/' in m else m for m in available_models]
                error_msg = (
                    f"Failed to initialize model '{model_name}'. "
                    f"Available models: {', '.join(available_model_names)}. "
                    f"Error: {str(e)}"
                )
                print(error_msg)
                # Try newer models as fallback
                fallback_models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-1.5-flash']
                for fallback_model in fallback_models:
                    if fallback_model in available_model_names:
                        print(f"Trying fallback model: {fallback_model}")
                        self.model = genai.GenerativeModel(fallback_model)
                        self.model_name = fallback_model  # Store model name
                        return
                raise ValueError(error_msg)
            except Exception as list_error:
                raise ValueError(
                    f"Failed to initialize Gemini model '{model_name}'. "
                    f"Could not list available models. Error: {str(e)}. "
                    f"List error: {str(list_error)}"
                )
        self.system_prompt = """You are a professional medical triage assistant for a hospital system called MediQueue. 
Your role is to:
1. Have a compassionate, professional conversation with patients about their symptoms
2. Collect information about their condition through natural dialogue
3. Assess the severity of their condition on a scale of 1-10
4. Provide appropriate home care guidance while they wait
5. Identify emergency situations that need immediate attention

Guidelines:
- Be empathetic and professional
- Ask follow-up questions to understand the full picture
- Don't diagnose, but assess severity
- Provide practical home care advice when appropriate
- Always prioritize patient safety

After each conversation turn, you should respond naturally to the patient, but also be ready to provide a structured assessment when asked."""

    def get_conversation_response(self, messages: List[Dict], user_history: Optional[Dict] = None) -> str:
        """Get AI response for conversation"""
        conversation_text = self._format_conversation(messages, user_history)
        
        try:
            prompt = f"{self.system_prompt}\n\nConversation so far:\n{conversation_text}\n\nRespond naturally to the patient:"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_str = str(e)
            # Provide more helpful error message
            if "404" in error_str or "not found" in error_str.lower():
                try:
                    available_models = [m.name.split('/')[-1] if '/' in m.name else m.name for m in genai.list_models()]
                    error_str += f" Available models: {', '.join(available_models[:5])}"
                except:
                    pass
            return f"I apologize, I'm having trouble processing that. Could you please repeat? Error: {error_str}"

    def analyze_triage(self, messages: List[Dict], user_history: Optional[Dict] = None) -> Dict:
        """Analyze conversation and extract triage information"""
        conversation_text = self._format_conversation(messages, user_history)
        
        analysis_prompt = f"""{self.system_prompt}

Based on this conversation, provide a structured assessment in JSON format:
{{
    "severity_score": <number 1-10>,
    "severity_reasoning": "<brief explanation>",
    "home_guidance": "<specific advice for what patient can do at home>",
    "emergency_flag": <true/false>,
    "emergency_reason": "<if emergency, why>",
    "symptoms_summary": "<brief summary of reported symptoms>"
}}

Conversation:
{conversation_text}

Provide ONLY the JSON response, no additional text:"""

        try:
            response = self.model.generate_content(analysis_prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            triage_data = json.loads(response_text)
            
            # Ensure severity_score is between 1-10
            triage_data["severity_score"] = max(1, min(10, float(triage_data.get("severity_score", 5))))
            
            return triage_data
        except Exception as e:
            # Fallback if JSON parsing fails
            return {
                "severity_score": 5.0,
                "severity_reasoning": "Unable to analyze - defaulting to moderate severity",
                "home_guidance": "Please monitor your symptoms and seek medical attention if they worsen.",
                "emergency_flag": False,
                "emergency_reason": "",
                "symptoms_summary": "Analysis unavailable"
            }

    def check_misuse(self, current_severity: float, user_history: Optional[Dict]) -> Dict:
        """Check for potential misuse based on user history"""
        if not user_history or not user_history.get("previous_severities"):
            return {"is_misuse": False, "confidence": 0.0, "reason": ""}
        
        previous_severities = user_history["previous_severities"]
        misuse_count = user_history.get("misuse_count", 0)
        
        # Check if current severity is significantly higher than historical average
        avg_severity = sum(previous_severities) / len(previous_severities)
        severity_diff = current_severity - avg_severity
        
        # Flag if severity jumped significantly (more than 3 points) and user has history of misuse
        if severity_diff > 3 and misuse_count > 0:
            return {
                "is_misuse": True,
                "confidence": 0.7,
                "reason": f"Severity score ({current_severity}) is significantly higher than your historical average ({avg_severity:.1f})."
            }
        
        return {"is_misuse": False, "confidence": 0.0, "reason": ""}

    def _format_conversation(self, messages: List[Dict], user_history: Optional[Dict] = None) -> str:
        """Format conversation messages into text"""
        formatted = []
        
        if user_history and user_history.get("misuse_count", 0) > 0:
            formatted.append(f"[Note: This user has {user_history['misuse_count']} previous misuse flags. Please verify their responses carefully.]")
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(formatted)

