from IPython.display import display, HTML, clear_output
from datetime import datetime
import json
import os
from typing import List, Dict, Optional, Union

class LabProgress:
    """
    A comprehensive lab progress tracker for Jupyter notebooks.
    Tracks step completion, timing, scores, and provides persistence.
    """
    
    def __init__(self, steps: Union[List[str], Dict[str, dict]], lab_name: str = "Lab", 
                 persist: bool = False, persist_file: str = None):
        """
        Initialize the lab progress tracker.
        
        Args:
            steps: List of step names or dict with step details
            lab_name: Name of the lab for display
            persist: Whether to save progress to file
            persist_file: Custom file path for persistence
        """
        self.lab_name = lab_name
        self.persist = persist
        self.persist_file = persist_file or f".{lab_name.lower().replace(' ', '_')}_progress.json"
        
        # Initialize steps
        if isinstance(steps, list):
            self.steps = {step: {
                'completed': False, 
                'timestamp': None,
                'attempts': 0,
                'score': None,
                'notes': ''
            } for step in steps}
        else:
            self.steps = steps
            
        # Load saved progress if exists
        if persist and os.path.exists(self.persist_file):
            self._load_progress()
            
        self.start_time = datetime.now()
        self._display_handle = None
        self.display_progress()
    
    def mark_done(self, step: str, score: Optional[float] = None, notes: str = ''):
        """Mark a step as completed with optional score and notes."""
        if step in self.steps:
            self.steps[step]['completed'] = True
            self.steps[step]['timestamp'] = datetime.now().isoformat()
            self.steps[step]['score'] = score
            if notes:
                self.steps[step]['notes'] = notes
            
            if self.persist:
                self._save_progress()
                
            self.display_progress()
        else:
            display(HTML(f"<div style='color: red;'>⚠️ Unknown step: {step}</div>"))
    
    def mark_partial(self, step: str, progress: float, notes: str = ''):
        """Mark partial progress on a step (0.0 to 1.0)."""
        if step in self.steps:
            self.steps[step]['progress'] = max(0, min(1, progress))
            if notes:
                self.steps[step]['notes'] = notes
            
            if self.persist:
                self._save_progress()
                
            self.display_progress()
    
    def increment_attempts(self, step: str):
        """Increment the attempt counter for a step."""
        if step in self.steps:
            self.steps[step]['attempts'] += 1
            if self.persist:
                self._save_progress()
    
    def reset_step(self, step: str):
        """Reset a specific step."""
        if step in self.steps:
            self.steps[step] = {
                'completed': False,
                'timestamp': None,
                'attempts': 0,
                'score': None,
                'notes': ''
            }
            if self.persist:
                self._save_progress()
            self.display_progress()
    
    def reset_all(self):
        """Reset all progress."""
        for step in self.steps:
            self.reset_step(step)
    
    def get_completion_rate(self) -> float:
        """Get overall completion percentage."""
        completed = sum(1 for s in self.steps.values() if s['completed'])
        return (completed / len(self.steps)) * 100 if self.steps else 0
    
    def get_average_score(self) -> Optional[float]:
        """Get average score across completed steps."""
        scores = [s['score'] for s in self.steps.values() 
                 if s['completed'] and s['score'] is not None]
        return sum(scores) / len(scores) if scores else None
    
    def display_progress(self, detailed: bool = False):
        """Display the current progress with visual indicators."""
        completion_rate = self.get_completion_rate()
        avg_score = self.get_average_score()
        
        # Build HTML
        html = f"""
        <div style='background-color: #f5f5f5; padding: 20px; border-radius: 10px; margin: 10px 0;'>
            <h3 style='color: #333; margin-bottom: 15px;'>{self.lab_name} Progress</h3>
            
            <!-- Progress Bar -->
            <div style='background-color: #e0e0e0; border-radius: 20px; height: 30px; margin-bottom: 20px;'>
                <div style='background-color: #4CAF50; height: 100%; border-radius: 20px; width: {completion_rate}%; 
                            transition: width 0.5s ease; display: flex; align-items: center; justify-content: center;'>
                    <span style='color: white; font-weight: bold;'>{completion_rate:.1f}%</span>
                </div>
            </div>
        """
        
        if avg_score is not None:
            html += f"<p style='color: #666;'>Average Score: {avg_score:.1f}/100</p>"
        
        # Steps list
        html += "<ul style='list-style: none; padding: 0;'>"
        
        for step, info in self.steps.items():
            # Determine icon and color
            if info['completed']:
                icon = "✅"
                color = "#4CAF50"
                status = "Completed"
            elif info.get('progress', 0) > 0:
                icon = "🔄"
                color = "#FF9800"
                status = f"{info['progress']*100:.0f}% Complete"
            else:
                icon = "⏳"
                color = "#9E9E9E"
                status = "Pending"
            
            html += f"""
            <li style='margin: 10px 0; padding: 10px; background-color: white; 
                       border-left: 4px solid {color}; border-radius: 5px;'>
                <span style='font-size: 20px; margin-right: 10px;'>{icon}</span>
                <strong>{step}</strong> - <span style='color: {color};'>{status}</span>
            """
            
            if detailed:
                if info['timestamp']:
                    html += f"<br><small style='color: #666;'>Completed: {info['timestamp']}</small>"
                if info['attempts'] > 0:
                    html += f"<br><small style='color: #666;'>Attempts: {info['attempts']}</small>"
                if info['score'] is not None:
                    html += f"<br><small style='color: #666;'>Score: {info['score']}/100</small>"
                if info['notes']:
                    html += f"<br><small style='color: #666;'>Notes: {info['notes']}</small>"
            
            html += "</li>"
        
        html += "</ul>"
        
        # Summary
        elapsed = datetime.now() - self.start_time
        html += f"""
        <div style='margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;'>
            <small style='color: #666;'>
                Time Elapsed: {str(elapsed).split('.')[0]} | 
                Steps Completed: {sum(1 for s in self.steps.values() if s['completed'])}/{len(self.steps)}
            </small>
        </div>
        </div>
        """
        
        # Use clear_output to update in place
        if self._display_handle:
            clear_output(wait=True)
        
        self._display_handle = display(HTML(html))
    
    def _save_progress(self):
        """Save progress to file."""
        data = {
            'lab_name': self.lab_name,
            'steps': self.steps,
            'start_time': self.start_time.isoformat()
        }
        with open(self.persist_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_progress(self):
        """Load progress from file."""
        try:
            with open(self.persist_file, 'r') as f:
                data = json.load(f)
                self.steps = data['steps']
                self.start_time = datetime.fromisoformat(data['start_time'])
        except Exception as e:
            print(f"Could not load saved progress: {e}")
    
    def export_report(self) -> str:
        """Export a text report of the progress."""
        report = f"Lab Progress Report: {self.lab_name}\n"
        report += "=" * 50 + "\n\n"
        report += f"Completion Rate: {self.get_completion_rate():.1f}%\n"
        
        avg_score = self.get_average_score()
        if avg_score:
            report += f"Average Score: {avg_score:.1f}/100\n"
        
        report += f"\nSteps:\n"
        for step, info in self.steps.items():
            status = "✅ Completed" if info['completed'] else "⏳ Pending"
            report += f"- {step}: {status}\n"
            if info['score'] is not None:
                report += f"  Score: {info['score']}/100\n"
            if info['attempts'] > 0:
                report += f"  Attempts: {info['attempts']}\n"
        
        return report