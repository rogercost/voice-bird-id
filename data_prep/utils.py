import csv

def read_aba_checklist(file_path):
    """
    Reads in a CSV file containing the ABA Checklist and found at https://www.aba.org/aba-checklist/
    The format is as follows:
    "Ducks, Geese, and Swans (Anatidae)",,,,,
    ,Black-bellied Whistling-Duck,Dendrocygne à ventre noir,Dendrocygna autumnalis,BBWD,1
    ,Fulvous Whistling-Duck,Dendrocygne fauve,Dendrocygna bicolor,FUWD,1
    """
    data_structure = {}
    current_section = None
    total_birds = 0

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            # Check if the row is a section heading (only first column has a value)
            if row[0] and all(cell == '' for cell in row[1:]):
                current_section = row[0]
                data_structure[current_section] = []
            elif current_section and row[5] == '1':  # Check if column 6 == 1 aka bird in range, not vagrant
                # Extract columns 2, 4, and 5 (indices 1, 3, 4)
                # English, Scientific, 4-Letter Code
                data_structure[current_section].append((row[1], row[3], row[4]))
                total_birds += 1

    print(f"Read {total_birds} birds from {len(data_structure)} unique families")
    return data_structure