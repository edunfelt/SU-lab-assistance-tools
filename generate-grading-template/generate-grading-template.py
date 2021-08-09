import argparse
import csv
from math import floor

def main():
    # Get arguments from commandline - call with -h for help
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--csv',
        required=True,
        dest='csv_file',
        help='Path to csv file to parse (with names/emails/lab status)')
    parser.add_argument(
        '--lab-n',
        required=False,
        type=int,
        dest='lab_n',
        help='Lab number feedback is about')
    parser.add_argument(
        '--TAs',
        required=False,
        type=int,
        dest='TAs_total',
        help='The total number of TAs among whom the grading is split')
    parser.add_argument(
        '--TA-n',
        required=False,
        type=int,
        dest='TA_n',
        help='The TA ID for which you wish to see the students list to grade')
    args = parser.parse_args()

    # Shortcuts
    csv_path = args.csv_file
    N = args.lab_n
    M = args.TAs_total
    K = args.TA_n

    students = parse_csv_to_dict(csv_path)
    students = maybe_purge_nohandin_students(students)
    J = len(students)

    #print(students)

    if N == None or M == None or K == None:
        print('Lab N, TAs total or TA_n is missing, so you will just get a grading template for all students.')
        filename = 'grading-template.txt'
        dump_students_to_file(students, filename)

    else:
        # How many students should there be in each group? z is group ID
        how_many = lambda z: int(floor(J/M) + ((J%M - (z-1))>0))

        # Build list with indexes of each group boundaries
        groups = [(0, how_many(1))]
        for i in range(2, M+1):
            groups.append((groups[-1][1], groups[-1][1] + how_many(i)))

        # Pick group for given TA according to rotation
        group_choser = ((N-1)+(K-1)) % M
        start_index = groups[group_choser][0]
        end_index = groups[group_choser][1]

        print('TA {} takes {} out of {} students, with indexes {}'.format(K, end_index-start_index, J, groups[group_choser]))
        filename = 'lab{}-TA{}.txt'.format(N, K)
        #print(students[start_index:end_index])
        dump_students_to_file(students[start_index:end_index], filename)

def parse_csv_to_dict(csv_path):
    """Parses csv into a dict"""

    students = []
    with open(csv_path, 'r') as handle:
        csvreader = csv.DictReader(handle)
        fields = csvreader.fieldnames

        for row in csvreader:
            student = {
                'name' : row[fields[0]],
                'email' : row[fields[1]],
            }

            # If file has info about current lab (ie comes from peergrade), use it
            if len(fields) > 2:
                student['lab_handedin'] = row[fields[2]]

            students.append(student)
            students = sorted(students, key=lambda k: k['name'])

    return students

def maybe_purge_nohandin_students(students):
    purged_students = []
    for student in students:
        if student.get('lab_handedin'):
            if student['lab_handedin'] == 'Yes':
                purged_students.append(student)
        else: #lacking handin info
            purged_students.append(student)
    return purged_students

def dump_students_to_file(students, filename):
    with open(filename, 'w') as handle:
        for student in students:

            # If we have handedin info, only include students who have handed in
            if student.get('lab_handedin') and student['lab_handedin'] == 'No':
                continue

            handle.write('{}\n'.format(student['name']))
            handle.write('{}\n'.format(student['email']))
            handle.write('none\n') #status

            handle.write('\n\n') #spacing between students

if __name__ == '__main__':
    main()