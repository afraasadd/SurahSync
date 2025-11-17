"""
Hifz Testing GUI - Auto-advance with hidden ayahs
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from quran_data import load_dataset


class HifzCompanionGUI:
    def __init__(self, root, hifz_tester):
        self.root = root
        self.tester = hifz_tester
        self.root.title("Hifz Companion - Memorization Test")
        self.root.geometry("900x750")

        # Load Quran data for surah selection
        self.quran_data = load_dataset()

        # GUI state
        self.is_test_active = False
        self.is_recording = False
        self.auto_advance = True  # Auto-advance to next ayah

        self.setup_gui()

    def setup_gui(self):
        """Setup the complete hifz testing interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame,
                               text="🕌 Hifz Companion - Memorization Test",
                               font=("Arial", 16, "bold"),
                               fg='#2c5530')
        title_label.pack(pady=10)

        # Test Setup Frame
        setup_frame = ttk.LabelFrame(main_frame, text="Test Setup", padding="10")
        setup_frame.pack(fill=tk.X, pady=10)

        # Surah Selection
        ttk.Label(setup_frame, text="Surah:").grid(row=0, column=0, padx=5, sticky='w')
        self.surah_var = tk.StringVar()
        self.surah_combo = ttk.Combobox(setup_frame, textvariable=self.surah_var, width=20)
        self.surah_combo['values'] = [f"{i}. Surah" for i in range(1, 115)]
        self.surah_combo.set("1. Surah")
        self.surah_combo.grid(row=0, column=1, padx=5)

        # Start Ayah
        ttk.Label(setup_frame, text="Start Ayah:").grid(row=0, column=2, padx=5, sticky='w')
        self.start_ayah_var = tk.StringVar(value="1")
        self.start_ayah_spin = ttk.Spinbox(setup_frame, from_=1, to=286,
                                           textvariable=self.start_ayah_var, width=5)
        self.start_ayah_spin.grid(row=0, column=3, padx=5)

        # Ayah Count
        ttk.Label(setup_frame, text="Ayahs to Test:").grid(row=0, column=4, padx=5, sticky='w')
        self.ayah_count_var = tk.StringVar(value="5")
        self.ayah_count_spin = ttk.Spinbox(setup_frame, from_=1, to=50,
                                           textvariable=self.ayah_count_var, width=5)
        self.ayah_count_spin.grid(row=0, column=5, padx=5)

        # Test Controls
        self.start_test_btn = ttk.Button(setup_frame,
                                         text="🚀 Start Hifz Test",
                                         command=self.start_hifz_test)
        self.start_test_btn.grid(row=0, column=6, padx=10)

        self.end_test_btn = ttk.Button(setup_frame,
                                       text="⏹️ End Test",
                                       command=self.end_hifz_test,
                                       state='disabled')
        self.end_test_btn.grid(row=0, column=7, padx=5)

        # Current Ayah Display (HIDDEN - only shows position)
        ayah_frame = ttk.LabelFrame(main_frame, text="Current Ayah", padding="15")
        ayah_frame.pack(fill=tk.X, pady=10)

        self.ayah_info_label = tk.Label(ayah_frame,
                                        text="🎯 Start test to begin memorization recitation",
                                        font=("Arial", 14, "bold"),
                                        fg='#2c5530')
        self.ayah_info_label.pack(pady=10)

        # Hidden text indicator
        self.hidden_text_label = tk.Label(ayah_frame,
                                          text="❌ Ayah Text Hidden - Recite from Memory",
                                          font=("Arial", 12),
                                          fg='#cc0000')
        self.hidden_text_label.pack(pady=5)

        # Recitation Controls
        recitation_frame = ttk.LabelFrame(main_frame, text="Recitation", padding="15")
        recitation_frame.pack(fill=tk.X, pady=10)

        self.record_btn = ttk.Button(recitation_frame,
                                     text="🎤 Start Recording & Auto-Continue",
                                     command=self.toggle_recording,
                                     state='disabled')
        self.record_btn.pack(pady=5)

        # Auto-continue info
        self.auto_info_label = tk.Label(recitation_frame,
                                        text="➡️ Will automatically continue to next ayah after evaluation",
                                        font=("Arial", 10),
                                        fg='#666666')
        self.auto_info_label.pack()

        # Your Recitation
        user_frame = ttk.LabelFrame(main_frame, text="Your Recitation & Results", padding="15")
        user_frame.pack(fill=tk.X, pady=10)

        self.recitation_text = scrolledtext.ScrolledText(user_frame,
                                                         height=3,
                                                         font=("Arial", 12),
                                                         wrap=tk.WORD)
        self.recitation_text.pack(fill=tk.BOTH, expand=True)

        # Results Display
        results_frame = ttk.LabelFrame(main_frame, text="Live Test Results", padding="15")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Score Display
        score_frame = ttk.Frame(results_frame)
        score_frame.pack(fill=tk.X, pady=5)

        self.score_label = tk.Label(score_frame,
                                    text="Score: --%",
                                    font=("Arial", 20, "bold"))
        self.score_label.pack(side=tk.LEFT, padx=10)

        self.feedback_label = tk.Label(score_frame,
                                       text="Start your test to see feedback",
                                       font=("Arial", 12))
        self.feedback_label.pack(side=tk.LEFT, padx=20)

        # Session Progress
        self.progress_label = tk.Label(score_frame,
                                       text="Progress: 0/0 ayahs",
                                       font=("Arial", 10),
                                       fg='#666666')
        self.progress_label.pack(side=tk.RIGHT, padx=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(score_frame, orient='horizontal', length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=10)

        # Detailed Results
        details_frame = ttk.Frame(results_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)

        self.details_text = scrolledtext.ScrolledText(details_frame,
                                                      height=8,
                                                      font=("Courier", 10))
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready to start hifz test...")
        status_bar = ttk.Label(main_frame,
                               textvariable=self.status_var,
                               relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=5)

    def start_hifz_test(self):
        """Start a new hifz test session"""
        try:
            surah_num = int(self.surah_var.get().split('.')[0])
            start_ayah = int(self.start_ayah_var.get())
            ayah_count = int(self.ayah_count_var.get())

            # Start test session
            current_ayah = self.tester.start_hifz_test(surah_num, start_ayah, ayah_count)

            if current_ayah:
                self.is_test_active = True
                self.update_ayah_display(current_ayah)

                # Enable controls
                self.record_btn.config(state='normal')
                self.start_test_btn.config(state='disabled')
                self.end_test_btn.config(state='normal')

                self.status_var.set(f"Hifz test started: {ayah_count} ayahs from Surah {surah_num}")
                self.update_session_display()
            else:
                messagebox.showerror("Error", "Could not start test session")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start test: {e}")

    def end_hifz_test(self):
        """End the current hifz test"""
        if self.is_test_active:
            summary = self.tester.end_session()

            # Show final results
            if summary:
                messagebox.showinfo("Test Complete",
                                    f"🎉 Test Complete!\n\n"
                                    f"Final Accuracy: {summary['accuracy']:.1f}%\n"
                                    f"Total Ayahs Tested: {summary['total_compared']}\n"
                                    f"Correct Recitations: {summary['correct_count']}\n"
                                    f"Major Mistakes: {summary['major_mistakes']}")

            # Reset UI
            self.is_test_active = False
            self.is_recording = False
            self.reset_ui()

            self.status_var.set("Test ended. Ready for new test.")

    def reset_ui(self):
        """Reset UI to initial state"""
        self.record_btn.config(text="🎤 Start Recording & Auto-Continue", state='disabled')
        self.start_test_btn.config(state='normal')
        self.end_test_btn.config(state='disabled')

        self.ayah_info_label.config(text="🎯 Start test to begin memorization recitation")
        self.hidden_text_label.config(text="❌ Ayah Text Hidden - Recite from Memory")
        self.recitation_text.delete(1.0, tk.END)
        self.details_text.delete(1.0, tk.END)
        self.score_label.config(text="Score: --%")
        self.feedback_label.config(text="Start your test to see feedback")
        self.progress_label.config(text="Progress: 0/0 ayahs")
        self.progress_bar['value'] = 0

    def update_ayah_display(self, ayah_info):
        """Update the current ayah display (position only - text hidden)"""
        self.ayah_info_label.config(text=f"🎯 Recite: {ayah_info['position']}")

        if ayah_info.get('is_last_ayah'):
            self.hidden_text_label.config(text="❌ Ayah Text Hidden - LAST AYAH! Recite from Memory")
        else:
            self.hidden_text_label.config(text="❌ Ayah Text Hidden - Recite from Memory")

    def toggle_recording(self):
        """Start or stop recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start recording recitation"""
        if not self.is_test_active:
            return

        self.is_recording = True
        self.record_btn.config(text="⏹️ Stop Recording", state='disabled')
        self.recitation_text.delete(1.0, tk.END)
        self.recitation_text.insert(1.0, "🎤 Recording... Recite the current ayah from memory!\n\n")
        self.recitation_text.insert(tk.END, "💡 Speak clearly in Arabic - system will auto-continue to next ayah")

        self.status_var.set("Recording... recite current ayah from memory!")

        # Start recording in thread
        threading.Thread(target=self.record_and_evaluate, daemon=True).start()

    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        self.record_btn.config(text="🎤 Start Recording & Auto-Continue")

    def record_and_evaluate(self):
        """Record audio, evaluate, and auto-advance"""
        try:
            print("🎯 Starting recording and auto-advance...")

            # Record and transcribe
            user_text = self.tester.voice_recorder.quick_record_and_transcribe(duration=15)

            # Update UI in main thread
            self.root.after(0, self.process_recitation_result, user_text)

        except Exception as e:
            error_msg = f"Recording error: {e}"
            print(f"❌ {error_msg}")
            self.root.after(0, lambda: self.recitation_text.insert(tk.END, f"\n\n❌ Error: {e}"))
        finally:
            self.root.after(0, self.stop_recording)

    def process_recitation_result(self, user_text):
        """Process the recitation result and auto-advance"""
        self.recitation_text.delete(1.0, tk.END)

        if user_text:
            self.recitation_text.insert(1.0, f"✅ Transcription successful!\n\nYour recitation:\n{user_text}")
            self.status_var.set("Transcription successful - analyzing...")

            if self.is_test_active:
                # Evaluate recitation and auto-advance
                result = self.tester.evaluate_and_advance(user_text)

                if 'error' not in result:
                    # Update display with results
                    self.update_results_display(result)
                    self.update_session_display()

                    # Check if test should auto-continue
                    if not result.get('test_complete') and result.get('next_ayah'):
                        # Auto-continue to next ayah
                        self.root.after(1000, self.auto_continue_to_next_ayah, result['next_ayah'])
                    elif result.get('test_complete'):
                        # Test complete
                        self.root.after(2000, self.end_hifz_test)
        else:
            self.recitation_text.insert(1.0, "❌ No speech detected or could not transcribe\n\n")
            self.recitation_text.insert(tk.END, "💡 Tips: Speak louder and clearer, use quiet environment")

            self.status_var.set("Transcription failed - try again")
            self.score_label.config(text="Score: --%", fg='black')
            self.feedback_label.config(text="Could not transcribe audio")

            # Re-enable recording for retry
            self.root.after(2000, lambda: self.record_btn.config(state='normal'))

    def auto_continue_to_next_ayah(self, next_ayah_info):
        """Automatically continue to next ayah"""
        if next_ayah_info and self.is_test_active:
            self.update_ayah_display(next_ayah_info)
            self.recitation_text.delete(1.0, tk.END)
            self.recitation_text.insert(1.0, f"➡️ Auto-advanced to: {next_ayah_info['position']}\n\n")
            self.recitation_text.insert(tk.END, "Click 'Start Recording' to continue or wait 3 seconds...")
            self.status_var.set(f"Ready for next ayah: {next_ayah_info['position']}")

            # Auto-start recording after 3 seconds
            self.root.after(3000, self.start_recording)

    def update_results_display(self, result):
        """Update results display with evaluation"""
        score = result['score']
        self.score_label.config(text=f"Score: {score}%")

        # Color code based on score
        if score >= 80:
            color = "green"
            feedback = "Excellent! Perfect memorization 🎉"
        elif score >= 70:
            color = "orange"
            feedback = "Good! Minor mistakes 👍"
        else:
            color = "red"
            feedback = "Needs practice - review this ayah 💪"

        self.score_label.config(fg=color)
        self.feedback_label.config(text=feedback)

        # Show detailed comparison (reveal correct text only in results)
        details = f"""Ayah: {result['surah']}:{result['ayah']}

Your Recitation: {result['user_text']}
Correct Text:    {result['correct_text']}

Similarity: {result['similarity']:.3f} ({score}%)
Status: {'✅ Correct' if result['is_correct'] else '❌ Needs Review'}
{'⚠️  Major mistakes detected' if result['is_major_mistake'] else '✨ Good recitation'}

{'➡️ Auto-advancing to next ayah...' if result.get('next_ayah') else '🎉 Test complete!'}"""

        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)

    def update_session_display(self):
        """Update session progress display"""
        summary = self.tester.get_session_summary()
        if summary:
            self.progress_label.config(
                text=f"Progress: {summary['total_compared']}/{summary['ayah_count']} ayahs"
            )
            self.progress_bar['value'] = summary['progress_percent']


def main():
    """Start the GUI application"""
    root = tk.Tk()

    # For testing without main.py
    from hifz_tester import HifzTester
    tester = HifzTester()

    app = HifzCompanionGUI(root, tester)
    root.mainloop()


if __name__ == "__main__":
    main()