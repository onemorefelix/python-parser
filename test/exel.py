import xlsxwriter
# открываем новый файл на запись
workbook = xlsxwriter.Workbook('hello.xlsx')
# создаем там "лист"
worksheet = workbook.add_worksheet()
# в ячейку A1 пишем текст
worksheet.write('A1', 'Hello world')
worksheet.write('B1', 'Hello world')
worksheet.write('B2', 'Hello world')
worksheet.write('C3', 'Hello world')
# сохраняем и закрываем
workbook.close()