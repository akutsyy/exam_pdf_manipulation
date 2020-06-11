from PyPDF2 import PdfFileWriter, PdfFileReader
from pathlib import Path

def split(filename,exam_num, pattern):
    inputpdf = PdfFileReader(open(filename, "rb"),strict=False)

    filepatterns = [s.strip() for s in pattern.split(",")]
    question_nums, pages = zip(*[fp.split(" ") for fp in filepatterns])
    outputs = []
    page = 0
    for i, q in enumerate(question_nums):
        output = PdfFileWriter()
        for p in pages[i]:
            if page >= inputpdf.numPages:
                print("Not enough pages in input pdf, aborting!")
                return
            if p == "1":
                output.addPage(inputpdf.getPage(page))
            page = page + 1
        outputs.append(output)
        print("Exam "+exam_num+", Question "+q+" processed...")


    print("Writing questions...")
    Path("./output").mkdir(exist_ok=True)
    for i,o in enumerate(outputs):
        name = "./output/p"+exam_num+"q"+question_nums[i]+".pdf"
        with open(name,"wb") as outputStream:
            o.write(outputStream)

    if page < inputpdf.numPages:
        print('Warning, '+str(inputpdf.numPages-page)+' pages at end skipped, outputting to "excess.pdf""')
        for i in range(page,inputpdf.numPages):
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(i))
            with open("./output/excess.pdf", "wb") as outputStream:
                output.write(outputStream)


split(input("Input PDF name:"),input("Paper number:"),input("Input pattern: \nForm is as follows: \n4 1101, 5 101 "
                                                           "would interpert the pdf as question 4, keeping page 1,2,"
                                                           "4 and skipping 3, followed by question 5, keeping pages "
                                                           "4,6 and skipping 5\n"))
