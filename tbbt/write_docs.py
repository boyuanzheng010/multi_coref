import xlsxwriter

# Define file
workbook = xlsxwriter.Workbook('test.xlsx')

# Define font
bold = workbook.add_format({'bold': 1})

# Define worksheet
worksheet_0 = workbook.add_worksheet("He")
worksheet_0.write(0, 1, "Hello World")
worksheet_0.write(0, 2, "This is the test", bold)

# Define worksheet
worksheet_1 = workbook.add_worksheet("Lo")
worksheet_1.write(1, 2, "Hi")



workbook.close()
