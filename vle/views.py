import operator

from django.template.loader import get_template
from django.template import RequestContext
from django.http import HttpResponse

from models import SimpleFluids
from common.settings import STATIC_URL, SITE_URL

#######################################################################################
# Common Functionality
#######################################################################################

def parse_request(request):
    result = {
        'site_url' : SITE_URL,
        'static_url': STATIC_URL
    }

    if request.method == 'POST':
        keys = ['selected_tests', 'selected_order', 'current_state', 'current_answers']
        for key in keys:
            if (request.POST.has_key(key)):
                result[key] = request.POST[key]


    return result

def tests_description():

    seconds_per_symbol = 1
    seconds_per_question = 10

    descriptions = Description.objects.all()
    tests = []
    id = 0
    for description in descriptions:
        time_on_read = seconds_per_symbol * description.symbols
        time_on_think = seconds_per_question * description.questions
        time = operator.div(time_on_read + time_on_think + 50, 60)
        russian_name = description.rname
        english_name = description.name

        tests.append({
            'time': time,
            'rname': russian_name,
            'ename': english_name,
            'id': id})

        id = id + 1

    return tests

def test_questions(test_name):

    db = 0

    if test_name == 'politics':
        db = Politics
    elif test_name == 'religion':
        db = Religion
    elif test_name == 'sex':
        db = Sex
    elif test_name == 'household':
        db = Household

    dbquestions = db.objects.all()
    questions = []

    id = 0
    for question in dbquestions:
        questions.append({
            'id' : id,
            'text' : question.question,
            'weight' : question.weight
        })

        id = id + 1

    return questions


#######################################################################################
# Begin Stuff
#######################################################################################

def process_beg(request):
    dict = parse_request(request)

    selected_tests = '' if not dict.has_key('selected_tests') else dict['selected_tests']

    template = ''
    if selected_tests == '':
        dict['tests'] = tests_description()
        template = 'welcome.html'
    else:
        template = 'beg_order.html'

    t = get_template(template)
    c = RequestContext(request, dict)

    return HttpResponse(t.render(c))


#######################################################################################
# Tests Execution Stuff
#######################################################################################

SESSION_START = 1
TEST_START = 2
RESULTS = 3

def go_subprocess(dict):
    number_of_tests = dict['selected_tests'].count('_') + 1
    states = dict['current_state'].split('_')

    current_session = -1 if states[0] == '' else int(states[0])
    current_test = -1 if len(states) <= 1 else int(states[1])

    if current_session == 2 and current_test == number_of_tests:
        return RESULTS

    # right after beg/
    if current_session == -1 and current_test == -1:
        return SESSION_START

    if current_test == number_of_tests:
        return SESSION_START

    return TEST_START

def go_session(dict):
    states = dict['current_state'].split('_')
    current_session = 0 if len(states[0]) == 0 else int(states[0]) + 1
    dict['current_state'] = str(current_session)

    co = dict['selected_order']

    pictures = ['user_m.png', 'user_w.png', 'user_mw.png']
    if co == 'wm':
        pictures[0], pictures[1] = pictures[1], pictures[0]

    dict['user_picture'] = pictures[current_session]

    return dict

def russian_name(ename):
    test = Description.objects.get(name=ename)
    return test.rname

def go_test(dict):
    test_names = dict['selected_tests'].split('_')
    states = dict['current_state'].split('_')
    current_test = int(states[1])

    current_name = test_names[current_test]

    dict['questions'] = test_questions(current_name)
    dict['test_name'] = russian_name(current_name)
    dict['number_of_questions'] = len(dict['questions'])

    return dict

def get_percent(man_answer, woman_answer, pair_answer):
    """Compute man share for given answers."""
    if (man_answer == woman_answer):
        return 50.0

    mi = min(man_answer, woman_answer)
    ma = max(man_answer, woman_answer)

    pair_answer = min(ma, pair_answer)
    pair_answer = max(mi, pair_answer)

    d2 = man_answer - woman_answer
    d12 = pair_answer - woman_answer

    return 100.0 * d12 / d2


def go_results(dict):
    test_names = dict['selected_tests'].split('_')
    answers = dict['current_answers']
    sl = len(answers) / 3 # session length

    test_results = []

    shift = 0
    for test_name in test_names:
        questions = test_questions(test_name)
        total_weight = 0
        total_percent = 0 # percent gained by man
        for question in questions:
            a_m = int(answers[shift])
            a_w = int(answers[shift + sl])
            a_mw = int(answers[shift + 2 * sl])
            shift += 1
            w = question['weight']
            total_weight += w
            total_percent += get_percent(a_m, a_w, a_mw) * w

        mean_percent = total_percent / total_weight

        if (dict['selected_order'] == 'wm'):
            mean_percent = 100.0 - mean_percent

        man_percent = int(mean_percent)
        man_percent = min(99, man_percent)
        man_percent = max(1, man_percent)
        woman_percent = 100 - man_percent

        test_results.append({
            'm' : man_percent,
            'w' : woman_percent,
            'name' : russian_name(test_name)
        })

    dict['tests_results'] = test_results

    return dict


def process_go(request):
    dict = parse_request(request)

    template = ''
    subprocess = go_subprocess(dict)

    if subprocess == SESSION_START:
        dict = go_session(dict)
        template = 'go_session.html'
    elif subprocess == TEST_START:
        dict = go_test(dict)
        template = 'go_test.html'
    else: # RESULTS
        dict = go_results(dict)
        template = 'go_results.html'

    t = get_template(template)
    c = RequestContext(request, dict)

    return HttpResponse(t.render(c))
