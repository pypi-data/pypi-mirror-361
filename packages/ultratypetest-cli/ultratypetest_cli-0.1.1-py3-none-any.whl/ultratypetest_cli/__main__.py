import curses
from curses import wrapper
import textwrap
import json
import sys

import time
import random
import csv
import os
from datetime import datetime
from typing import List
import pathlib

def get_data_file_path(filename: str) -> pathlib.Path:
    """
    Get the absolute path to a data file, works for both normal
    execution and a PyInstaller bundled application.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = pathlib.Path(sys._MEIPASS)
    else:
        base_path = pathlib.Path(__file__).parent.resolve()
    
    return base_path / filename

TEXTS_FILE = get_data_file_path("texts.txt")
HISTORY_FILE = "history.csv"
KEY_STATS_FILE = "key_stats.json"

def load_text() -> str:
    """Loads a random line from the texts file."""
    try:
        with open(TEXTS_FILE, "r") as f:
            lines = f.readlines()
            if not lines:
                return "Hello world. This is the default text."
            return random.choice(lines).strip()
    except FileNotFoundError:
        return "The texts.txt file was not found. Please create it."

def save_result(wpm: float, accuracy: float, duration: float):
    """Saves the test result to the history CSV file."""
    file_exists = os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "wpm", "accuracy", "duration_seconds"])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, f"{wpm:.2f}", f"{accuracy:.2f}", f"{duration:.2f}"])

def load_key_stats() -> dict:
    """Loads key statistics from a JSON file."""
    try:
        with open(KEY_STATS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_key_stats(stats: dict):
    """Saves key statistics to a JSON file."""
    with open(KEY_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def display_history(stdscr):
    """Displays past results from the history file."""
    stdscr.clear()
    try:
        with open(HISTORY_FILE, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            
            stdscr.addstr(0, 0, "--- Typing History ---")
            stdscr.addstr(2, 0, f"{header[0]:<22}{header[1]:<10}{header[2]:<15}{header[3]:<20}")
            stdscr.addstr(3, 0, "-" * 67)

            y = 4
            for row in reader:
                if y < curses.LINES - 2:
                    timestamp, wpm, accuracy, duration = row
                    stdscr.addstr(y, 0, f"{timestamp:<22}{wpm:<10}{accuracy:<15}{duration:<20}")
                    y += 1
    except (FileNotFoundError, StopIteration):
        stdscr.addstr(1, 0, "No history found. Complete a test to start your history.")

    stdscr.addstr(curses.LINES - 2, 0, "Press any key to return to the menu...")
    stdscr.getkey()

def display_stats(stdscr):
    """Calculates and displays performance statistics."""
    stdscr.clear()
    stdscr.addstr(0, 0, "--- Your Statistics ---")
    
    try:
        with open(HISTORY_FILE, "r") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            if not data:
                raise StopIteration

            wpms = [float(row['wpm']) for row in data]
            accuracies = [float(row['accuracy']) for row in data]

            best_wpm = max(wpms)
            avg_wpm = sum(wpms) / len(wpms)
            avg_accuracy = sum(accuracies) / len(accuracies)
            total_tests = len(data)

            stdscr.addstr(2, 2, f"Best WPM: {best_wpm:.2f}")
            stdscr.addstr(3, 2, f"Average WPM: {avg_wpm:.2f}")
            stdscr.addstr(4, 2, f"Average Accuracy: {avg_accuracy:.2f}%")
            stdscr.addstr(5, 2, f"Total Tests Taken: {total_tests}")

    except (FileNotFoundError, StopIteration):
        stdscr.addstr(2, 2, "No data available to calculate stats.")
    except (ValueError, KeyError):
        stdscr.addstr(2, 2, "History file is corrupted or has an invalid format.")

    stdscr.addstr(curses.LINES - 2, 0, "Press any key to return to the menu...")
    stdscr.getkey()

def display_test_ui(stdscr, target: str, current: List[str], wpm: float = 0.0):
    """
    Displays the main UI for the typing test.
    Handles word wrapping and uses an underscore cursor for better readability.
    """
    h, w = stdscr.getmaxyx()
    
    stdscr.addstr(1, 2, f"WPM: {wpm:.2f}")
    stdscr.addstr(1, w - 20, "Press ESC to exit test")
    
    margin = 2
    wrapped_target = textwrap.wrap(target, w - margin * 2)
    if not wrapped_target:
        return

    char_index_global = 0
    for line_num, line in enumerate(wrapped_target):
        line_y = h // 2 - len(wrapped_target) // 2 + line_num
        line_x = margin

        if line_y >= h - 1:
            break

        for i, char in enumerate(line):
            if char_index_global >= len(target):
                break
            
            char_to_display = char
            color = curses.color_pair(4)

            if char_index_global < len(current):
                if current[char_index_global] == target[char_index_global]:
                    color = curses.color_pair(1)
                else:
                    color = curses.color_pair(2)
                    if target[char_index_global] == ' ':
                        char_to_display = '_'
            
            if line_x + i < w - 1:
                stdscr.addstr(line_y, line_x + i, char_to_display, color)
            
            char_index_global += 1

        if line_num < len(wrapped_target) - 1:
            char_index_global += 1

    cursor_char_index = len(current)
    
    if cursor_char_index < len(target):
        cursor_y, cursor_x = h // 2 - len(wrapped_target) // 2, margin
        temp_index = cursor_char_index
        for line_num, line in enumerate(wrapped_target):
            line_len_with_space = len(line) + 1
            if temp_index < line_len_with_space or line_num == len(wrapped_target) - 1:
                cursor_y += line_num
                cursor_x += temp_index
                break
            temp_index -= line_len_with_space
            
        if cursor_y < h - 1 and cursor_x < w - 1:
            char_at_cursor = target[cursor_char_index]
            stdscr.addstr(cursor_y, cursor_x, char_at_cursor,
                          curses.color_pair(4) | curses.A_UNDERLINE)


def start_test(stdscr):
    """Main function to run the typing test and capture key statistics."""
    target_text = load_text()
    current_text: List[str] = []
    wpm = 0.0
    start_time = None
    need_to_save=True
    
    key_stats = load_key_stats()
    
    curses.curs_set(0)
    try:
        stdscr.nodelay(True)
        while True:
            if len(current_text) == len(target_text):
                break

            if start_time is not None:
                duration = max(time.time() - start_time, 1)
                wpm = (len(current_text) / 5) / (duration / 60)
            
            stdscr.clear()
            display_test_ui(stdscr, target_text, current_text, wpm)
            stdscr.refresh()

            try:
                key = stdscr.getkey()
            except curses.error:
                continue

            if start_time is None and len(key) == 1:
                start_time = time.time()
            
            if key == "\x1b":
                need_to_save = False
                return
            elif key in ("KEY_BACKSPACE", '\b', "\x7f"):
                if len(current_text) > 0:
                    current_text.pop()
            elif len(key) == 1 and len(current_text) < len(target_text):
                target_char_index = len(current_text)
                target_char = target_text[target_char_index].lower()

                if target_char.isalnum() or target_char in ".,;'[]-=<>?/:\"{}|\\`~!@#$%^&*()_+":
                    # Initialize stat entry if it doesn't exist
                    key_stats.setdefault(target_char, {"correct": 0, "incorrect": 0})
                    
                    if key.lower() == target_char:
                        key_stats[target_char]["correct"] += 1
                    else:
                        key_stats[target_char]["incorrect"] += 1

                current_text.append(key)
    
    finally:
        stdscr.nodelay(False)

    if start_time is None:
        return

    if need_to_save:
        save_key_stats(key_stats)

    end_time = time.time()
    final_duration = end_time - start_time
    final_wpm = (len(target_text) / 5) / (final_duration / 60) if final_duration > 0 else 0
    
    correct_chars = sum(1 for i, char in enumerate(current_text) if char == target_text[i])
    accuracy = (correct_chars / len(target_text)) * 100 if len(target_text) > 0 else 0

    if need_to_save:
        save_result(final_wpm, accuracy, final_duration)

    stdscr.clear()
    stdscr.addstr(1, 0, "--- Test Complete! ---")
    stdscr.addstr(3, 0, f"Words Per Minute (WPM): {final_wpm:.2f}")
    stdscr.addstr(4, 0, f"Accuracy: {accuracy:.2f}%")
    stdscr.addstr(5, 0, f"Time Taken: {final_duration:.2f}s")
    stdscr.addstr(7, 0, "Press any key to return to the menu...")
    stdscr.getkey()


def display_menu(stdscr, selected_row_idx):
    """Displays the main menu."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    title = "Welcome to Typing test"
    stdscr.addstr(h // 2 - 5, w // 2 - len(title) // 2, title)

    menu = ["Start Test", "View History", "View Stats", "Quit"]
    for idx, row in enumerate(menu):
        x = w // 2 - len(row) // 2
        y = h // 2 - 2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(y, x, f" > {row} < ")
            stdscr.attroff(curses.color_pair(3))
        else:
            stdscr.addstr(y, x, row)
            
    stdscr.refresh()

def display_key_stats(stdscr):
    """Displays character accuracy in a keyboard layout."""
    stdscr.clear()
    stats = load_key_stats()

    KEYBOARD_LAYOUT = [
        "` 1 2 3 4 5 6 7 8 9 0 - =",
        " q w e r t y u i o p [ ] \\",
        " a s d f g h j k l ; '",
        " z x c v b n m , . /"
    ]
    
    h, w = stdscr.getmaxyx()
    start_y = h // 2 - len(KEYBOARD_LAYOUT) * 2

    stdscr.addstr(start_y - 2, w // 2 - 12, "--- Key Accuracy Stats ---")

    for row_idx, row_str in enumerate(KEYBOARD_LAYOUT):
        keys = row_str.split(' ')
        # Center the row horizontally
        row_width = sum(len(key) + 3 for key in keys)
        start_x = w // 2 - row_width // 2

        for key in keys:
            if not key:
                start_x += 1
                continue
            
            data = stats.get(key, {"correct": 0, "incorrect": 0})
            correct = data["correct"]
            incorrect = data["incorrect"]
            total = correct + incorrect
            
            accuracy = 0
            if total > 0:
                accuracy = (correct / total) * 100

            color = curses.color_pair(4)
            if total > 0:
                if accuracy >= 95:
                    color = curses.color_pair(1)
                elif accuracy >= 85:
                    color = curses.color_pair(6)
                else:
                    color = curses.color_pair(2)

            key_y = start_y + row_idx * 3
            
            stdscr.addstr(key_y, start_x, f" {key} ", color | curses.A_REVERSE)
            stdscr.addstr(key_y + 1, start_x, f"{accuracy:^3.0f}%", color)
            
            start_x += len(key) + 3

    stdscr.addstr(h - 2, 0, "Press any key to return to the menu...")
    stdscr.getkey()

def main(stdscr):
    """The main function to orchestrate the application."""
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    current_row_idx = 0
    menu = ["Start Test", "View History", "View Stats", "View Key Stats", "Quit"]

    def display_menu(stdscr, selected_row_idx):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "Welcome to Ultra Type Test"
        stdscr.addstr(h // 2 - 6, w // 2 - len(title) // 2, title)
        for idx, row in enumerate(menu):
            x = w // 2 - len(row) // 2
            y = h // 2 - 3 + idx
            if idx == selected_row_idx:
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(y, x, f" > {row} < ")
                stdscr.attroff(curses.color_pair(3))
            else:
                stdscr.addstr(y, x, row)
        stdscr.refresh()

    while True:
        display_menu(stdscr, current_row_idx)
        key = stdscr.getkey()

        if key == "KEY_UP" and current_row_idx > 0:
            current_row_idx -= 1
        elif key == "KEY_DOWN" and current_row_idx < len(menu) - 1:
            current_row_idx += 1
        elif key == '\n' or key == "KEY_ENTER":
            if current_row_idx == 0:
                start_test(stdscr)
            elif current_row_idx == 1:
                display_history(stdscr)
            elif current_row_idx == 2:
                display_stats(stdscr)
            elif current_row_idx == 3:
                display_key_stats(stdscr)
            elif current_row_idx == 4:
                break
    
if __name__ == "__main__":
    wrapper(main)