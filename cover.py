from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject
from os import listdir
from os.path import isfile, join
from pathlib import Path

import re


def set_need_appearances_writer(writer: PdfFileWriter):
    # See 12.7.2 and 7.7.2 for more information:
    # http://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
    try:
        catalog = writer._root_object
        # get the AcroForm tree
        if "/AcroForm" not in catalog:
            writer._root_object.update({
                NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
        return writer

    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))
        return writer


def get_cover_writer(infile, field_dictionary):
    pdf = PdfFileReader(open(infile, "rb"), strict=False)

    if "/AcroForm" in pdf.trailer["/Root"]:
        pdf.trailer["/Root"]["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})

    pdf2 = PdfFileWriter()
    set_need_appearances_writer(pdf2)
    if "/AcroForm" in pdf2._root_object:
        pdf2._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})

    pdf2.addPage(pdf.getPage(0))
    pdf2.updatePageFormFieldValues(pdf2.getPage(0), field_dictionary)

    return pdf2


# Assumes files are in format e<exam_number>q<question_number>.pdf and that all exam questions are present
def append_covers(cover_filename, path):
    path = path+"/"
    # Lists all files in specified directory
    files = [f for f in listdir(path) if isfile(join(path, f))]
    # Filter to only questions
    regex = re.compile('p[0-9]q[0-9]+.pdf')
    selected_files = list(filter(regex.match, files))

    exam_question_dict = {}
    # Determine which questions are done in which exams
    for file in selected_files:
        e_s, q_s = file.split('q')
        exam = re.findall('\d+', e_s)[0]
        question = re.findall('\d+', q_s)[0]
        if exam in exam_question_dict.keys():
            exam_question_dict[exam] = (exam_question_dict[exam] + ", " + question)
        else:
            exam_question_dict[exam] = question
    print("Exam-question map:")
    print(exam_question_dict)

    for file in selected_files:
        print("Processing "+file)
        # Fill out cover sheet
        e_s, q_s = file.split('q')
        exam = re.findall('\d+', e_s)[0]
        question = re.findall('\d+', q_s)[0]
        field_dictionary = {"Question number": question,
                            "Paper": exam,
                            "Questions": exam_question_dict[exam]}
        output = get_cover_writer(cover_filename, field_dictionary)
        inputpdf = PdfFileReader(open(path+file, "rb"))

        # Append exam question pdf
        for page in inputpdf.pages:
            output.addPage(page)
        Path("./cover_output").mkdir(exist_ok=True)
        with open("./cover_output/p" + exam + "q" + question + ".pdf", "wb") as outputStream:
            output.write(outputStream)
            
if 'n' not in input("IMPORTANT: Have you filled out the BGN and all relevant checkboxes on the cover sheet? [Y/n]:") and 'n' not in input("Are all questions in the form p[paper number]q[question number].pdf? [Y/n]:"):
    append_covers(input("Cover filename:"), input("Path to questions:"))
else:
    print("Aborting")