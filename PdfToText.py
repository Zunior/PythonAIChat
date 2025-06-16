from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure

def text_extraction(element):
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

def extractTextFromPDF(filePath):
    page_text = []
    for pagenum, page in enumerate(extract_pages(filePath)):

        # Iterate the elements that composed a page
        for element in page:

            # Check if the element is a text element
            if isinstance(element, LTTextContainer):
                # Function to extract text from the text block
                (line_text, format_per_line) = text_extraction(element)
                # Append the text of each line to the page text
                page_text.append(line_text)
                pass
                # Function to extract text format
                pass

            # Check the elements for images
            if isinstance(element, LTFigure):
                # Function to convert PDF to Image
                pass
                # Function to extract text with OCR
                pass

            # Check the elements for tables
            if isinstance(element, LTRect):
                # Function to extract table
                pass
                # Function to convert table content into a string
                pass

    clearedContent = [i for i in page_text if i.rstrip() != ""]
    for item in clearedContent:
        item.rstrip()
    finalContent = "".join(clearedContent)
    return finalContent