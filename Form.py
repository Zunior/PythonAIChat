import os
from tkinter import *
from tkinter import ttk
import threading

import FileConfirmationDialog
import GPTAI.AiResponderInterface
import GPTAI.customgpt
import GPTAI.OpenAI
import FormUtil
import constants
from QueryTypeEnum import QueryType

os.environ['OPENAI_API_KEY'] = constants.API_KEY

class ChatApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Local Chat AI Interface")
        self.master.geometry("1000x600")

        self.chat_history = []
        self.query_type = StringVar(master, QueryType.LOCAL.value)
        self.gpt_type = StringVar(master, "1")

        self._create_widgets()

    def _create_widgets(self):
        """Creates and places all the Tkinter widgets for the UI."""
        # Labels
        self.title_label = Label(self.master, text="Local Chat", font=("Arial", 20))
        self.question_label = Label(self.master, text="Please state your question", font=("Arial", 10))
        self.answer_label = Label(self.master, text="Answer", font=("Arial", 10))
        self.error_label = Label(self.master, font=("Arial", 10), fg='#f00', wraplength=600, justify="left")
        self.blank_line = Label(self.master, text="\n", font=("Arial", 20)) # Use separate blank labels

        # Entries/Text Areas
        self.question_text = Text(self.master, font=("Arial", 10), height=5, width=50)
        self.answer_text = Text(self.master, height=20)
        self.answer_text.config(state=NORMAL) # Ensure it's modifiable by code initially

        # Radio Buttons for Query Type
        self.query_type_rb1 = Radiobutton(self.master, text="Local", variable=self.query_type, value=QueryType.LOCAL.value)
        self.query_type_rb2 = Radiobutton(self.master, text="Global", variable=self.query_type, value=QueryType.GLOBAL.value)
        self.query_type_rb3 = Radiobutton(self.master, text="Both", variable=self.query_type, value=QueryType.BOTH.value)

        # Radio Buttons for GPT Type
        self.gpt_type_rb1 = Radiobutton(self.master, text="OpenAI", variable=self.gpt_type, value="1")
        self.gpt_type_rb2 = Radiobutton(self.master, text="Custom", variable=self.gpt_type, value="2")

        # Spinner/Progress Bar (ttk.Progressbar)
        self.progress_bar = ttk.Progressbar(self.master, mode='indeterminate', length=200)

        # Buttons
        self.submit_button = Button(self.master, text="Ask", command=self._start_query_thread)
        self.upload_button = Button(self.master, text='Import data', command=lambda: FormUtil.upload_action(self.error_label))

        # --- Grid Layout (moved from top-level) ---
        self.title_label.grid(row=0, column=0, columnspan=2, sticky=W, padx=20, pady=10) # Added columnspan for better title centering
        self.query_type_rb1.grid(row=0, column=2, sticky=W)
        self.query_type_rb2.grid(row=0, column=3, sticky=W)
        self.query_type_rb3.grid(row=0, column=4, sticky=W)

        self.blank_line.grid(row=1, column=0) # Acts as a spacer
        self.gpt_type_rb1.grid(row=1, column=2, sticky=W)
        self.gpt_type_rb2.grid(row=1, column=3, sticky=W)

        self.question_label.grid(row=2, column=0, sticky=W, padx=20)
        self.question_text.grid(row=3, column=0, padx=20)
        self.submit_button.grid(row=3, column=1, sticky=W)
        self.upload_button.grid(row=3, column=2, sticky=W)

        # Position the progress bar near the submit button or status
        self.progress_bar.grid(row=3, column=3, columnspan=2, padx=10, sticky="ew") # Placed in grid, but not packed

        self.error_label.grid(row=4, column=0, columnspan=5, sticky=W, padx=20, pady=5) # Error label before answer
        self.answer_label.grid(row=5, column=0, sticky=W, padx=20)
        self.answer_text.grid(row=6, column=0, columnspan=5, padx=20, pady=5, sticky="nsew")

        # Configure grid row and column weights for resizing
        self.master.grid_rowconfigure(6, weight=1) # Make answer_text row expandable
        self.master.grid_columnconfigure(0, weight=1) # Make question/answer column expandable

    def _start_query_thread(self):
        """Initiates the query process, showing spinner and starting a new thread."""
        question_val = FormUtil.get_text_value(self.question_text)
        if not question_val:
            self.error_label.config(text="Please enter a question.")
            return

        # Clear previous error
        self.error_label.config(text="")

        # Disable UI elements and show spinner
        self.submit_button.config(state=DISABLED)
        self.upload_button.config(state=DISABLED)
        self.progress_bar.start(10) # Start the animation
        self.status_label.config(text="Asking AI, please wait...") # Update status label

        # Start the long-running task in a separate thread
        query_thread = threading.Thread(target=self._perform_query, args=(question_val,))
        query_thread.daemon = True # Allows the program to exit if main window closes
        query_thread.start()

    def _start_query_thread(self):
        """Initiates the query process, showing spinner and starting a new thread."""
        question_val = FormUtil.get_text_value(self.question_text)
        if not question_val:
            self.error_label.config(text="Please enter a question.")
            return

        # Clear previous error
        self.error_label.config(text="")

        # Disable UI elements and show spinner
        self.submit_button.config(state=DISABLED)
        self.upload_button.config(state=DISABLED)
        self.progress_bar.start(10) # Start the animation
        self.status_label.config(text="Asking AI, please wait...") # Update status label

        # Start the long-running task in a separate thread
        query_thread = threading.Thread(target=self._perform_query, args=(question_val,))
        query_thread.daemon = True # Allows the program to exit if main window closes
        query_thread.start()

    def _perform_query(self, question_val):
        """
        Performs the actual AI query in a separate thread.
        All GUI updates must be scheduled via self.master.after().
        """
        open_ai_instance = None
        current_query_type = QueryType(int(self.query_type.get()))
        current_gpt_type = self.gpt_type.get()
        answer = ""
        error_message = ""
        new_chat_history = []

        try:
            if current_gpt_type == "1":
                open_ai_instance = GPTAI.OpenAI.OpenAI()
            elif current_gpt_type == "2":
                open_ai_instance = GPTAI.customgpt.CustomGPT()
            else:
                raise ValueError("Invalid GPT type selected.")

            result_tuple = open_ai_instance.return_answer(current_query_type, question_val)
            answer = result_tuple[0]
            new_chat_history = result_tuple[1]

        except Exception as e:
            error_message = f"Error during query: {e}"
            print(error_message) # Print to console for debugging

        finally:
            # --- Schedule all GUI updates back on the main thread ---
            self.master.after(0, self.progress_bar.stop)
            # self.master.after(0, self.progress_bar.grid_forget) # If you want to hide it completely
            self.master.after(0, lambda: self.submit_button.config(state=NORMAL))
            self.master.after(0, lambda: self.upload_button.config(state=NORMAL))

            if error_message:
                self.master.after(0, lambda: self.error_label.config(text=error_message))
                self.master.after(0, lambda: self.status_label.config(text="Query failed."))
            else:
                self.master.after(0, lambda: self.answer_text.delete(1.0, FileConfirmationDialog.END))
                self.master.after(0, lambda: self.answer_text.insert(FileConfirmationDialog.END, answer))
                self.master.after(0, lambda: self.status_label.config(text="Query completed."))
                # Update chat history in the main thread
                self.master.after(0, lambda: setattr(self, 'chat_history', new_chat_history))

if __name__ == "__main__":
    root = Tk()
    app = ChatApp(root)
    root.mainloop()


##### FORM #####
# def get_values():
#     open_ai = None
#     answer_text.delete(1.0, FileConfirmationDialog.END)
#
#     match gpt_type.get():
#         case "1":
#             open_ai = GPTAI.OpenAI.OpenAI()
#         case "2":
#             open_ai = GPTAI.customgpt.CustomGPT()
#
#     try:
#         result = open_ai.return_answer(QueryType(int(query_type.get())), FormUtil.get_text_value(question_text))
#         chat_history = result[1]
#         answer_text.insert(FileConfirmationDialog.END, result[0])
#     except Exception as e:
#         error_label.configure(text=str(e))

# root = Tk()
#
# title = Label(root, text="Local chat", font=("Arial", 20))
#
# # labels
# question_label = Label(root, text="Please state your question", font=("Arial", 10))
# answer_label = Label(root, text="Answer", font=("Arial", 10))
# query_type_label = Label(root)
# error_label = Label(root, font=("Arial", 10), fg='#f00', wraplength=600, justify="left")
# blank_line = Label(root, text="\n", font=("Arial", 20))
#
# # entries
# question_text = Text(root, font=("Arial", 10), height=5, width=50)
# answer_text = Text(root, height=20)
# answer_text.config(state=NORMAL) # to be able to be deleted
#
# query_type_rb1 = Radiobutton(root, text="Local", variable=query_type, value=QueryType.LOCAL.value)
# query_type_rb2 = Radiobutton(root, text="Global", variable=query_type, value=QueryType.GLOBAL.value)
# query_type_rb3 = Radiobutton(root, text="Both", variable=query_type, value=QueryType.BOTH.value)
#
# gpt_type_rb1 = Radiobutton(root, text="OpenAI", variable=gpt_type, value=1)
# gpt_type_rb2 = Radiobutton(root, text="Custom", variable=gpt_type, value=2)
#
# # submit button
# submit_button = Button(root, text="Ask", command=get_values)
#
# # upload button
# upload_button = Button(root, text='Import data', command= lambda: FormUtil.upload_action(error_label))
#
# # grid
# title.grid(row=0, column=0)
# query_type_rb1.grid(row=0, column=2, sticky=W)
# query_type_rb2.grid(row=0, column=3, sticky=W)
# query_type_rb3.grid(row=0, column=4, sticky=W)
# blank_line.grid(row=1, column=0)
# gpt_type_rb1.grid(row=1, column=2, sticky=W)
# gpt_type_rb2.grid(row=1, column=3, sticky=W)
# question_label.grid(row=2, column=0)
# question_text.grid(row=3, column=0, padx = 20)
# submit_button.grid(row=3, column=1, sticky=W)
# upload_button.grid(row=3, column=2)
# blank_line.grid(row=4, column=0)
# error_label.grid(row=5, column=0, columnspan=4, sticky=W, padx = 20)
# answer_label.grid(row=6, column=0)
# answer_text.grid(row=7, column=0, columnspan=2, padx = 20)
#
# root.mainloop()
