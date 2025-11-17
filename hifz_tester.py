"""
Hifz Testing Engine - Auto-advance with hidden ayahs
"""

from quran_data import load_dataset, get_ayah_text, normalize_arabic, compare_texts
from voice_recognition import VoiceRecorder
import time


class HifzTester:
    def __init__(self):
        self.quran_data = load_dataset()
        self.voice_recorder = VoiceRecorder()
        self.current_session = None
        self.current_surah = None
        self.current_ayah = None
        self.is_test_running = False

    def start_hifz_test(self, surah_number, start_ayah=1, ayah_count=5):
        """Start a new hifz test session"""
        self.current_surah = surah_number
        self.current_ayah = start_ayah
        self.is_test_running = True

        self.current_session = {
            'surah': surah_number,
            'start_ayah': start_ayah,
            'current_ayah': start_ayah,
            'ayah_count': ayah_count,
            'recitations': [],
            'score': 0,
            'total_compared': 0,
            'test_start_time': time.time()
        }

        return self.get_current_ayah_info()

    def get_current_ayah_info(self):
        """Get current ayah info WITHOUT revealing the text"""
        if not self.current_session:
            return None

        try:
            ayah_text = get_ayah_text(self.quran_data, self.current_surah, self.current_ayah)
            return {
                'surah': self.current_surah,
                'ayah': self.current_ayah,
                'position': f"Surah {self.current_surah}, Ayah {self.current_ayah}",
                'is_last_ayah': self.current_ayah >= (
                            self.current_session['start_ayah'] + self.current_session['ayah_count'] - 1)
            }
        except Exception as e:
            print(f"Error getting ayah: {e}")
            return None

    def get_correct_text_for_comparison(self):
        """Get the correct text for comparison only"""
        try:
            return get_ayah_text(self.quran_data, self.current_surah, self.current_ayah)
        except:
            return None

    def auto_advance_ayah(self):
        """Automatically move to next ayah"""
        if not self.current_session:
            return None

        self.current_ayah += 1

        # Check if we've reached the end of test
        if self.current_ayah >= (self.current_session['start_ayah'] + self.current_session['ayah_count']):
            self.is_test_running = False
            return None

        try:
            # Check if next ayah exists
            get_ayah_text(self.quran_data, self.current_surah, self.current_ayah)
            self.current_session['current_ayah'] = self.current_ayah
            return self.get_current_ayah_info()
        except:
            # End of surah
            self.is_test_running = False
            return None

    def evaluate_and_advance(self, user_recitation):
        """Evaluate recitation and auto-advance to next ayah"""
        if not self.current_session or not self.is_test_running:
            return {'error': 'No active test session'}

        correct_text = self.get_correct_text_for_comparison()
        if not correct_text:
            return {'error': 'Cannot get correct text'}

        # Compare texts
        comparison_result = compare_texts(user_recitation, correct_text)

        # Calculate score
        score = comparison_result['match_percent']

        # Store result
        result = {
            'surah': self.current_surah,
            'ayah': self.current_ayah,
            'user_text': user_recitation,
            'correct_text': correct_text,  # Store for results display
            'similarity': comparison_result['similarity'],
            'score': score,
            'is_correct': score >= 70,
            'is_major_mistake': score < 60,
            'normalized_comparison': {
                'user': comparison_result['normalized_user'],
                'correct': comparison_result['normalized_correct']
            }
        }

        # Update session
        self.current_session['recitations'].append(result)
        self.current_session['total_compared'] += 1
        if self.current_session['total_compared'] > 0:
            self.current_session['score'] = (
                    sum(r['score'] for r in self.current_session['recitations']) /
                    self.current_session['total_compared']
            )

        # Auto-advance to next ayah
        next_ayah_info = self.auto_advance_ayah()
        result['next_ayah'] = next_ayah_info
        result['test_complete'] = next_ayah_info is None

        return result

    def get_session_summary(self):
        """Get summary of current test session"""
        if not self.current_session:
            return None

        total = self.current_session['total_compared']
        correct = sum(1 for r in self.current_session['recitations'] if r['is_correct'])
        major_mistakes = sum(1 for r in self.current_session['recitations'] if r['is_major_mistake'])

        progress = min(100, (total / self.current_session['ayah_count']) * 100) if self.current_session[
                                                                                       'ayah_count'] > 0 else 0

        return {
            'surah': self.current_session['surah'],
            'start_ayah': self.current_session['start_ayah'],
            'current_ayah': self.current_session['current_ayah'],
            'total_compared': total,
            'ayah_count': self.current_session['ayah_count'],
            'correct_count': correct,
            'accuracy': self.current_session['score'],
            'major_mistakes': major_mistakes,
            'progress_percent': progress,
            'is_test_complete': not self.is_test_running or progress >= 100
        }

    def end_session(self):
        """End current test session and return final results"""
        summary = self.get_session_summary()
        self.is_test_running = False
        self.current_session = None
        self.current_surah = None
        self.current_ayah = None
        return summary