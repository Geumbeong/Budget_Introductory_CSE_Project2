import csv
import re
from datetime import datetime
import os
import ast
import pandas as pd

INDEX = 0
DATE = 1
CATEGORY= 3
PRICE = 2
COMMEND_INPUT = 0
DATE_INPUT = 1
CATEGORY_INPUT = 3
PRICE_INPUT = 2

#파일 유효성 검사
def is_valid_csv():
    if not os.path.exists('category.csv'):
        raise FileNotFoundError("파일이 없습니다")
    if not os.path.exists('expense.csv'):
        raise FileNotFoundError("파일이 없습니다")
    if not os.path.exists('income.csv'):
        raise FileNotFoundError("파일이 없습니다")
    if not os.path.exists('etc.csv'):
        raise FileNotFoundError("파일이 없습니다")


def read_etc_price():
    with open('etc.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            return int(row[0])

# 메인 메뉴 출력 함수
def main_menu(etc_price):
    print("1.지출/수입")
    print("2.카테고리")
    print("3.종료")
    print(f"현재 남은 금액 : {etc_price}원\n") # 남은 금액 가져오기
    x = input("위 번호 중 선택해주세요:")
    return x

def income_expense_menu():
    print("\n=======================\n")
    print("i/income 수입 추가하기")
    print("e/expense 지출 추가하기")
    print("d/dir 수입 내역 보기")
    print("h/home 돌아가기")
    print("\n=======================\n")
    x = list(input("(문법 형식에 맞게 입력해주세요):").split(','))

    # 아무 입력이 없을 경우
    if not x:
        x = ["default_value"]

    return x

def category_menu():
    print("\n=======================\n")
    print("카테고리 관리 메뉴")
    print("a/add 카테고리 추가하기")
    print("e/edit 카테고리 편집/병합하기")
    print("r/remove 카테고리 삭제하기")
    print("u/update 미분류 항목 이름 수정하기")
    print("h/home 돌아가기")
    print("\n=======================\n")
    x = list(input("(문법 형식에 맞게 입력해주세요):").split(','))
    return x

# 카테고리 중복 검사
def check_existing_category(category_name, category_type):
    is_income_section = True
    with open('category.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] == "#":
                is_income_section = False  # '#' 이후는 지출 섹션
                continue

            if ((is_income_section and category_type in ["i", "income"]) or
               (not is_income_section and category_type in ["e", "expense"])):
                if row and row[0].strip() == category_name:
                    return True  # 중복되는 카테고리가 있음
    return False

# 카테고리 추가
def category_add(category_name, category_type):
    # 중복 검사
    if check_existing_category(category_name, category_type):
        print(f"오류: '{category_name}' 카테고리가 이미 존재합니다.")
        return

    updated_rows = []
    with open('category.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            updated_rows.append(row)
            # 수입/지출 구분자인 "#"에 따라 추가 위치 결정
            if row and row[0] == "#" and category_type in ["e", "expense"]:
                updated_rows.append([category_name, "0"])
            elif row and row[0] == "#" and category_type in ["i", "income"]:
                updated_rows.insert(-1, [category_name, "0"])

    with open('category.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)
    print(f"카테고리 '{category_name}'이(가) 추가되었습니다.")

# 카테고리 삭제 함수
def category_remove(category_name, category_type):
    updated_rows = []
    category_found = False

    with open('category.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] == "#":
                updated_rows.append(row)
                continue

            if (category_type in ["i", "income"] and row[0].strip() == category_name) or \
               (category_type in ["e", "expense"] and row[0].strip() == category_name):
                category_found = True
                updated_rows.append([f"*{row[0]}", row[1]])  # 카테고리 이름 앞에 "*" 추가
            else:
                updated_rows.append(row)

    if category_found:
        with open('category.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)
        print(f"카테고리 '{category_name}'이(가) 삭제되었습니다.")
    else:
        print(f"오류: '{category_name}' 카테고리를 '{category_type}' 유형에서 찾을 수 없습니다.")
        return

    filename = 'income.csv' if category_type in ["i", "income"] else 'expense.csv'
    updated_entries = []

    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[CATEGORY_INPUT] == category_name:
                row[CATEGORY_INPUT] = f"*{row[CATEGORY_INPUT]}"
            updated_entries.append(row)

    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_entries)

# 카테고리 목록 출력 함수
def category_list_print():
    display_items = []   # 출력할 항목만 저장하는 리스트
    current_section = 'income'
    index = 1

    # CSV 파일 읽기 및 항목 추가
    with open('category.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # 비어있지 않은 행에 대해서만 처리
                if row[0].strip() == '#':
                    current_section = 'expense'
                else:
                    item = {
                        'index': index,
                        'section': current_section,
                        'name': row[0].strip(),
                        'amount': row[1].strip()
                    }
                    if not item['name'].startswith('*'):  # "*"로 시작하지 않는 항목만 출력 리스트에 추가
                        display_items.append(item)
                    index += 1

    # 결과 출력
    print("\n카테고리 목록")
    for i, item in enumerate(display_items, start=1):
        print(f"{i}. {item['name']} ({'수입' if item['section'] == 'income' else '지출'})")

    return display_items


# 카테고리 편집 함수
def change_category():
    display_items = []   # 출력할 항목만 저장하는 리스트
    income_items = []    # income 항목 리스트
    expense_items = []   # expense 항목 리스트
    current_section = 'income'
    index = 1

    # CSV 파일 읽기 및 항목 추가
    with open('category.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # 비어있지 않은 행에 대해서만 처리
                if row[0].strip() == '#':
                    current_section = 'expense'
                else:
                    item = {
                        'index': index,
                        'section': current_section,
                        'name': row[0].strip(),
                        'amount': row[1].strip()
                    }
                    if current_section == 'income':
                        income_items.append(item)
                    else:
                        expense_items.append(item)
                    if not item['name'].startswith('*'):  # "*"로 시작하지 않는 항목만 출력 리스트에 추가
                        display_items.append(item)
                    index += 1

    # 결과 출력
    print("\n카테고리 목록")
    for i, item in enumerate(display_items, start=1):
        print(f"{i}. {item['name']} ({'수입' if item['section'] == 'income' else '지출'})")

    # 수정할 항목 선택 및 이름 수정
    try:
        input_choices = input("\n수정할 항목 1개나 병합할 항목들 2개 이상을 선택해주세요: ")
        if not re.match(r'^[0-9]+(,[0-9]+)*$', input_choices):
            print("유효한 번호를 입력해주세요. 메인 메뉴로 돌아갑니다.")
            return
        choices = list(map(int, input_choices.split(',')))
        # 입력된 번호가 유효한지 체크
        if any(choice < 1 or choice > len(display_items) for choice in choices):
            print("잘못된 번호입니다. 메인 메뉴로 돌아갑니다.")
            return() 
        selected_items = [display_items[choice - 1] for choice in choices]  # display_items에서 선택된 항목 가져오기
        selected_indices = [choice - 1 for choice in choices]  # 선택된 항목의 인덱스
    except ValueError:
        print("유효한 번호를 입력해주세요. 메인 메뉴로 돌아갑니다.")
        return()  # 프로그램 종료

    # 선택한 항목의 section 검증
    section_set = {item['section'] for item in selected_items}
    if len(section_set) > 1:
        print("수입과 지출 항목을 동시에 병합할 수 없습니다. 메인 메뉴로 돌아갑니다.")
        return

    # 선택된 항목 수정
    old_names = [item['name'] for item in selected_items]
    new_name = input("새로운 항목 이름을 입력해주세요: ")
    if not re.match(r'^[a-zA-Z가-힣0-9 ]*$', new_name):
        print("유효한 이름을 입력해주세요. 메인 메뉴로 돌아갑니다.")
        return()  # 프로그램 종료
    new_amount = sum(int(item['amount']) for item in selected_items)

    deleted_sections = []
    for index in sorted(selected_indices, reverse=True):  # 역순으로 삭제
        removed_item = display_items.pop(index)
        if removed_item['section'] == 'income':
            income_items.remove(removed_item)
        else:
            expense_items.remove(removed_item)
        deleted_sections.append(removed_item['section'])

    # 새 항목 추가
    new_item = {'name': new_name, 'amount': str(new_amount)}
    if deleted_sections and deleted_sections[0] == 'income':
        income_items.append(new_item)
    else:
        expense_items.insert(0, new_item)

    # 수정된 내용 저장
    with open('category.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for item in income_items:
            writer.writerow([item['name'], item['amount']])
        writer.writerow(['#'])
        for item in expense_items:
            writer.writerow([item['name'], item['amount']])

    filename = selected_items[0]['section'] + '.csv'
    for old_name in old_names:
        update_csv(filename, old_name, new_name)

    print("항목이 성공적으로 수정/병합 되었습니다!")

# 카테고리 변경으로 인한 csv 업데이트
def update_csv(file_name, old_category, new_category):
    rows = []

    # 기존 내용을 읽어서 수정
    with open(file_name, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                if len(row) > 2 and old_category in row[2]:
                    # row[2]에서 ','를 기준으로 각 카테고리 분리
                    categories = row[2][1:-1].split(',')  # '['와 ']'를 제외한 부분을 분리
                    categories = [category.strip() for category in categories]  # 공백 제거
                    categories = [new_category if category == old_category else category for category in categories]

                    row[2] = f"[{', '.join(categories)}]"

                rows.append(row)

# 카테고리 관리 함수
def category():
    while True:
        try:
            menu_input = category_menu()
            if not menu_input:
                print("오류: 입력이 비어있습니다. 다시 입력해 주세요.")
                continue

            if menu_input[0] in ['a', 'add']:
                category_type = input("카테고리 유형을 선택하세요 (i/income 또는 e/expense):").strip().lower()
                if category_type not in ["i", "income", "e", "expense"]:
                    print("오류: 유효한 카테고리 유형을 입력하세요. (i/income 또는 e/expense)")
                    continue

                category_name = input("추가할 카테고리 이름을 입력하세요:")
                if not re.match(r'^[\w\s]*$', category_name):
                    print("오류: 카테고리 이름은 한글, 영문, 공백, 숫자로만 구성해야 합니다.")
                    continue

                category_add(category_name, category_type)

            elif menu_input[0] in ['e', 'edit']:
              change_category()

            elif menu_input[0] in ['r', 'remove']:
                category_type = input("카테고리 유형을 선택하세요 (i/income 또는 e/expense):").strip().lower()
                if category_type not in ["i", "income", "e", "expense"]:
                    print("오류: 유효한 카테고리 유형을 입력하세요. (i/income 또는 e/expense)")
                    continue

                category_name = input("삭제할 카테고리 이름을 입력하세요:")
                if not re.match(r'^[\w\s]*$', category_name):
                    print("오류: 카테고리 이름은 한글, 영문, 공백, 숫자로만 구성해야 합니다.")
                    continue

                category_remove(category_name, category_type)
            elif menu_input[0] in ['u', 'update']:
                new_income_name = input("새로운 '미지정 수입' 이름을 입력하세요: ")
                new_expense_name = input("새로운 '미지정 지출' 이름을 입력하세요: ")
                update_uncategorized_name(new_income_name, new_expense_name)
                
            elif menu_input[0] in ['h', 'home']:
                break
            else:
                print("오류: 명령어가 올바르지 않습니다. (a/add, r/remove, h/home 중 하나를 입력하세요)")

        except Exception as e:
            print(f"예기치 않은 오류가 발생했습니다: {e}")

# 수입 추가
def income_add(input):

    etc_price = read_etc_price()
    # 남은 금액 변경
    etc_price += int(input[PRICE_INPUT])

    with open('etc.csv','r',encoding='utf-8') as file:
        reader = csv.reader(file)
        new_index = int(list(reader)[0][1]) + 1

    with open('etc.csv','w',encoding='utf-8') as file:
        file.write(str(etc_price) + "," + str(new_index))

     # 리스트를 쉼표로 구분된 문자열로 변환
    input_str = str(new_index) + "," + ",".join(map(str, input[1:])) + "\n"

    # lines csv에 추가
    with open('income.csv','a',encoding='utf-8') as file:
        file.write(input_str)

    return etc_price

#지출 추가
def expense_add(input):

    etc_price = read_etc_price()
    # 남은 금액 변경
    etc_price -= int(input[PRICE_INPUT])

    with open('etc.csv','r',encoding='utf-8') as file:
        reader = csv.reader(file)
        new_index = int(list(reader)[0][1]) + 1

    with open('etc.csv','w',encoding='utf-8') as file:
        file.write(str(etc_price) + "," + str(new_index))

    # 리스트를 쉼표로 구분된 문자열로 변환
    input_str = str(new_index) + "," + ",".join(map(str, input[1:])) + "\n"

    # lines csv에 추가
    with open('expense.csv','a',encoding='utf-8') as file:
        file.write(input_str)

    return etc_price

#기간별 출력
def print_date():
    f=open('income.csv','r',encoding='utf-8')
    rdr = csv.reader(f)
    plist=[]
    for i in rdr:
        i.append('수입')
        plist.append(i)
    f1=open('expense.csv','r',encoding='utf-8')
    rdr = csv.reader(f1)
    list1=[]
    for i in rdr:
        i.append('지출')
        list1.append(i)
    plist.extend(list1)
    for i in plist:
        elist=[]
        for j in i[3:]:
            if ']' in j:
                if '[' not in j:
                    elist.append(j[:len(j)-1])
                else:
                    elist.append(j[1:len(j)-1])
                i.remove(j)
                break
            if '[' in j:
                elist.append(j[1:])
            else:
                elist.append(j)
            i.remove(j)
        i.insert(3, elist)
    plist = sorted(plist, key=lambda plist: (plist[1], plist[0]))
    f.close()
    f1.close()
    while True: #년도 입력
        date = input("날짜를 입력해주세요:")
        if len(date)==4 and str.isdigit(date):
            year=date
            month=00
            day=00
            break
        elif len(date)==7:
            if str.isdigit(date[0:4]) and str.isdigit(date[5:7]):
                if (date[4]=='/' or date[4]==',' or date[4]=='-') and int(date[5:7])>=1 and int(date[5:7])<=12:
                    year=date[0:4]
                    month=date[5:7]
                    day=00
                    break
        elif len(date)==10:
            if str.isdigit(date[0:4]) and str.isdigit(date[5:7]) and str.isdigit(date[8:10]):
                if (date[4]=='/' or date[4]==',' or date[4]=='-') and int(date[5:7])>=1 and int(date[5:7])<=12 and date[4]==date[7]:
                    date = date.replace('/', '-').replace(',', '-')
                    try:
                        # 날짜 유효성 검사 (존재하는 날짜인지 확인)
                        datetime.strptime(date, "%Y-%m-%d")
                        year=date[0:4]
                        month=date[5:7]
                        day=date[8:10]
                        break
                    except ValueError:
                        print("문법형식에 맞게 다시 입력해주세요.")
                        continue
        print("문법형식에 맞게 다시 입력해주세요.")
        
    category_num = print_specific_category()

    if (not category_num == '*'):
        for entry in plist[:]:
            if category_num not in entry[3]:
                print(entry)
                plist.remove(entry)

    for i in plist[:]:
            if i[1][0:4]!=year:
                plist.remove(i)
    if month!=00:
        for i in plist[:]:
            if i[1][5:7]!=month:
                plist.remove(i)
    if day!=00:
        date=year+'-'+month+'-'+day
        date = pd.to_datetime(date).weekofyear
        for i in plist[:]:
            check = pd.to_datetime(i[1]).weekofyear
            if date!=check:
                plist.remove(i)
                
    
    count=1

    print('\n번호  날짜  수입액 지출액 [카테고리(들)] 사유')
    for i in plist:
        print(count, end=' ')
        count+=1
        print(i[1], end=' ')
        if i[len(i)-1]=='수입':
            print(i[2]+'    ', end=' ')
        else:
            print('    '+i[2], end=' ')
        print(i[3], end=' ')
        if len(i)==6:
            print(i[len(i)-2])
        else:
            print()
    print("\n=======================\n")
    print("i/income 수입 추가하기")
    print("e/expense 지출 추가하기")
    print("d/dir 수입 내역 보기")
    print("h/home 돌아가기")
    
#기간별 출력 (+특정 카테고리)
def print_specific_category():
    while (1):
        specific_category_input = input("특정 카테고리만 출력하시겠습니까? (맞으면 y/ 아니면 n) : ")
        if specific_category_input == 'y':
            display_list = category_list_print()
            print("\n카테고리가 삭제된 항목을 출력하고 싶으시면 0을 입력해주세요.")
            category_num = input("출력할 카테고리의 번호를 입력해주세요 : ")
            while(re.fullmatch(r'^[0-9]\d*$',category_num) and int(category_num) <= len(display_list)):
                if (category_num == '0'):
                    return ''
                return display_list[int(category_num) - 1].get('name')
            print("잘못된 값을 입력하였습니다. 다시 입력해주세요. \n")
        elif specific_category_input == 'n':
            print()
            return '*';
        else:
            print("잘못된 값을 입력하였습니다. 다시 입력해주세요.\n")
        
#카테고리별 추가
def add_to_category(income_expense_input, validate_income_expense):
    updated_rows = []  # 업데이트된 내용을 저장할 리스트
    category_found = False  # 카테고리가 발견되었는지 여부를 추적하는 변수
    category_validated = 0

    # 금액 입력값을 확인하고 정수로 변환
    try:
        amount_to_add = int(income_expense_input[PRICE_INPUT])
    except ValueError:
        return False

    # 파일 읽기
    with open('category.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        current_section = None

        for row in reader:
            if row:  # 비어있지 않은 행에 대해서만 처리
                if row[0] == '#':
                    # 수입/지출 구분점에서 #을 추가하고, current_section 업데이트
                    updated_rows.append(row)
                    current_section = 'expense'
                elif current_section is None:
                    # # 전이면 수입 섹션
                    current_section = 'income'
                    updated_rows.append(row)
                else:
                    # 카테고리 확인
                    category = row[0].strip()  # 카테고리 이름
                    # 두 번째 열이 있을 경우에만 금액 처리
                    if len(row) > 1:
                        try:
                            amount = int(row[1].strip())  # 기존 금액
                        except ValueError:
                            amount = 0  # 금액이 숫자가 아닌 경우 0으로 처리
                    else:
                        amount = 0  # 두 번째 열이 없으면 금액을 0으로 처리

                    
                    # is_error = False
                    i = 0
                    start_category = False

                    while(not category_found):
                        category_name = income_expense_input[CATEGORY_INPUT + i]  # 입력된 카테고리 이름
                    

                        # 아무 카테고리에도 속하지 않을 경우
                        if category_name == "[]":
                            category_found = True

                        # 맨 처음 괄호
                        try:
                            if category_name[0] == "[":
                                category_name = category_name[1:]
                                start_category = True
                        except IndexError:
                            # 빈 문자열일 경우
                            #is_error = True
                            return False

                        # 맨 마지막 괄호
                        try:
                            if category_name[len(category_name) - 1] == "]" and start_category:
                                category_name = category_name[:-1]
                                category_count = i + 1
                        except IndexError:
                            # is_error = True
                            return False

                        # 해당 카테고리가 맞고, 올바른 섹션인지 확인
                        if category == category_name and current_section == validate_income_expense:
                            amount += amount_to_add  # 금액 업데이트  
                            category_validated += 1
                            if category_count == category_validated:
                                category_found = True
                        
                        i += 1
                        # 입력받은 카테고리가 없을 경우
                        if len(income_expense_input) <= CATEGORY_INPUT + i:
                            break


                    # 업데이트된 행 추가
                    updated_rows.append([category, amount])


    # 카테고리를 찾지 못했을 경우 False 반환
    if not category_found:
        return False

    # 파일 업데이트
    with open('category.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

    return True


def delete_to_category(income_expense_input, validate_income_expense):
    updated_rows = []  # 업데이트된 내용을 저장할 리스트
    category_found = False
    category_name = income_expense_input[CATEGORY]
    amount_to_delete = int(income_expense_input[PRICE])

    with open('category.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        is_income_section = True

        for row in reader:
            if row:  # 비어있지 않은 행에 대해서만 처리
                # 섹션 확인
                if row[0] == "#":
                    is_income_section = False
                    updated_rows.append(row)  # 구분자 추가
                    continue

                # 카테고리와 섹션이 일치하는 경우 금액 삭제
                if ((is_income_section and validate_income_expense == 'income') or
                    (not is_income_section and validate_income_expense == 'expense')) and row[0].strip() == category_name:
                    amount = max(int(row[1].strip()) - amount_to_delete, 0)  # 금액 삭제 후 최소 0으로 제한
                    updated_rows.append([category_name, str(amount)])  # 수정된 금액 추가
                    category_found = True  # 카테고리 찾음
                else:
                    updated_rows.append(row)  # 카테고리 찾지 못한 경우 원본 추가

    if not category_found:
        return False

    # 업데이트된 내용을 파일에 쓰기
    with open('category.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)
    return True

def validate_and_parse_date(data_input):
    # 정규 표현식 패턴: 2024-05-12, 2024/05/12, 2024,05,12 형식만 허용
    pattern = r'^\d{4}[-/,]\d{2}[-/,]\d{2}$'

    # 입력이 패턴과 일치하는지 검사
    if re.match(pattern, data_input[DATE_INPUT]):
        # 다양한 구분자를 표준화하여 파싱 (모두 '-'로 통일)
        normalized_date = data_input[DATE_INPUT].replace('/', '-').replace(',', '-')
        try:
            # 날짜 유효성 검사 (존재하는 날짜인지 확인)
            datetime.strptime(normalized_date, "%Y-%m-%d")
            return True
        except ValueError:
            print("오류 : 입력하신 날짜 형식이 올바르지 않습니다. (현행 그레고리력에 존재하는 날짜가 아닙니다.)")
            return False
    else:
        print("오류 : 입력하신 날짜 형식이 올바르지 않습니다. 허용되는 형식은 YYYY-MM-DD, YYYY/MM/DD, YYYY,MM,DD입니다.")
        return False

def validate_number(income_expense_input):
    price = income_expense_input[PRICE_INPUT]

    # 음수인지 확인
    if price.startswith('-'):
        print(f"오류 : 입력하신 금액 입력 형식이 올바르지 않습니다. (금액은 음수일 수 없습니다.)")
        return False

    elif price.startswith(' '):
        print(f"오류 : 입력하신 금액 입력 형식이 올바르지 않습니다. (금액은 숫자로만 표현되어야 합니다.)")
        return False

    # 맨 앞이 0으로 시작하는지 확인 (단, 숫자가 '0'인 경우는 허용)
    if price.startswith('0') and len(price) > 1:
        print(f"오류 : 입력하신 금액 입력 형식이 올바르지 않습니다. (금액은 0으로 시작할 수 없습니다.)")
        return False

    # 새롭게 추가된 부분
    try : int(income_expense_input[PRICE_INPUT])
    except :
        print(f"오류 : 입력하신 금액 입력 형식이 올바르지 않습니다. (금액은 숫자로만 표현되어야 합니다.)")
        return False

    return True

# 입력받은 열의 개수가 1개인지 아닌지 (dir, home 여부) 확인
def validate_length(income_expense_input):
    if len(income_expense_input) == 1:
        return False
    return True

# 유효한 날짜 형식인지, 가격 형식인지 확인
def validate_date_and_price():
    if validate_and_parse_date(income_expense_input) and validate_number(income_expense_input):
        return True
    else :
        return False

# dir의 수입 부분 읽어오기
def read_income(file_path='income.csv'):
    income_records = []
    # 어떤 정보는 utf-8로 저장되고 어떤 정보는 cp949로 저장되서 둘다 할 수 있게 만듬
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                # income.csv의 각 행에서 필요한 정보를 가져옴
                if row:  # 비어있지 않은 행 확인
                    income_records.append(row)
    except UnicodeDecodeError:
        # utf-8로 읽기 실패 시 cp949로 다시 시도
        with open(file_path, 'r', encoding='cp949') as file:
            reader = csv.reader(file)
            for row in reader:
                # income.csv의 각 행에서 필요한 정보를 가져옴
                if row:  # 비어있지 않은 행 확인
                    income_records.append(row)

    return income_records

# dir의 지출 부분 읽어오기
def read_expense(file_path='expense.csv'):
    expense_records = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                # income.csv의 각 행에서 필요한 정보를 가져옴
                if row:  # 비어있지 않은 행 확인
                    expense_records.append(row)
    except UnicodeDecodeError:
        # utf-8로 읽기 실패 시 cp949로 다시 시도
        with open(file_path, 'r', encoding='cp949') as file:
            reader = csv.reader(file)
            for row in reader:
                # income.csv의 각 행에서 필요한 정보를 가져옴
                if row:  # 비어있지 않은 행 확인
                    expense_records.append(row)
    return expense_records

# 수입 / 지출 내역 존재 여부
def validate_income_expense():
    if (len(read_income())) == 0 and (len(read_expense()) == 0):
        print("\n=======================\n")
        print("수입/지출 내역이 존재하지 않습니다.")
        return False

    return True

#수입 지출 내역 전체 출력(데이터 저장순서)
def inex_period_records():
    income_records = read_income()
    expense_records = read_expense()
    print("수입 / 지출 내역입니다.\n")
    if (not validate_income_expense()):
        print("\n=======================\n")
        print("수입/지출 내역이 존재하지 않습니다.")
        return -1

    if (len(income_records) > 0):
    # 수입 출력
        print("수입")
        print("번호 날짜 / 금액 / 사유")
        for index, record in enumerate(income_records, start=1):
            if len(record) == 5:
                if "*" in record[2]:
                    print(f"{index} {record[1]} '없음' {record[3]} {record[4]}")
                else:
                    print(f"{index} {record[1]} {record[2]} {record[3]} {record[4]}")
            elif len(record) == 4:
                if "*" in record[2]:
                    print(f"{index} {record[1]} '없음' {record[3]}")
                else:
                    print(f"{index} {record[1]} {record[2]} {record[3]}")
            elif len(record) == 3:
                if "*" in record[2]:
                    print(f"{index} {record[1]} '없음'")
                else:
                    print(f"{index} {record[1]} {record[2]}")
            elif len(record) > 5:
                print(f"{index}",end=" ")
                for i,records in enumerate(record):
                    if i == 0:
                        continue
                    print(f"{records}",end=" ")
                print()
            elif len(record) == 0:
                print("내역이 없습니다.")
            else:
                print("출력 오류")


    if (len(expense_records) > 0):
    # 지출 출력
        print("\n지출")
        print("지출 내역 번호 / 날짜 / 카테고리 / 금액 / 사유")
        for index, record in enumerate(expense_records, start=len(income_records) + 1):  # 수입 내역 번호 이후부터 시작
            if len(record) == 5:
                if "*" in record[2]:
                    print(f"{index} {record[1]} '없음' {record[3]} {record[4]}")
                else:
                    print(f"{index} {record[1]} {record[2]} {record[3]} {record[4]}")
            elif len(record) == 4:
                if "*" in record[2]:
                    print(f"{index} {record[1]} '없음' {record[3]}")
                else:
                    print(f"{index} {record[1]} {record[2]} {record[3]}")
            elif len(record) == 3:
                if "*" in record[2]:
                    print(f"{index} {record[1]} '없음'")
                else:
                    print(f"{index} {record[1]} {record[2]}")
            elif len(record) == 0:
                print("내역이 없습니다.")
            elif len(record) > 5:
                print(f"{index}",end=" ")
                for i,records in enumerate(record):
                    if i == 0:
                        continue
                    print(f"{records}",end=" ")
                print()
            else:
                print("출력 오류")
        return -2

def delete_record(index):
    income_records = read_income()
    expense_records = read_expense()
    # index가 income_records의 길이 보다 작으면 income_records에서 삭제
    if 1 <= index <= len(income_records):
        etc_price = read_etc_price()
        delete_data = income_records[index - 1]

        with open('etc.csv','r',encoding='utf-8') as file:
          reader = csv.reader(file)
          new_index = int(list(reader)[0][1]) - 1

        # 남은 금액 변경
        etc_price -= int(delete_data[PRICE])
        with open('etc.csv','w',encoding='utf-8') as file:
            file.write(str(etc_price)+','+str(new_index))

        # 카테고리 가격 변경
        delete_to_category(delete_data, 'income')

        # 삭제
        del income_records[index - 1]
        with open('income.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            for input_data in income_records:
                writer.writerow(input_data)
        return True

    # index가 지출 부분을 가르킬 경우
    elif index <= len(income_records) + len(expense_records):
        etc_price = read_etc_price()
        delete_data = expense_records[index - len(income_records) - 1]

        with open('etc.csv','r',encoding='utf-8') as file:
          reader = csv.reader(file)
          new_index = int(list(reader)[0][1]) + 1

        # 남은 금액 변경
        etc_price += int(delete_data[PRICE])
        with open('etc.csv','w',encoding='utf-8') as file:
            file.write(str(etc_price)+','+str(new_index))

        # 카테고리 가격 변경
        delete_to_category(delete_data, 'expense')

        # 삭제
        del expense_records[index - len(income_records) - 1]
        with open('expense.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            for input_data in expense_records:
                writer.writerow(input_data)
        return True
    else:
        return False

skip_menu_update = False
is_valid_csv()

# 카테고리에 미분류 항목 추가
def add_uncategorized_to_category_csv():
    # etc.csv에서 미분류 항목 읽기
    uncategorized_income, uncategorized_expense = None, None
    with open('etc.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == "수입":
                uncategorized_income = row[1]
            elif row[0] == "지출":
                uncategorized_expense = row[1]

    if not uncategorized_income or not uncategorized_expense:
        print("오류: etc.csv에 미분류 항목이 정의되지 않았습니다.")
        return

    # category.csv 읽기
    income_categories = []
    expense_categories = []
    with open('category.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        is_expense_section = False
        for row in reader:
            if row and row[0] == "#":
                is_expense_section = True
                continue
            if is_expense_section:
                expense_categories.append(row[0].strip())
            else:
                income_categories.append(row[0].strip())

    # category.csv 업데이트
    with open('category.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for category in income_categories:
            writer.writerow([category, "0"])
        if uncategorized_income not in income_categories:
            writer.writerow([uncategorized_income, "0"])
        writer.writerow(["#"])
        for category in expense_categories:
            writer.writerow([category, "0"])
        if uncategorized_expense not in expense_categories:
            writer.writerow([uncategorized_expense, "0"])


def add_to_uncategorized(file_name, row, category_type):
    # etc.csv에서 미분류 항목 읽기
    uncategorized_income, uncategorized_expense = None, None
    with open('etc.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for line in reader:
            if line[0] == "수입":
                uncategorized_income = line[1]
            elif line[0] == "지출":
                uncategorized_expense = line[1]

    if not uncategorized_income or not uncategorized_expense:
        print("오류: etc.csv에 미분류 항목이 정의되지 않았습니다.")
        return

    uncategorized_category = uncategorized_income if category_type == "income" else uncategorized_expense

    # 금액 가져오기
    amount = int(row[PRICE])
    
    # etc.csv 업데이트
    etc_data = []
    with open('etc.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for line in reader:
            if line and line[0] == category_type:
                line[1] = str(int(line[1]) + amount)  # 미분류 금액 업데이트
            etc_data.append(line)

    with open('etc.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(etc_data)

    # 파일에 미분류 항목 추가
    row[CATEGORY] = uncategorized_category
    with open(file_name, 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

    print(f"항목이 미분류 카테고리 '{uncategorized_category}'로 추가되었습니다.")

#income.csv와 expense.csv에서 미분류 이름 업데이트.
def update_uncategorized_entries(old_income_name, old_expense_name, new_income_name, new_expense_name):

    def process_file(file_name, old_name, new_name):
        updated_rows = []

        with open(file_name, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > CATEGORY and row[CATEGORY] == old_name:
                    row[CATEGORY] = new_name  # 새 이름으로 변경
                updated_rows.append(row)

        # 파일 업데이트
        with open(file_name, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

    # income.csv와 expense.csv 파일 처리
    process_file('income.csv', old_income_name, new_income_name)
    process_file('expense.csv', old_expense_name, new_expense_name)

# 빈 카테고리를 새로 지정된 이름으로 업데이트하는 함수
def process_empty_categories(file_name, uncategorized_category, old_category_name, new_category_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        updated_rows = []
        for row in reader:
            if len(row) > CATEGORY:
                # 빈 카테고리([])를 새로 지정된 이름으로 업데이트
                if row[CATEGORY].strip() == "[]" or not row[CATEGORY].strip():
                    row[CATEGORY] = f"[{uncategorized_category}]"
                # 기존 이름을 새 이름으로 업데이트
                elif row[CATEGORY].strip() == f"[{old_category_name}]":
                    row[CATEGORY] = f"[{new_category_name}]"
            updated_rows.append(row)

    with open(file_name, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

# 미분류 항목 이름을 수정하고 관련 파일에 반영하는 함수
def update_uncategorized_name(new_income_name, new_expense_name):
    etc_data = []
    uncategorized_income, uncategorized_expense = None, None

    # etc.csv에서 기존 이름 가져오기
    with open('etc.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == "수입":
                uncategorized_income = row[1]
                etc_data.append(["수입", new_income_name])
            elif row[0] == "지출":
                uncategorized_expense = row[1]
                etc_data.append(["지출", new_expense_name])
            else:
                etc_data.append(row)

    with open('etc.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(etc_data)

    # category.csv 업데이트
    # add_uncategorized_to_category_csv()

    # income.csv와 expense.csv에서 비어 있는 카테고리와 기존 이름 업데이트
    process_empty_categories('income.csv', new_income_name, uncategorized_income, new_income_name)
    process_empty_categories('expense.csv', new_expense_name, uncategorized_expense, new_expense_name)

    print(f"미분류 항목 이름이 '[{new_income_name}]'와 '[{new_expense_name}]'으로 변경되었습니다.")


while(1):
    # 잘못 입력 했을 시 menu를 skip하도록 함
    if not skip_menu_update:
        etc_price = read_etc_price()
        menu = main_menu(etc_price)
    else:
        menu = input("위 번호 중 선택해주세요:")

    skip_menu_update = False

    if menu == '1':
      income_expense_input = income_expense_menu()
      while(1):
          # 입력받은 열의 개수가 1개인지 아닌지 (dir, home 여부) 확인
          if (validate_length(income_expense_input)):
              if income_expense_input[COMMEND_INPUT] == 'i' or income_expense_input[COMMEND_INPUT] == 'income' :
                    # 유효한 날짜 형식인지, 가격 형식인지 확인
                  if validate_date_and_price():
                        # 수입 내역 추가
                        # 입력받은 카테고리가 카테고리에 있는지 확인 후 추가
                      if add_to_category(income_expense_input, 'income'):
                          etc_price = income_add(income_expense_input)
                          print("성공적으로 추가 되었습니다.")
                          income_expense_input = ['b']
                      else:
                          print("오류! 입력하신 카테고리가 존재하지 않습니다.")
                          income_expense_input = ['a']

              elif income_expense_input[COMMEND_INPUT] == 'e' or income_expense_input[COMMEND_INPUT] == 'expense' :
                  # 유효한 날짜 형식인지, 가격 형식인지 확인
                  if validate_date_and_price():
                      # 지출 내역 추가
                      # 입력받은 카테고리가 카테고리에 있는지 확인 후 추가
                      if add_to_category(income_expense_input, 'expense'):
                          etc_price = expense_add(income_expense_input)
                          print("성공적으로 추가 되었습니다.")
                          income_expense_input = ['b']
                      else:
                          print("오류! 입력하신 카테고리가 존재하지 않습니다.")
                          income_expense_input = ['a']
              else :
                  print("오류 : 명령어가 올바르지 않습니다.")

          else:
              if income_expense_input[COMMEND_INPUT] == 'd' or income_expense_input[COMMEND_INPUT] == 'dir' :

                  if(not validate_income_expense()):
                    income_expense_input = income_expense_menu()
                    continue

                  print("\n=======================\n")
                  print("s/save 등록별 출력 순서")
                  print("p/period 기간별 출력 순서")
                  income_expense_period_value = input("값을 입력해주세요 : ")

                  if (income_expense_period_value == 's' or income_expense_period_value == 'save'):
                      print()
                      check_print_i_e = inex_period_records()
                      while(1):

                        if (check_print_i_e != -1):
                          print()
                          delete_record_index = input("삭제 하실 수입/지출 내역 번호를 선택해주세요 (없으면 0을 눌러주세요):")
                          if delete_record_index == '0':
                              print("수입 / 지출 메뉴로 돌아갑니다.")
                              print("\n=======================\n")
                              print("i/income 수입 추가하기")
                              print("e/expense 지출 추가하기")
                              print("d/dir 수입 내역 보기")
                              print("h/home 돌아가기")
                              break
                            # 입력 받은 수가 정수가 아니라면 에러 발생
                          try:
                              value = int(delete_record_index)
                              if delete_record(value):
                                  print("정상적으로 삭제되었습니다.")
                                  if(not validate_income_expense()):
                                      income_expense_input = income_expense_menu()
                                      break
                                  print("\n=======================\n")
                                  inex_period_records()
                                  print("\n=======================\n")
                              else:
                                  print("오류! 존재하지 않는 수입 / 지출 번호입니다.")
                          except ValueError:
                              print("오류! 잘못된 입력입니다.")
                        else:
                          print("\n=======================\n")
                          print("i/income 수입 추가하기")
                          print("e/expense 지출 추가하기")
                          print("d/dir 수입 내역 보기")
                          print("h/home 돌아가기")
                          break

                  elif (income_expense_period_value == 'p' or income_expense_period_value == 'period'):
                    print_date()

                  else:
                        print("오류! : 명령어가 올바르지 않습니다. home으로 돌아갑니다.")
                        print("\n=======================\n")
                        print("i/income 수입 추가하기")
                        print("e/expense 지출 추가하기")
                        print("d/dir 수입 내역 보기")
                        print("h/home 돌아가기")
                  print("\n=======================\n")

              elif income_expense_input[COMMEND_INPUT] == 'h' or income_expense_input[COMMEND_INPUT] == 'home' :
                  print()
                  break
              elif income_expense_input[COMMEND_INPUT] == 'b':
                continue
              else:
                  print("오류! : 명령어가 올바르지 않습니다.")

          income_expense_input = list(input("(문법 형식에 맞게 입력해주세요):").split(','))
          if not income_expense_input:
              income_expense_input = ["default_value"]
    elif menu == '2':
        category()
    elif menu == '3':
        print("종료합니다.")
        break
    else:
        print("오류 : 잘못된 입력입니다.")
        skip_menu_update = True

