import spacy

from typing import List

nlp = spacy.load("en_core_web_sm")


def formulate_yes_no_question(subject, predicate, object,
                              time, time_until=None,
                              *, is_given_time_correct=True,
                              predicate_question_dict=None,
                              count_of_falsy_year_question=None,
                              produce_all_interval_questions=False,
                              time_indication=True,
                              lemma=True) -> List[tuple]:
    """
        Generates Yes No Question based on temporal RDFs.

        As an example:
        - Obama, president of, USA, 2009 -> Was Obama president of USA in 2009?

        Template forms are:
        - Did {subject} {predicate} {object} in {time}?
        - Was {subject} {predicate} {object} in {time}?
        - Custom

        :param subject: Subject of the RDF
        :param predicate: Predicate of the RDF
        :param object: Object of the RDF
        :param time: timestamp of the RDF fact
        :param time_until: Until timestamp for generating interval questions
        :param is_given_time_correct: True returns a 'yes' and False returns a 'no' in the Tuple
        :param predicate_question_dict: Optional dict if some predicates deliver a not valid Question.
        Ensures that customised templates can be added.
        Such as 'was born in': 'Was {} born in {} in {}?' for 'was born in'
        :param interval_is_active: if false the generation of many Yes No Questions based on the interval is suppressed
        :param count_of_falsy_year_question: if a number is provided questions exceeding the boundaries of the interval
        + and - in both directions are appended with an 'no' as second tuple entry
        :param time_indication: adds a year indication to the question
        :param produce_all_interval_questions: if True also all interval questions
        :param lemma: If True predicate gets lemmatized

        :return: A list of tuples containing the Yes No Question and its Answer
    """

    time, time_until, interval_given = check_time(time, time_until)

    # initiates yes_no to indicate if the generated questions are correct or incorrect
    if is_given_time_correct:
        yes_no = 'yes'
    else:
        yes_no = 'no'

    # checks if the given predicate has an entry in predicate_question_dict
    if predicate_question_dict:
        if predicate in predicate_question_dict.keys():
            custom_template = predicate_question_dict[predicate]
            temps = generate_yes_no_interval_questions(subject, object, time, time_until, custom_template, yes_no,
                                                       produce_all_interval_questions=produce_all_interval_questions,
                                                       n_falsy_years=count_of_falsy_year_question)
            return temps

    # Lemma predicate and removes be or have if it is the first value.
    processed_predicate, first_word_is_be, first_word_is_have = lemma_predicate(predicate, lemma)

    if first_word_is_be:
        first_part_question = 'Was {} {} {}'
    else:
        first_part_question = 'Did {} {} {}'

    if time_indication:
        second_part_question = 'in the year {}?'
    else:
        second_part_question = 'in {}?'

    template_patches = [first_part_question, second_part_question]

    template = ' '.join([value for value in template_patches])

    temps = generate_yes_no_interval_questions(subject, object, time, time_until, template, yes_no,
                                               predicate=processed_predicate,
                                               produce_all_interval_questions=produce_all_interval_questions,
                                               n_falsy_years=count_of_falsy_year_question)
    return temps


def generate_yes_no_interval_questions(subject, object,
                                       time, time_until,
                                       template, yes_no,
                                       *, predicate=None,
                                       n_falsy_years=None,
                                       produce_all_interval_questions=False):
    """
    Helper function for formulate_yes_no_question
    """
    temps = []

    start_year = time
    end_year = time_until
    falsy_years = []
    if not produce_all_interval_questions:
        start_year = time
        end_year = time

    if n_falsy_years:
        falsy_years = [*get_interval(start_year - n_falsy_years, start_year - 1),
                       *get_interval(end_year + 1, end_year + n_falsy_years)]

    years = [*falsy_years, *get_interval(start_year, end_year)]
    for year in years:
        temp_yes_no = yes_no
        if year in falsy_years:
            temp_yes_no = 'no'

        if predicate:
            temps.append((template.format(subject, predicate, object, str(year)), temp_yes_no))
        else:
            temps.append((template.format(subject, object, str(year)), temp_yes_no))
    return temps


def formulate_simple_when_question(subject, predicate, object,
                                   time, time_until=None,
                                   *, predicate_question_dict=None,
                                   lemma=True, time_indication=True) -> List[tuple]:
    """
    Generates Simple When Question based on temporal RDFs.

        As an example:
        - Obama, president of, USA, 2009 -> When was Obama president of USA?

        Template forms are:
        - When did {subject} {predicate} {object}?
        - When was {subject} {predicate} {object}?
        - Custom

    :param subject: Subject of the RDF
    :param predicate: Predicate of the RDF
    :param object: Object of the RDF
    :param time: timestamp of the RDF fact
    :param time_until: Until timestamp for generating interval answers
    :param predicate_question_dict: Optional dict if some predicates deliver a not valid Question.
    Ensures that customised templates can be added.
    Such as 'When was {} born in {}?' for 'was born in'
    :param lemma: If True predicate gets lemmatized
    :param time_indication: adds a year indication to the question

    :return: Tuple of question and a list of correct year answers
    """
    temps = []

    time, time_until, interval_given = check_time(time, time_until)

    if interval_given:
        answer = get_interval(time, time_until)
    else:
        answer = [time]

    # checks if the given predicate has an entry in predicate_question_dict
    if predicate_question_dict:
        if predicate in predicate_question_dict.keys():
            temps.append((predicate_question_dict[predicate].format(subject, object), answer))
            return temps

    processed_predicate, first_word_is_be, first_word_is_have = lemma_predicate(predicate, lemma)

    first_part_question = ['In which year', 'When']
    if time_indication:
        first_part_question = first_part_question[0]
    else:
        first_part_question = first_part_question[1]

    if first_word_is_be:
        second_part_question = f'was {subject} {processed_predicate} {object}?'
    else:
        second_part_question = f'did {subject} {processed_predicate} {object}?'

    return append_templates(first_part_question, second_part_question, answer, temps)


def formulate_when_to_when_question(subject, predicate, object,
                                    time, time_until=None,
                                    *, predicate_question_dict=None,
                                    time_indication=True,
                                    lemma=True):
    """
    Generates When to When Question based on temporal RDFs.

        As an example:
        - Obama, president of, USA, 2009 -> From when until when was Obama president of USA?

        Template forms are:
        - From when until when was {subject} {predicate} {object}?
        - From when to when was {subject} {predicate} {object}?
        - From when until when did {subject} {predicate} {object}?
        - From when to when did {subject} {predicate} {object}?
        - Custom

    NOTE: If time and time_until have the same year then the question is skipped and a None is returned


    :param subject: Subject of the RDF
    :param predicate: Predicate of the RDF
    :param object: Object of the RDF
    :param time: from timestamp of the RDF fact
    :param time_until: until timestamp for generating interval answers
    :param predicate_question_dict: Optional dict if some predicates deliver a not valid Question.
    Ensures that customised templates can be added.
    Such as 'From when until when was {} born in {}?' for 'was born in'
    :param time_indication: adds a year indication to the question
    :param lemma: If True predicate gets lemmatized

    :return: Tuple of question and a list of correct year answers
    """
    temps = []

    time, time_until, interval_given = check_time(time, time_until)

    if not interval_given:
        return None

    answer = get_interval(time, time_until)

    # checks if the given predicate has an entry in predicate_question_dict
    if predicate_question_dict:
        if predicate in predicate_question_dict.keys():
            temps.append((predicate_question_dict[predicate].format(subject, object), answer))
            return temps

    processed_predicate, first_word_is_be, first_word_is_have = lemma_predicate(predicate, lemma)

    first_part_question = ['From which year until which year', 'From when to when']
    if time_indication:
        first_part_question = first_part_question[0]
    else:
        first_part_question = first_part_question[1]

    if first_word_is_be:
        second_part_question = f'was {subject} {processed_predicate} {object}?'
    else:
        second_part_question = f'did {subject} {processed_predicate} {object}?'

    return append_templates(first_part_question, second_part_question, answer, temps)


def formulate_from_or_until_question(subject, predicate, object,
                                     time, time_until, is_from_question=True,
                                     *, predicate_question_dict=None,
                                     time_indication=True,
                                     lemma=True):
    """
    Generates From when or Until when Question based on temporal RDFs.

        As an example:
        - Obama, president of, USA, 2009
        is_from_question=True -> From which year on was Obama president of USA?
        is_from_question=False -> Until when was Obama president of USA?


        Template forms for is_from_question=True are:
        - From which year on was {subject} {processed_predicate} {object}
        - When was {subject} {processed_predicate} {object} the first time?
        - From which year on did {subject} {processed_predicate} {object}?
        - When did {subject} {processed_predicate} {object} the first time?
        - Custom
        Template forms for is_from_question=False are:
        - Until when was {subject} {processed_predicate} {object}?
        - When was {subject} {processed_predicate} {object} the last time?
        - Until when did {subject} {processed_predicate} {object}?
        - When did {subject} {processed_predicate} {object} the last time?
        - Custom

    NOTE: If time and time_until have the same year then the question is skipped and a None is returned

    :param subject: Subject of the RDF
    :param predicate: Predicate of the RDF
    :param object: Object of the RDF
    :param time: from timestamp of the RDF fact
    :param time_until: until timestamp for generating interval answers
    :param is_from_question: indicates if either a from or a until question is generated
    :param predicate_question_dict: Optional dict if some predicates deliver a not valid Question.
    Ensures that customised templates can be added.
    Such as '{}was married to {} but when was their marriage?' for 'is married to'
    :param time_indication: adds a year indication to the question
    :param lemma: If True predicate gets lemmatized

    :return: Tuple of question and the answer whereby the answer is either time or time_until based on is_from_question
    """
    temps = []

    time, time_until, interval_given = check_time(time, time_until)

    if not interval_given:
        return None

    if is_from_question:
        answer = time
    else:
        answer = time_until

    # checks if the given predicate has an entry in predicate_question_dict
    if predicate_question_dict:
        if predicate in predicate_question_dict.keys():
            temps.append((predicate_question_dict[predicate].format(subject, object), time))
            return temps

    processed_predicate, first_word_is_be, first_word_is_have = lemma_predicate(predicate, lemma)

    if is_from_question:
        first_part_question = ['From which year', 'Since when']
    else:
        first_part_question = ['Until which year', 'Until when']

    if time_indication:
        first_part_question = first_part_question[0]
    else:
        first_part_question = first_part_question[1]

    if first_word_is_be:
        second_part_question = f'was {subject} {processed_predicate} {object}?'
    else:
        second_part_question = f'did {subject} {processed_predicate} {object}?'

    return append_templates(first_part_question, second_part_question, answer, temps)


def formulate_left_or_right_open_interval_questions(subject, predicate, object, time_from, time_until,
                                                    right_open=True,
                                                    *, predicate_question_dict=None,
                                                    time_indication=True,
                                                    lemma=True):
    """
    Generates Left or Right open Question based on temporal RDFs.

        As an example:
        - Obama, president of, USA, 2009
        right_open=True -> From 2009 until when was Obama president of USA??
        right_open=False -> From when until 2017 was Obama president of USA?


        Template forms for right_open=True are:
        - From {time_from} until when was {subject} {processed_predicate} {object}?
        - From {time_from} until when did {subject} {processed_predicate} {object}?
        - Custom
        Template forms for right_open=False are:
        - From when until {time_until} was {subject} {processed_predicate} {object}?
        - From when until {time_until} did {subject} {processed_predicate} {object}?
        - Custom

    :param subject: Subject of the RDF
    :param predicate: Predicate of the RDF
    :param object: Object of the RDF
    :param time_from: from timestamp of the RDF fact
    :param time_until: until timestamp for generating interval answers
    :param right_open: indicate if a left or a right open question should be generated
    :param predicate_question_dict: Optional dict if some predicates deliver a not valid Question.
    Ensures that customised templates can be added.
    Such as 'was president of': 'Until the year {} {} was president of {} and when was the election?
    CAUTION the first {} has to indicate the year.
    :param time_indication: adds a year indication to the question
    :param lemma: If True predicate gets lemmatized

    :return: A list of Tuples of question and answer
    whereby the answer is either time_start or time_until based on right_open
    """
    temps = []
    time_from, time_until, interval_given = check_time(time_from, time_until)

    if not interval_given:
        return None

    # checks if the given predicate has an entry in predicate_question_dict
    if predicate_question_dict:
        if predicate in predicate_question_dict.keys():
            if right_open:
                time_template = time_until
                time_answer = time_from
            else:
                time_template = time_from
                time_answer = time_until
            temps.append((predicate_question_dict[predicate].format(time_template, subject, object), time_answer))
            return temps

    processed_predicate, first_word_is_be, first_word_is_have = lemma_predicate(predicate, lemma)

    if right_open:
        first_part_question = [f'From the year {time_from} until which year',
                               f'From {time_from} until when ']
        answer = time_until
    else:
        first_part_question = [f'From which year until the year {time_until}',
                               f'From when until {time_until}']
        answer = time_from

    if time_indication:
        first_part_question = first_part_question[0]
    else:
        first_part_question = first_part_question[1]

    if first_word_is_be:
        second_part_question = f'was {subject} {processed_predicate} {object}?'
    else:
        second_part_question = f'did {subject} {processed_predicate} {object}?'

    return append_templates(first_part_question, second_part_question, answer, temps)


def formulate_duration_question(subject, predicate, object,
                                time_from, time_until,
                                *, predicate_question_dict=None,
                                time_indication=True,
                                lemma=True):

    temps = []
    time_from, time_until, interval_given = check_time(time_from, time_until)

    if not interval_given:
        return None
    interval = get_interval(time_from, time_until)
    answer = interval[len(interval) - 1] - interval[0]

    # checks if the given predicate has an entry in predicate_question_dict
    if predicate_question_dict:
        if predicate in predicate_question_dict.keys():
            temps.append((predicate_question_dict[predicate].format(subject, object), answer))
            return temps

    processed_predicate, first_word_is_be, first_word_is_have = lemma_predicate(predicate, lemma)

    if first_word_is_be:
        first_part_question = ['For how many years was', 'For how long was']
    else:
        first_part_question = ['For how many years did', 'For how long did']

    if time_indication:
        first_part_question = first_part_question[0]
    else:
        first_part_question = first_part_question[1]

    second_part_question = f'{subject} {processed_predicate} {object}?'

    return append_templates(first_part_question, second_part_question, answer, temps)


def formulate_before_after_question(subject1, predicate1, object1, time1, time_until1,
                                    subject2, predicate2, object2, time2, time_until2,
                                    before=True):
    pass


def formulate_while_question(subject1, predicate1, object1,
                             subject2, predicate2, object2):
    pass


####################### Helper Functions #######################

def process_predicate(predicate, pos=True):
    predicate = predicate.lower()
    doc = nlp(predicate)
    return_string = ''

    for token in doc:
        if pos:
            return_string = return_string + ' ' + token.pos_
        else:
            return_string = return_string + ' ' + token.tag_
    return return_string


def elaborate_spacy_pos(predicate):
    print(f'{predicate} -> {process_predicate(predicate)}')
    print(f'{predicate} -> {process_predicate(predicate, False)}')


def lemma_predicate(predicate, lemma=True):
    """
    Converts a predicate into its lemma form and removes leading be and have.

    Examples:
        - is affiliated to  -> affiliate to
        - has won prize     -> win prize
        - graduated from    -> graduate from

    :param lemma: toggles if words get lemmatized
    :param predicate: Predicate of the RDF
    :return: lemma form of the given predicate, bool first_word_is_be, bool first_word_is_have
    """
    doc = nlp(predicate)

    first_word_is_be = doc[0].lemma_ == 'be'
    first_word_is_have = doc[0].lemma_ == 'have'

    if lemma and not first_word_is_be:
        token = [token.lemma_ for token in doc]
    else:
        token = [str(token.text) for token in doc]

    if first_word_is_be or first_word_is_have:
        token = token[1:]

    resulted_predicate = ' '.join(token)
    return resulted_predicate, first_word_is_be, first_word_is_have


def lemma_predicate_new(predicate):
    """
    Converts a predicate into its lemma form and removes leading be and have.

    Examples:
        - is affiliated to  -> affiliate to
        - has won prize     -> win prize
        - graduated from    -> graduate from

    :param predicate: Predicate of the RDF
    :return: lemma form of the given predicate, bool first_word_is_be, bool first_word_is_have
    """
    predicate = predicate.lower()
    doc = nlp(predicate)

    pos = [token.pos_ for token in doc]
    token = [token.lemma_.lower() for token in doc]

    first_word_is_be = token[0] == 'be'
    first_word_is_have = token[0] == 'have'

    # token = [token.text for token in doc]

    first_word_is_verb = pos[0] == 'ADJ'

    if first_word_is_be or first_word_is_have:
        token = token[1:]

    resulted_predicate = ' '.join(token)
    return resulted_predicate, first_word_is_be, first_word_is_have, first_word_is_verb


def get_interval(time: int, time_until: int):
    return [*range(time, time_until + 1, 1)]


def parse_year(year) -> int:
    """
    Checks if the input is a valid year only consisting of digits and max length of 4.

    :param year: temporal RDF value that should be a year
    :return: year as a string
    :raises:
        ValueError: Has more than 4 figures or is not castable to an int.
    """
    if isinstance(year, int):
        year = str(year)

    if len(year) <= 4:
        # conversion also checks if the string does only contain digits
        return int(year)
    else:
        raise ValueError('Not a valid year. Max length of 4 is allowed.')


def check_time(time, time_until):
    interval_given = False

    time = parse_year(time)

    if not time_until:
        time_until = time
    else:
        time_until = parse_year(time_until)

    # If the time is smaller than time_until the variables are exchanged
    if time != time_until:
        if time > time_until:
            helper_time = time
            time = time_until
            time_until = helper_time
        interval_given = True

    return time, time_until, interval_given


def append_templates(first_part_question, second_part_question, answer, temps):
    if isinstance(first_part_question, str):
        temps.append((' '.join([value for value in [first_part_question, second_part_question]]), answer))
        return temps

    for entry in first_part_question:
        if isinstance(entry, str):
            temps.append((' '.join([value for value in [entry, second_part_question]]), answer))
        elif len(entry) == 1:
            temps.append((' '.join([value for value in [entry[0], second_part_question]]), answer))
        elif len(entry) == 2:
            head = entry[0]
            tail = entry[1]
            # remove question mark
            body = second_part_question[:len(second_part_question) - 1]
            temps.append((' '.join([value for value in [head, body, tail]]), answer))
        else:
            raise ValueError('Within the first_part_question are only nested lists allowed af max length 2')

    return temps
