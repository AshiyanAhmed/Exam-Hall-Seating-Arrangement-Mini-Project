import os
import re

import pandas as pd


def check_format(csv_file):
    roll_no_re = r'^[A-Z][A-Z]\d\d$'
    roll_no_compiled = re.compile(roll_no_re)
    dep_compiled = re.compile('^[A-Z][A-Z]')

    df = pd.read_csv(csv_file)
    if 'roll number' not in df.columns:
        return f'There is no column "roll number in {os.path.split(csv_file)[1]}"'
    
    first_dep = dep_compiled.search(df['roll number'][0])
    if first_dep:
        first_dep = first_dep.group()
    else:
        rno = df['roll number'][0]
        return f'{rno} in {os.path.split(csv_file)[1]} is of incorrect type'
    
    for roll_no in df['roll number']:
        if type(roll_no) != str:
            return f'{roll_no} in {os.path.split(csv_file)[1]} is of incorrect type'
        
        if not roll_no_compiled.search(roll_no):
            return f'{roll_no} in {os.path.split(csv_file)[1]} is of incorrect format'
        
        if dep_compiled.search(roll_no).group() != first_dep:
            return f'{roll_no} in {os.path.split(csv_file)[1]} is of different department'

    return 'correct'


def total_len(st_details):
    s = 0
    for d in st_details:
        s += len(d)
    return s



def arrange(st_details: list, rooms_details: list): #params st_details list of dfs, room_details list of dicts
    # st_details.sort(key=lambda p: len(p), reverse=True)

    
    rooms = []
    benches = []
    capacity = 0
    for rd in rooms_details:
        room = pd.DataFrame()
        for i in range(rd['columns']):
            room.insert(i, i, [None]*rd['rows'])
        
        benches.append(rd['benches'])
        capacity += rd['benches']
        rooms.append(room)
    
    if total_len(st_details) > capacity*2:
        return  []

    for dep in st_details:      #checking if there is more students in a department than total no of benches
        if len(dep) > capacity:
            return  []

    students = []
    for dep in st_details:
        l = list(dep['roll number'])
        l.reverse()
        students.append(l)
    students.sort(key=lambda d: len(d))
    

    first_dep = []
    second_dep = []
    for room, num_benches in zip(rooms, benches):

        for col in room.columns:
            for row, val in enumerate(room[col]):
                if not num_benches:
                    break

                if not first_dep:
                    if students:
                        first_dep = students.pop()
                    elif second_dep:
                        first_dep = [None] * len(second_dep)
                    else:
                        room[col][row] = [None, None]
                        num_benches -= 1
                        continue
                
                if not second_dep:
                    if students:
                        second_dep = students.pop()
                    else:
                        second_dep = [None] * len(first_dep)

                room[col][row] = [
                    first_dep.pop(),
                    second_dep.pop()
                ]
                num_benches -= 1

    return rooms


if __name__ == '__main__':
    # df = pd.read_csv('csvs/cs_list.csv')
    # # print(type(df['roll number'][0])) 
    print(check_format('test.csv'))
    # df = pd.DataFrame()
    rooms_details = [
        {
            'room_no': 1,
            'benches': 45,
            'rows': 10,
            'columns': 5
        },
        {
            'room_no': 2,
            'benches': 61,
            'rows': 10,
            'columns': 7
        },
        {
            'room_no': 3,
            'benches': 50,
            'rows': 10,
            'columns': 5
        },

    ]

    st_details = [
        pd.read_csv('csvs/cs_list.csv'),
        pd.read_csv('csvs/ce_list.csv')
        # pd.read_csv('test.csv')
    ]

    # print(*arrange(st_details, rooms_details), sep='\n\n')




            