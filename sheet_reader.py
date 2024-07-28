from openpyxl import worksheet


# SEARCH MIN AND MAX ROW SCHEDULE IN LAST MONTH
def search_max_min(ws: worksheet):
    start = 0
    end = 0
    count = 1
    for row in ws.rows:
        if len(row) != 0:
            if row[0].value == 1:
                start = count
            else:
                end = count
        count += 1
    return start, end


def update_employee_queue(ws: worksheet):
    start, end = search_max_min(ws)
    employee_queue = []
    for col in range(4, 35):
        employee_in_current_day = []

        for row in ws.iter_rows(min_row=start, max_row=end, min_col=1, max_col=col):
            if row[col - 1].value is not None:
                employee_in_current_day.append(row[1].value)
        employee_queue.append(employee_in_current_day)
    return employee_queue
