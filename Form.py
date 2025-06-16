import os
from tkinter import *

import FileConfirmationDialog
import GPTAI.AiResponderInterface
import GPTAI.customgpt
import GPTAI.OpenAI
import FormUtil
import constants
from QueryTypeEnum import QueryType

os.environ['OPENAI_API_KEY'] = constants.API_KEY

chat_history = []

##### FORM #####
def get_values():
    open_ai = None
    answer_text.delete(1.0, FileConfirmationDialog.END)

    match gpt_type.get():
        case "1":
            open_ai = GPTAI.OpenAI.OpenAI()
        case "2":
            open_ai = GPTAI.customgpt.CustomGPT()

    try:
        result = open_ai.return_answer(QueryType(int(query_type.get())), FormUtil.get_text_value(question_text))
        chat_history = result[1]
        answer_text.insert(FileConfirmationDialog.END, result[0])
    except Exception as e:
        error_label.configure(text=str(e))

root = Tk()
root.geometry("1000x600")

# variables
query_type = StringVar(root, QueryType.LOCAL.value)
gpt_type = StringVar(root, 1)

title = Label(root, text="Local chat", font=("Arial", 20))

# labels
question_label = Label(root, text="Please state your question", font=("Arial", 10))
answer_label = Label(root, text="Answer", font=("Arial", 10))
query_type_label = Label(root)
error_label = Label(root, font=("Arial", 10), fg='#f00', wraplength=600, justify="left")
blank_line = Label(root, text="\n", font=("Arial", 20))

# entries
question_text = Text(root, font=("Arial", 10), height=5, width=50)
answer_text = Text(root, height=20)
answer_text.config(state=NORMAL) # to be able to be deleted

query_type_rb1 = Radiobutton(root, text="Local", variable=query_type, value=QueryType.LOCAL.value)
query_type_rb2 = Radiobutton(root, text="Global", variable=query_type, value=QueryType.GLOBAL.value)
query_type_rb3 = Radiobutton(root, text="Both", variable=query_type, value=QueryType.BOTH.value)

gpt_type_rb1 = Radiobutton(root, text="OpenAI", variable=gpt_type, value=1)
gpt_type_rb2 = Radiobutton(root, text="Custom", variable=gpt_type, value=2)

# submit button
submit_button = Button(root, text="Ask", command=get_values)

# upload button
upload_button = Button(root, text='Import data', command= lambda: FormUtil.upload_action(error_label))

# grid
title.grid(row=0, column=0)
query_type_rb1.grid(row=0, column=2, sticky=W)
query_type_rb2.grid(row=0, column=3, sticky=W)
query_type_rb3.grid(row=0, column=4, sticky=W)
blank_line.grid(row=1, column=0)
gpt_type_rb1.grid(row=1, column=2, sticky=W)
gpt_type_rb2.grid(row=1, column=3, sticky=W)
question_label.grid(row=2, column=0)
question_text.grid(row=3, column=0, padx = 20)
submit_button.grid(row=3, column=1, sticky=W)
upload_button.grid(row=3, column=2)
blank_line.grid(row=4, column=0)
error_label.grid(row=5, column=0, columnspan=4, sticky=W, padx = 20)
answer_label.grid(row=6, column=0)
answer_text.grid(row=7, column=0, columnspan=2, padx = 20)

root.mainloop()
