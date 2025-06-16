from tkinter import filedialog
import pathlib
import logging
from FileTypeEnum import FileTypeEnum
import PdfToText
import os
import Util
import GPTAI.customgpt
import GPTAI.OpenAI
from tkinter.messagebox import askyesno

from tkinter import *

def get_text_value(obj):
    return obj.get("1.0", 'end-1c')

def upload_action(error_label):
    # event=None,
    file_full_path = filedialog.askopenfilename()
    file_extension = pathlib.Path(file_full_path).suffix[1:]
    if not file_extension:
        return
    content = ""
    try:
        file_type = FileTypeEnum[file_extension.upper()]
        match file_type:
            case FileTypeEnum.PDF:
                content = PdfToText.extractTextFromPDF(file_full_path)
            case FileTypeEnum.TXT:
                content = file_full_path
    except KeyError as ve:
        logging.warning(f"File type not supported: {ve}")
        error_label.configure(text="File type not supported.")

    file_name_with_extension = Util.path_leaf(file_full_path)
    (file_name, extension) = os.path.splitext(file_name_with_extension)

    if os.path.exists(file_full_path) and os.path.isfile(file_full_path) and content:
        storage_full_path = GPTAI.OpenAI.OpenAI._LOCAL_DATA_DIR + "/" + file_name + ".txt"
        answer = False
        info_error_text = ""
        if os.path.exists(storage_full_path):
            answer = askyesno(title='Input data',
                              message='Input data already exists. Do you want to overwrite it? (y/n): ')
        if answer or not os.path.exists(storage_full_path):
            # create data file
            info_error_text = Util.create_data_file(storage_full_path, content)
            # train the custom model
            GPTAI.customgpt.CustomGPT().train_model(content)
        else:
            info_error_text = "Import canceled."

        error_label.configure(text=info_error_text)