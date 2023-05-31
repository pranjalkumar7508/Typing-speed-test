from tkinter import *
from lorem_text import lorem    
import ctypes
import random
from datetime import datetime

STARTING_TIME = 60
FONT = ("Ariel", "16", "bold")
random_word = None
timer = None
total_characters = 0
unique_words = []
test_started = False

# ----------------------------------------- FUNCTIONS -----------------------------------------------------


# start test by generating a unique list of words, starting the timer, and loading a new word from the unique list
def start_test():
    global unique_words
    word_list = lorem.words(200).lower().split(" ")  # list with lower case words
    unique_words = []
    [unique_words.append(word) for word in word_list if word not in unique_words]  # list with no duplicates
    start_timer(STARTING_TIME)
    new_word(unique_words)



def start_timer(seconds):
    global timer, total_characters, test_started
    timer_input.config(state="normal")
    timer_input.delete(0, END)
    timer_input.insert(0, seconds)
    cpm_input.config(state="normal")
    wpm_input.config(state="normal")
    word_input.config(state="normal")
    calculate_score(total_characters, STARTING_TIME - seconds)
    if seconds > 0:
        timer = window.after(1000, start_timer, seconds - 1)
    else:
        test_started = False
        window.after_cancel(timer)
        current_word.config(text="Test is over!\nClick the input bar to try again.")
        timer_input.config(state="disabled")
        cpm_input.config(state="disabled")
        wpm_input.config(state="disabled")
        word_input.config(state="disabled")
        final_scores = calculate_score(total_characters, STARTING_TIME - seconds)
        update_recent_score(final_scores)
        read_recent_score()


# load a new word from the word list, then remove it from the word list
def new_word(words):
    global random_word
    random_word = random.choice(words)
    current_word.config(text=f"{random_word}", font=FONT)
    words.remove(random_word)


# clear input bar. start timer, reset total characters typed to 0, load a new word if test hasn't been started yet
def click_input_bar(*args):
    global total_characters, test_started
    word_input.delete(0, END)
    if not test_started:    # if test hasn't been started (equal to False), start it
        test_started = True
        total_characters = 0
        start_test()


# call this function to clear word_input when user clicks outside the entry box
def leave_input_bar(*args):
    word_input.delete(0, END)
    word_input.insert(0, 'type words here')
    window.focus()


# when user inputs word, add the number of correct characters to the total amount and load a new word
def enter_word(*args):
    global random_word, total_characters, unique_words
    entered_word = word_input.get().strip()
    word_input.delete(0, END)
    print(entered_word)
    print(random_word)
    if entered_word == random_word:
        total_characters += (len(entered_word) + 1)  # plus 1 to account for space bar
    else:
        correct_chars = [letter_tuple for letter_tuple in enumerate(entered_word) if letter_tuple in
                         enumerate(random_word)]    # ensure letter and index are the same to be considered correct
        print(correct_chars)
        total_characters += (len(correct_chars) + 1)
        print(total_characters)
    new_word(unique_words)


# calculate the current cpm and wpm from the current character count and time elapsed
def calculate_score(num_characters, time_elapsed):
    cpm = 0
    wpm = 0
    cpm_input.delete(0, END)
    wpm_input.delete(0, END)
    try:
        cpm = (num_characters / time_elapsed) * 60
        wpm = cpm / 5
    except ZeroDivisionError:
        wpm_input.insert(0, 0)
        cpm_input.insert(0, 0)
    else:
        wpm_input.insert(0, round(wpm, 3))
        cpm_input.insert(0, round(cpm, 3))
    finally:
        return [cpm, wpm]


# stop timer, reset timer, score, and word inputs to default settings
def restart():
    global test_started
    try:
        window.after_cancel(timer)
    except ValueError:
        pass
    test_started = False
    timer_input.delete(0, END)
    timer_input.insert(0, STARTING_TIME)
    timer_input.config(state="disabled")
    cpm_input.config(state="disabled")
    wpm_input.config(state="disabled")
    word_input.config(state="normal")
    current_word.config(text="Hi! Click the bar below me to get started!", font=FONT)


# read newest score from csv file and display it
def read_recent_score():
    try:
        with open("recent_score.csv", mode="r") as data:
            recent_scores = data.read().split(",")
            cpm = float(recent_scores[0])
            wpm = float(recent_scores[1])
            date = recent_scores[2]
            return f"Most recent score: {round(cpm, 1)} CPM, {round(wpm, 1)} WPM on {date}."
    except FileNotFoundError:
        return "No recent score listed."


# write new score in a csv file
def update_recent_score(scores):
    current_time = datetime.now().strftime("%b %d %Y at %I:%M %p")
    with open("recent_score.csv", mode="w") as file:
        file.write(f"{scores[0]},{scores[1]},{current_time}")   # cpm, wpm, current time and date
    recent_score_text.config(text=read_recent_score())


# close window
def close_window():
    window.destroy()

# ----------------------------------------- GUI -----------------------------------------------------
# https://colorhunt.co/palette/fcd8d4fdf6f0f8e2cff5c6aa
ctypes.windll.shcore.SetProcessDpiAwareness(1)
window = Tk()
window.title("Typing Speed Test")
window.config(padx=50, pady=50, bg="#FDF6F0")

# logo
logo = PhotoImage(file="i/keypad.png")
canvas = Canvas(window, width=256, height=256, bg="#FDF6F0", highlightthickness=0)
canvas.create_image(128, 128, image=logo)
canvas.grid(column=1, row=0, columnspan=5)

# instruction message bar
instruction_label = Label(window, text="What's your typing speed in WPM and CPM?\nDo the one-minute typing test!\n"
                                       "Press enter or the space bar after typing each word.",
                          font="Ariel", bg="#F8E2CF", fg="#62867F")
instruction_label.grid(column=1, row=1, columnspan=5, pady=(0, 15))

# cpm
cpm_label = Label(text="Corrected CPM", font="Ariel", bg="#F8E2CF", fg="#62867F")
cpm_label.grid(column=0, row=2, sticky="E")
cpm_input = Entry(width=6)
cpm_input.insert(0, "?")
cpm_input.grid(column=1, row=2, sticky="W", padx=(5, 0))
cpm_input.config(state="disabled")

# wpm
wpm_label = Label(text="WPM", font="Ariel", bg="#F8E2CF", fg="#62867F")
wpm_label.grid(column=2, row=2, sticky="E")
wpm_input = Entry(width=6)
wpm_input.insert(0, "?")
wpm_input.grid(column=3, row=2, sticky="W", padx=(5, 0))
wpm_input.config(state="disabled")

# timer
timer_label = Label(text="Time Left", font="Ariel", bg="#F8E2CF", fg="#62867F")
timer_label.grid(column=4, row=2, sticky="E")
timer_input = Entry(width=6)
timer_input.insert(0, STARTING_TIME)
timer_input.grid(column=5, row=2, sticky="W", padx=(5, 0))
timer_input.config(state="disabled")

# restart button
restart_btn = Button(window, text="Reset", command=restart, font="Ariel", bg="#FCD8D4", fg="#62867F", height=1,
                     relief=GROOVE)
restart_btn.grid(column=6, row=2, sticky="W", padx=(15, 0))

# label for current word display
words_label = Label(text="Type the current word below", font="Ariel", bg="#F8E2CF", fg="#62867F")
words_label.grid(column=1, row=3, sticky="W", pady=(15, 0))

# display for current word
current_word = Label(text=f"Hi! Click the bar below me to get started!", font=FONT, bg="#F8E2CF",
                     fg="#62867F", height=5, width=40)
current_word.grid(column=1, row=4, columnspan=5, sticky="W", pady=(5, 0))
current_word.config(state="disabled")

# input for user to type current word
word_input = Entry(width=76)
word_input.insert(0, "type word here")
word_input.grid(column=1, row=5, columnspan=5, sticky="W")
word_input.config(state="normal")
word_input.bind("<Button-1>", click_input_bar)
word_input.bind("<Leave>", leave_input_bar)
word_input.bind("<space>", enter_word)
word_input.bind("<Return>", enter_word)

# newest score
recent_score_text = Label(text=read_recent_score(), font="Ariel", bg="#F8E2CF", fg="#62867F")
recent_score_text.grid(column=0, row=6, columnspan=5, pady=(25, 0))

# exit button
exit_btn = Button(window, text="Exit", command=close_window, font="Ariel", bg="#FCD8D4", fg="#62867F", height=2,
                  width=5, relief=GROOVE)
exit_btn.grid(column=6, row=6, sticky="W", padx=(15, 0), pady=(25, 0))

window.mainloop()