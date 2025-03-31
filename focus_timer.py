from datetime import datetime, timedelta
from enum import Enum
import time
import random
import threading

class TimerState(Enum):
    IDLE = "idle"
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    MICRO_BREAK = "micro_break"
    DEEP_FOCUS = "deep_focus"

class FocusTimer:
    def __init__(self, focus_time=30, short_break=7, long_break=20, micro_break=2, deep_focus_time=45, cycles_before_long_break=3):
        # Timer settings
        self.focus_time = focus_time * 60
        self.short_break = short_break * 60
        self.long_break = long_break * 60
        self.micro_break = micro_break * 60
        self.deep_focus_time = deep_focus_time * 60
        self.cycles_before_long_break = cycles_before_long_break
        
        # Timer state
        self.current_state = TimerState.IDLE
        self.running = False
        self.is_paused = False
        self.current_task = None
        self.remaining_time = 0
        
        # Threading controls
        self.timer_thread = None
        self.pause_event = threading.Event()
        self.pause_event.set()
        
        # Statistics
        self.completed_cycles = 0
        self.consecutive_focus_sessions = 0
        self.session_stats = {
            'total_focus_time': 0,
            'completed_cycles': 0,
            'tasks_completed': 0,
            'deep_focus_sessions': 0,
            'micro_breaks_taken': 0
        }

    def notify(self, message):
        print(f"\n[NOTIFICATION] {message}")

    def start_timer(self, duration, message):
        self.running = True
        self.is_paused = False
        self.remaining_time = duration
        while self.remaining_time > 0 and self.running:
            self.pause_event.wait()  # Wait if paused
            if not self.running:
                break
            time.sleep(1)
            self.remaining_time -= 1
        if self.running:
            self.notify(message)

    def start_focus(self, task_description=None):
        self.current_task = task_description
        self.running = True
        self.is_paused = False
        self.pause_event.set()
        
        if not self.timer_thread or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()
        
        message = f"Focus session started! Focus for {self.focus_time // 60} minutes"
        self.notify(message)
        return message

    def pause(self):
        if self.running and not self.is_paused:
            self.is_paused = True
            self.pause_event.clear()
            return "Timer paused"
        return "No active timer to pause"

    def resume(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            return "Timer resumed"
        return "Timer is not paused"

    def stop(self):
        self.running = False
        self.is_paused = False
        self.current_state = TimerState.IDLE
        self.pause_event.set()
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join()
        return "Timer stopped"

    def run_timer(self):
        for cycle in range(1, 4):  # Three focus cycles
            if not self.running:
                break
            
            # Determine focus type based on consecutive sessions
            if self.consecutive_focus_sessions >= 2 and random.random() < 0.4:
                self.current_state = TimerState.DEEP_FOCUS
                duration = self.deep_focus_time
                self.session_stats['deep_focus_sessions'] += 1
                message = f"Deep Focus Session {cycle}: Focus intensely for {duration // 60} minutes"
            else:
                self.current_state = TimerState.FOCUS
                duration = self.focus_time
                message = f"Cycle {cycle}: Focus for {duration // 60} minutes"
            
            print(message)
            self.notify(message)
            self.start_timer(duration, "Focus session over! Take a break!")
            
            if not self.running:
                break
            
            # Handle breaks
            if cycle < 3:  # Short breaks between focus sessions
                self.current_state = TimerState.SHORT_BREAK
                print(f"Time for a {self.short_break // 60}-minute break!")
                self.notify(f"Take a {self.short_break // 60}-minute break!")
                self.start_timer(self.short_break, "Break over! Get ready for next session!")
            else:  # Long break after completing all cycles
                self.current_state = TimerState.LONG_BREAK
                print(f"Great job! Take a {self.long_break // 60}-minute break!")
                self.notify(f"Take a {self.long_break // 60}-minute break!")
                self.start_timer(self.long_break, "Session complete! Well done!")
            
            self.completed_cycles += 1
            self.consecutive_focus_sessions += 1
            self.session_stats['completed_cycles'] += 1
        
        self.running = False
        self.current_state = TimerState.IDLE

    def _calculate_remaining_time(self):
        return self.remaining_time

    def get_stats(self):
        return f"""Focus Sessions:
• Total Focus Time: {self.session_stats['total_focus_time']:.1f} minutes
• Completed Cycles: {self.session_stats['completed_cycles']}
• Tasks Completed: {self.session_stats['tasks_completed']}
• Deep Focus Sessions: {self.session_stats['deep_focus_sessions']}
• Micro-breaks Taken: {self.session_stats['micro_breaks_taken']}"""

    def get_total_time(self):
        if self.current_state in [TimerState.FOCUS, TimerState.DEEP_FOCUS]:
            return (self.focus_time if self.current_state == TimerState.FOCUS else self.deep_focus_time) - self.remaining_time
        return 0

    def get_status(self):
        state_text = f"Current state: {self.current_state.value}"
        time_text = f"Time remaining: {self.remaining_time // 60:02d}:{self.remaining_time % 60:02d}"
        task_text = f"Current task: {self.current_task}" if self.current_task else ""
        return "\n".join([state_text, time_text, task_text])

    def complete_cycle(self):
        if self.current_state in [TimerState.FOCUS, TimerState.DEEP_FOCUS]:
            self.session_stats['tasks_completed'] += 1
            self.session_stats['total_focus_time'] += self.get_total_time() / 60
            
            if self.current_state == TimerState.DEEP_FOCUS:
                self.session_stats['deep_focus_sessions'] += 1
            
            self.completed_cycles += 1
            self.consecutive_focus_sessions += 1
            message = "Focus session completed successfully!"
            self.notify(message)
            
            # Start appropriate break
            if self.completed_cycles % self.cycles_before_long_break == 0:
                self.current_state = TimerState.LONG_BREAK
                self.remaining_time = self.long_break
                return f"Great work! Take a long break ({self.long_break // 60} minutes)"
            else:
                self.current_state = TimerState.SHORT_BREAK
                self.remaining_time = self.short_break
                return f"Good job! Take a short break ({self.short_break // 60} minutes)"
        return "Can only complete focus or deep focus sessions"