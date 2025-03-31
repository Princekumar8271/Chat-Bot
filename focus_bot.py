import random
import google.generativeai as genai
from focus_timer import FocusTimer

class FocusBot:
    # Add timer integration to FocusBot
    def __init__(self):
        self.timer = FocusTimer()  # Add this line
        # Configure Gemini AI
        genai.configure(api_key="AIzaSyDi9dguUXe03mjj1eayIFMALyJpIq_Fb4A")
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.conversation_history = []

    def get_ai_response(self, prompt):
        try:
            context = """You are Beluga, an AI study assistant. Be friendly and conversational while helping users with their studies and productivity.
            Key features of the Beluga Technique:
            - Regular focus sessions (30 minutes)
            - Deep focus sessions (45 minutes)
            - Short breaks (7 minutes)
            - Micro-breaks (2 minutes)
            - Long breaks (20 minutes after 3 cycles)"""
            
            full_prompt = f"{context}\n\nUser: {prompt}"
            response = self.model.generate_content(full_prompt)
            
            # Check if response is valid and extract text
            if response and hasattr(response, 'text'):
                return response.text
            elif isinstance(response, str):
                return response
            else:
                return "I'm processing your request..."
                
        except Exception as e:
            print(f"AI Response Error: {str(e)}")
            return "I'm having trouble connecting. Please try again."

    def process_command(self, command):
        # Add timer-related commands
        if command.startswith('start'):
            task = command[6:].strip() if len(command) > 6 else ''
            return self.timer.start_focus(task)
        elif command == 'pause':
            return self.timer.pause()
        elif command == 'resume':
            return self.timer.resume()
        elif command == 'stop':
            return self.timer.stop()
        elif command == 'complete':
            return self.timer.complete_cycle()
        elif command == 'stats':
            return self.timer.get_stats()
        elif command == 'status':
            return self.timer.get_status()
        elif command == 'help':
            return self._get_help_message()
        
        # For everything else, use AI conversation
        return self.get_ai_response(command)

    def _get_help_message(self):
        # Help message remains the same
        help_text = "Available commands:\n"
        help_text += "- start [task]: Start a Beluga focus session with optional task description\n"
        help_text += "- pause: Pause the current timer\n"
        help_text += "- resume: Resume a paused timer\n"
        help_text += "- stop: Stop the current timer\n"
        help_text += "- status: Check the current timer status\n"
        help_text += "- stats: View your Beluga Technique statistics\n"
        help_text += "- complete: Complete current focus session and start a break\n"
        help_text += "- motivate: Get a motivational message\n"
        help_text += "- hlo/hello/hi: Get a greeting and a study tip\n"
        help_text += "- study tips: Get a list of Beluga Technique tips to improve study focus\n"
        help_text += "- help: Show this help message\n\n"
        help_text += "About the Beluga Technique:\n"
        help_text += "- Regular focus sessions: 30 minutes\n"
        help_text += "- Deep focus sessions: 45 minutes (unlocked after consecutive focus sessions)\n"
        help_text += "- Short breaks: 7 minutes\n"
        help_text += "- Micro-breaks: 2 minutes (randomly offered for quick refreshes)\n"
        help_text += "- Long breaks: 20 minutes (after 3 completed cycles)\n"
        help_text += "The Beluga Technique adapts to your study patterns for optimal productivity!"
        return help_text