import os
from io import BytesIO
from typing import Optional, List, Dict, Any
from groq import Groq
from gtts import gTTS
from dotenv import load_dotenv

# Load env variables (such as GROQ_API_KEY) using absolute paths
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=env_path)


class AICoachService:
    """
    Virtual fitness trainer service supplying AI form feedback and audio readings.
    """

    @classmethod
    def get_groq_client(cls, api_key_override: Optional[str] = None) -> Optional[Groq]:
        """
        Retrieves the Groq client, prioritizing settings overrides over environment variables.
        """
        api_key = api_key_override or os.environ.get("GROQ_API_KEY")
        if not api_key:
            return None
        try:
            return Groq(api_key=api_key)
        except Exception:
            return None

    @classmethod
    def ask_coach(
        cls,
        user_message: str,
        chat_history: List[Dict[str, str]],
        workout_context: Optional[str] = None,
        api_key_override: Optional[str] = None
    ) -> str:
        """
        Submits the user question to the AI Coach LLM. Falls back to a local rule-based engine if offline.
        """
        client = cls.get_groq_client(api_key_override)
        system_prompt = (
            "You are RepSense Coach, an expert AI fitness coach and personal trainer. "
            "Your tone is motivational, professional, and clear. "
            "You give short, actionable advice on exercise form, workouts, routines, and recovery. "
            "Keep your responses concise (under 3 sentences) because they will be read aloud to the user."
        )

        if workout_context:
            system_prompt += f"\nHere is the current user's profile/workout summary to contextually base your feedback on: {workout_context}"

        if client:
            try:
                messages = [{"role": "system", "content": system_prompt}]
                # Append last few messages in chat history (limit context size to 5 for rapid response)
                for h in chat_history[-5:]:
                    messages.append({"role": h["role"], "content": h["content"]})
                
                messages.append({"role": "user", "content": user_message})

                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                # Log error and fall back to local rule-based coach
                print(f"Groq API Error: {e}")

        # --- Rule-based Local Coach fallback ---
        message_lower = user_message.lower()
        if "squat" in message_lower:
            return (
                "For squats, remember to keep your chest up, brace your core, and drop until your hips are parallel with "
                "your knees. Keep your heels firmly planted on the ground."
            )
        elif "pushup" in message_lower or "push up" in message_lower:
            return (
                "Keep your body in a straight line from head to heels. Avoid letting your hips sag or pike up. "
                "Tuck your elbows at a 45-degree angle rather than flaring them."
            )
        elif "curl" in message_lower:
            return (
                "Keep your elbows locked at your side to prevent elbow drift. Do not swing your hips or use momentum "
                "to raise the weights; control the negative path."
            )
        elif "lunge" in message_lower:
            return (
                "Ensure your front knee does not bend past your toes. Keep your weight centered and step "
                "directly forward to maintain balance."
            )
        elif "shoulder press" in message_lower or "overhead press" in message_lower:
            return (
                "Brace your core to keep a neutral spine and avoid hyperextending your lower back. "
                "Extend your arms fully overhead at the top of the movement."
            )
        elif "motivation" in message_lower or "tired" in message_lower or "hard" in message_lower:
            return (
                "Every single rep counts! Focus on your form, breathe deep, and remember why you started. "
                "You are stronger than you think. Let's crush this set!"
            )
        else:
            return (
                "I am here to help you get the most out of your workouts. Ask me anything about squats, "
                "pushups, bicep curls, lunges, or overhead presses!"
            )

    @classmethod
    def generate_speech(cls, text: str) -> Optional[bytes]:
        """
        Synthesizes speech from a text input using gTTS.
        Returns the generated audio as bytes (MP3) or None on failure.
        """
        try:
            # Clean text of any emojis or special symbols
            clean_text = text.encode("ascii", "ignore").decode("ascii")
            if not clean_text.strip():
                clean_text = "Keep going!"
                
            tts = gTTS(text=clean_text, lang="en", slow=False)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception as e:
            print(f"Text-to-Speech Error: {e}")
            return None
