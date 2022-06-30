import re
from word2number import w2n


def sec_to_min(sec):
    minutes = sec / 60
    minutes_no_decimal = int(minutes)
    decimal = minutes - minutes_no_decimal
    total_sec = 60 * decimal

    return f'{minutes_no_decimal} min {round(total_sec)} sec'


def sec_to_hour(sec):
    minutes = sec / 60
    hours = minutes / 60
    hours_no_decimal = int(hours)
    decimal = hours - hours_no_decimal
    total_min = 60 * decimal

    return f'{hours_no_decimal} h {round(total_min)} min'

def min_to_hour(min):
    hour = min / 60
    hour_no_decimal = int(hour)
    decimal = hour - hour_no_decimal
    total_min = 60 * decimal

    return f'{hour_no_decimal} h {round(total_min)} min'

def remove_unnecessary_model_answer_chars(model_answer):
    model_answer = str(model_answer)
    model_answer = model_answer[6: len(model_answer) - 4]
    return model_answer


def extract_year(string: str):
    m = re.search(r'[1-3][0-9]{3}', string)
    if m:
        year = m.group(0)
        return year
    m = re.search(r'[0-9]{3}', string)
    if m:
        year = m.group(0)
        return year
    return string


def has_year(string: str):
    m = re.search(r'[1-3][0-9]{3}', string)
    if m:
        return True
    return False


def extract_two_years(string: str):
    matches = re.findall(r'[1-3][0-9]{3}', string)
    ret = []
    if len(matches) == 2:
        ret.append(matches[0])
        ret.append(matches[1])
        return ret
    ret.append(string)
    return ret


def is_exactly_year(model_an):
    length = len(model_an)
    if not (length == 4 or length == 3):
        return False
    m = re.search(r'[1-3][0-9]{3}', model_an)
    if m:
        return True
    m = re.search(r'[0-9]{3}', model_an)
    if m:
        return True
    return False


def is_yes_no(model_an):
    if model_an == 'yes' or model_an == 'no':
        return True
    return False


def has_duration(model_an):
    if has_numbers(model_an):
        return True
    try:
        w2n.word_to_num(model_an)
        return True
    except ValueError as e:
        print(e)
    return False


def extract_duration(model_an, valid_answer):
    if valid_answer:
        w2n_num = None
        try:
            w2n_num = w2n.word_to_num(model_an)
            return w2n_num
        except ValueError as e:
            print(e)
        if not w2n_num:
            return int(extract_number(model_an))
        return model_an
    return model_an


def has_numbers(model_an):
    m = re.search(r'[0-9]+', model_an)
    if m:
        return True
    return False


def extract_number(model_an):
    m = re.search(r'[0-9]+', model_an)
    if m:
        year = m.group(0)
        return year


def has_two_entries(model_an):
    if len(model_an) == 2:
        return True
    return False


def check_yes_no_correct(an, model_an):
    if an == model_an:
        return True
    return False


def check_if_an_in_interval(model_an, an, valid_answer):
    if valid_answer:
        if an:
            an = int(an)
        if an in model_an:
            return True
    return False


def check_if_equal(model_an, an, valid_answer):
    if valid_answer:
        if an:
            an = int(an)
        if an == model_an:
            return True
    return False


def check_if_first_and_last_equal(model_an, an, valid_answer):
    if valid_answer:
        an_first = int(an[0])
        an_last = int(an[1])

        model_an_first = model_an[0]
        model_an_last = model_an[len(model_an) - 1]
        if an_first == model_an_first:
            if an_last == model_an_last:
                return True
    return False


def remove_underline_and_capitalise(question_type: str):
    return question_type.replace('_', ' ').title()


# qe -> question
def estimated_model_time_consumption(n_qe, sec_per_100_qe):
    n_qe = n_qe/100
    return sec_to_hour(sec_per_100_qe * n_qe)