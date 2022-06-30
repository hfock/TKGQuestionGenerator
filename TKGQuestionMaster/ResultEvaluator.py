import TKGQuestionMaster.HelperUtils as helper
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

VALID_ANSWER = 'valid_answer'
CORRECT_ANSWER = 'correct_answer'
TIME_PROCESSED = 'time_processed'
CORRECT_PERCENTAGE = 'correct_percentage'
QUESTION_TYPE = "question_type"
SIZE = 'size'


def eval_yes_no(df, version):
    yes_no = ['yes_no_qe', 'yes_no_an', 'yes_no_model_an', 'yes_no_time', 'predicate']

    cur_columns = yes_no
    qe_name = f'yes_no_{version}'
    an = cur_columns[1]
    model_an = cur_columns[2]

    df = df.loc[:, cur_columns]
    model_time = df[cur_columns[3]].iloc[0]
    df = df.dropna()

    df[model_an] = df[model_an].apply(
        lambda x: helper.remove_unnecessary_model_answer_chars(x.lower()))

    df[VALID_ANSWER] = df[model_an].apply(
        lambda x: helper.is_yes_no(x))

    df[CORRECT_ANSWER] = df.apply(lambda x: helper.check_yes_no_correct(x[an], x[model_an]), axis=1)
    df[qe_name + '_' + CORRECT_ANSWER] = df.apply(lambda x: helper.check_yes_no_correct(x[an], x[model_an]), axis=1)

    results, predicate_results = get_results(df, qe_name, model_time)
    return results, predicate_results, df


def eval_yes_no_robust(df, version, complete_interval):
    if complete_interval:
        qe_name = f'yes_no_robust_{version}_complete_interval'
    else:
        qe_name = f'yes_no_robust_{version}_single_value'
    an = 'yes_no_robust_an'
    model_an = 'yes_no_robust_model_an'

    model_time = df['yes_no_robust_time'].iloc[0]
    df = df.dropna()

    df[model_an] = df[model_an].apply(
        lambda x: helper.remove_unnecessary_model_answer_chars(x.lower()))

    df[VALID_ANSWER] = df[model_an].apply(
        lambda x: helper.is_yes_no(x))

    df[CORRECT_ANSWER] = df.apply(lambda x: helper.check_yes_no_correct(x[an], x[model_an]), axis=1)
    df[qe_name + '_' + CORRECT_ANSWER] = df.apply(lambda x: helper.check_yes_no_correct(x[an], x[model_an]), axis=1)

    correct_indices = get_indices_of_all_correctly_answered_questions(df)

    print(qe_name)
    return get_results_yes_no_robust(df, qe_name, len(correct_indices), model_time), df


def get_indices_of_all_correctly_answered_questions(df):
    correct_indices = []

    for i, entry in df.groupby('qe_index'):
        all_questions_correctly_answered = all(entry['correct_answer'])
        if all_questions_correctly_answered:
            correct_indices.append(entry['correct_answer'].index.to_list())
    return correct_indices


def eval_when(df, version):
    when = ['when_qe', 'when_an', 'when_model_an', 'when_time', 'predicate']

    cur_columns = when
    qe_name = f'when_{version}'
    an = cur_columns[1]
    model_an = cur_columns[2]

    df = df.loc[:, cur_columns]
    model_time = df[cur_columns[3]].iloc[0]
    df = df.dropna()

    df[model_an] = df[model_an].apply(
        lambda x: helper.remove_unnecessary_model_answer_chars(x.lower()))

    df[model_an] = df[model_an].apply(
        lambda x: helper.extract_year(x))

    df[VALID_ANSWER] = df[model_an].apply(
        lambda x: helper.is_exactly_year(x))

    df[CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_an_in_interval(x[an], x[model_an], x[VALID_ANSWER]), axis=1)
    df[qe_name + '_' + CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_an_in_interval(x[an], x[model_an], x[VALID_ANSWER]), axis=1)

    results, predicate_results = get_results(df, qe_name, model_time)
    return results, predicate_results, df


def evaluate_left_open(df, version):
    left_open = ['left_open_qe', 'left_open_an', 'left_open_model_an', 'left_open_time', 'predicate']

    return eval_left_or_right_open(df, left_open, f'left_open_{version}')


def evaluate_right_open(df, version):
    right_open = ['right_open_qe', 'right_open_an', 'right_open_model_an', 'right_open_time', 'predicate']
    return eval_left_or_right_open(df, right_open, f'right_open_{version}')


def eval_left_or_right_open(df, cur_columns, qe_name):
    an = cur_columns[1]
    model_an = cur_columns[2]

    df = df.loc[:, cur_columns]
    model_time = df[cur_columns[3]].iloc[0]
    df = df.dropna()

    df[model_an] = df[model_an].apply(
        lambda x: helper.remove_unnecessary_model_answer_chars(x.lower()))

    df[model_an] = df[model_an].apply(
        lambda x: helper.extract_year(x))

    df[VALID_ANSWER] = df[model_an].apply(
        lambda x: helper.is_exactly_year(x))

    df[CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_equal(x[an], x[model_an], x[VALID_ANSWER]), axis=1)
    df[qe_name + '_' + CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_equal(x[an], x[model_an], x[VALID_ANSWER]), axis=1)

    results, predicate_results = get_results(df, qe_name, model_time)
    return results, predicate_results, df


def eval_until_when(df, version, *, exact_answer=True):
    until_when = ['until_when_qe', 'until_when_an', 'until_when_model_an', 'until_when_time', 'predicate']

    cur_columns = until_when
    qe_name = f'until_when_{version}'
    an = cur_columns[1]
    model_an = cur_columns[2]

    df = df.loc[:, cur_columns]
    model_time = df[cur_columns[3]].iloc[0]
    df = df.dropna()

    df[model_an] = df[model_an].apply(
        lambda x: helper.remove_unnecessary_model_answer_chars(x.lower()))

    df[model_an] = df[model_an].apply(
        lambda x: helper.extract_year(x))

    df[VALID_ANSWER] = df[model_an].apply(
        lambda x: helper.is_exactly_year(x))

    if exact_answer:
        df[CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_equal(x[an], x[model_an], x[VALID_ANSWER]), axis=1)
        df[qe_name + '_' + CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_equal(x[an], x[model_an], x[VALID_ANSWER]), axis=1)
    else:
        df[CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_an_in_interval(x[an], x[model_an], x[VALID_ANSWER]),
                                      axis=1)
        df[qe_name + '_' + CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_an_in_interval(x[an], x[model_an], x[VALID_ANSWER]),
                                              axis=1)

    results, predicate_results = get_results(df, qe_name, model_time)
    return results, predicate_results, df


def eval_when_to_when(df, version):
    when_to_when = ['when_to_when_qe', 'when_to_when_an', 'when_to_when_model_an', 'when_to_when_time', 'predicate']

    cur_columns = when_to_when
    qe_name = f'when_to_when_{version}'
    qe = cur_columns[0]
    an = cur_columns[1]
    model_an = cur_columns[2]

    df = df.loc[:, cur_columns]
    model_time = df[cur_columns[3]].iloc[0]
    df = df.dropna()

    df[model_an] = df[model_an].apply(
        lambda x: helper.remove_unnecessary_model_answer_chars(x.lower()))

    df[model_an] = df[model_an].apply(
        lambda x: helper.extract_two_years(x))

    df[VALID_ANSWER] = df[model_an].apply(
        lambda x: helper.has_two_entries(x))

    df[CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_first_and_last_equal(x[an], x[model_an], x[VALID_ANSWER]),
                                  axis=1)
    df[qe_name + '_' + CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_first_and_last_equal(x[an], x[model_an], x[VALID_ANSWER]),
                                  axis=1)

    results, predicate_results = get_results(df, qe_name, model_time)
    return results, predicate_results, df


def eval_duration(df, version):
    duration = ['duration_qe', 'duration_an', 'duration_model_an', 'duration_time', 'predicate']

    cur_columns = duration
    qe_name = f'duration_{version}'
    qe = cur_columns[0]
    an = cur_columns[1]
    model_an = cur_columns[2]

    df = df.loc[:, cur_columns]
    model_time = df[cur_columns[3]].iloc[0]
    df = df.dropna()

    df[model_an] = df[model_an].apply(lambda x: helper.remove_unnecessary_model_answer_chars(x.lower()))

    df[VALID_ANSWER] = df[model_an].apply(lambda x: helper.has_duration(x))

    df[model_an] = df.apply(lambda x: helper.extract_duration(x[model_an], x[VALID_ANSWER]), axis=1)

    df[CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_equal(x[an], x[model_an], x[VALID_ANSWER]), axis=1)
    df[qe_name + '_' + CORRECT_ANSWER] = df.apply(lambda x: helper.check_if_equal(x[an], x[model_an], x[VALID_ANSWER]), axis=1)

    results, predicate_results = get_results(df, qe_name, model_time)
    return results, predicate_results, df


def get_results(df, question_type, time_processed, predicate=True):
    result = {'question_type': question_type,
              'size': len(df),
              VALID_ANSWER: sum(df[VALID_ANSWER]),
              CORRECT_ANSWER: sum(df[CORRECT_ANSWER]),
              'time_processed': helper.sec_to_min(time_processed)}
    result['correct_percentage'] = result[CORRECT_ANSWER] / result['size']

    predicate_results = {}
    if predicate:
        for i, entry in df.groupby('predicate'):
            predicate_results[i + '_' + CORRECT_ANSWER] = sum(entry[CORRECT_ANSWER])
            predicate_results[i + '_' + VALID_ANSWER] = sum(entry[VALID_ANSWER])
            predicate_results[i + '_' + SIZE] = len(entry)
            predicate_results['question_type'] = question_type
    return result, predicate_results


def get_results_yes_no_robust(df, question_type, correctly_answered_entities, time_processed, predicate=False):
    result, predicate_results = get_results(df, question_type, time_processed, predicate)
    result['correctly_answered_entities'] = correctly_answered_entities
    result['correct_percentage'] = result[CORRECT_ANSWER] / result['size']
    result['correctly_answered_entities_percentage'] = correctly_answered_entities / len(df.groupby('qe_index'))
    return result, predicate_results


def result_to_df(results_dict):
    return pd.DataFrame.from_dict(results_dict, orient='index').T


def generate_pie_chart(result_df, path, qe_type=None):
    for i, entry in result_df.iterrows():
        if qe_type:
            qe_type = qe_type
        else:
            qe_type = entry[QUESTION_TYPE]
        n_cor_ans = entry[CORRECT_ANSWER]
        n_incor_ans = entry[SIZE] - n_cor_ans
        cor_percentage = round(entry[CORRECT_PERCENTAGE] * 100, 2)

        y = np.array([n_cor_ans, n_incor_ans])
        labels = ['Correct answers', 'Incorrect answers']

        plt.pie(y, labels=labels, autopct='%1.2f%%')
        plt.title(f"{helper.remove_underline_and_capitalise(qe_type)}")
        plt.savefig(f'{path}{qe_type}.png')
        plt.show()

def generate_latex_table(df):
    pass