from tkinter import filedialog
import pathlib
import logging

import Constants
from FileTypeEnum import FileTypeEnum
from PdfToText import PdfToText
import os
from Util import Util
import GPTAI.customgpt
import GPTAI.OpenAI
from tkinter.messagebox import askyesno
import threading

from tkinter import *


class FormUtil:
    @staticmethod
    def get_text_value(obj):
        return obj.get("1.0", 'end-1c')

    @staticmethod
    def start_upload_thread(input_class):
        """Initiates the upload process, showing spinner and starting a new thread."""

        # Clear previous error
        input_class.error_label.config(text="")

        # Disable UI elements and show spinner
        input_class.submit_button.config(state=DISABLED)
        input_class.upload_button.config(state=DISABLED)
        input_class.progress_bar.start(10) # Start the animation
        input_class.status_label.config(text="Importing data...") # Update status label

        # Start the long-running task in a separate thread
        query_thread = threading.Thread(target=FormUtil._perform_upload(input_class))
        query_thread.daemon = True # Allows the program to exit if main window closes
        query_thread.start()

    @staticmethod
    def _perform_upload(input_class):
        # event=None,
        file_full_path = filedialog.askopenfilename()
        file_extension = pathlib.Path(file_full_path).suffix[1:]
        if not file_extension:
            return
        content = ""
        info_error_text = ""
        try:
            file_type = FileTypeEnum[file_extension.upper()]
            match file_type:
                case FileTypeEnum.PDF:
                    content = PdfToText.extract_text_from_pdf(file_full_path)
                case FileTypeEnum.TXT:
                    content = file_full_path

            file_name_with_extension = Util.path_leaf(file_full_path)
            (file_name, extension) = os.path.splitext(file_name_with_extension)

            if os.path.exists(file_full_path) and os.path.isfile(file_full_path) and content:
                storage_full_path = Constants.LOCAL_DATA_DIR + "/" + file_name + ".txt"
                answer = False
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
        except Exception as ve:
            logging.warning(f"Error during query: {ve}")
            info_error_text = f"Error during query: {ve}"
        finally:
            # --- Schedule all GUI updates back on the main thread ---
            input_class.master.after(0, input_class.progress_bar.stop)
            # self.master.after(0, self.progress_bar.grid_forget) # If you want to hide it completely
            input_class.master.after(0, lambda: input_class.submit_button.config(state=NORMAL))
            input_class.master.after(0, lambda: input_class.upload_button.config(state=NORMAL))

            if info_error_text:
                input_class.master.after(0, lambda: input_class.error_label.config(text=info_error_text))
                input_class.master.after(0, lambda: input_class.status_label.config(text="Upload failed."))
            else:
                input_class.master.after(0, lambda: input_class.status_label.config(text="Upload completed."))