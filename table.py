from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

class Table():
    def __init__(self, path, data):
        self.path = path
        self.rows = data
        self.headers=list(dict.fromkeys([key for _data in data for key in _data.keys()]))

        self.__write_data()

    def __write_data(self):
        wb = Workbook()
        ws = wb.active
        ws.append(self.headers)
        for description in self.rows:
            ws.append(["-" if description.get(head)==None else description.get(head) for head in self.headers])

        for col in ws.columns:
            #Header
            column_name = col[0].column_letter
            col[0].alignment = Alignment(horizontal = "center")
            col[0].font = Font(bold=True)
            
            #Cells
            max_length = max([len(str(cell.value)) for cell in col])* 1.05
            
            ws.column_dimensions[column_name].width = max(min(max_length, 50), 10)
        wb.save(self.path)