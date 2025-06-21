from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure

class PdfToText:
    @staticmethod
    def _text_extraction(element):
        # Extracting the text from the in-line text element
        line_text = element.get_text()

        # Find the formats of the text
        # Initialize the list with all the formats that appeared in the line of text
        line_formats = []
        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                # Iterating through each character in the line of text
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Append the font name of the character
                        line_formats.append(character.fontname)
                        # Append the font size of the character
                        line_formats.append(character.size)
        # Find the unique font sizes and names in the line
        format_per_line = list(set(line_formats))

        # Return a tuple with the text in each line along with its format
        return (line_text, format_per_line)

    @staticmethod
    def extract_text_from_pdf(file_path):
        page_text = []
        for pagenum, page in enumerate(extract_pages(file_path)):

            # Iterate the elements that composed a page
            for element in page:

                # Check if the element is a text element
                if isinstance(element, LTTextContainer):
                    # Function to extract text from the text block
                    (line_text, format_per_line) = PdfToText._text_extraction(element)
                    # Append the text of each line to the page text
                    page_text.append(line_text)

                # Check the elements for images
                if isinstance(element, LTFigure):
                    # Function to convert PDF to Image
                    pass

                # Check the elements for tables
                if isinstance(element, LTRect):
                    # Function to extract table
                    pass

        cleared_content = [i for i in page_text if i.rstrip() != ""]
        for item in cleared_content:
            item.rstrip()
        final_content = "".join(cleared_content)
        return final_content