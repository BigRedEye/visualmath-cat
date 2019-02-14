import json
from bs4 import BeautifulSoup as bs
import image_fetcher

tasks = [
    ({'6.1', }, {'1.1.1', '1.1.3', '2.1.12'}),
    ({'3.1', '6.2',}, {'3.1', '3.2', '3.3', '6.2.1'}),
    ({'4.1', }, {'5.1', '5.5'}),
    ({'5.4', }, {'6.3', }),
    ({'2.1', }, {'2.1', }),
    ({'4.1', '5.2' }, {'5.1.1', '5.1.2', '5.1.3', '5.1.4', '5.5.1', '5.5.2', '5.5.3','.5.5.4', '5.5.5'}),
    ({'3.1', '3.2', '3.3'}, {'4.1', '4.2', '4.3'}),
    ({'4.2', }, {'5.2', '5.3', '5.4', '5.5'}),
    ({'1.1', '1.2', '1.3'}, {'1.1', '1.2', '1.3', '1.4'}),
    ({'6.1', '6.2', '6.3' }, {'2.1', '2.2' }),
    ({'5.1', }, {'2.1', '2.2'}),
    ({'3.2', '3.3',}, {'4.1', '4.2'}),
    ({'2.1', '2.2', '2.3'}, {'2.1', '2.2'}),
    ({'4.2', '4.3', '5.2', '5.3'}, {'5.2', '5.3', '5.4', '5.5', '5.6'}),
    ({'2.3', }, {'2.1', '2.2'}),
    ({'4.1', '5.2', '5.3'}, {'5.1'}),
    ({'6.1', '6.3'}, {'1.1.1', '1.1.3', '2.1.12'}),
    ({'2.1', '2.2', '2.3', '5.1'}, {'2.1', '2.2', '3.2', '3.3'}),
    ({'5.1', '5.3'}, {'1.1', '1.2', '1.3', '1.4'}),
]

probs = [
    93.3,
    95.9,
    87.2,
    87.5,
    93.4,
    78.2,
    47.9,
    52.8,
    89.7,
    66.9,
    61.2,
    44.2,
    28.7,
    9.4,
    12.6,
    3.6,
    2.2,
    1.2,
    2.5,
]

def has_class(tag):
    return tag.has_attr('class')

TASKS = 19
assert(len(probs) == TASKS)
assert(len(tasks) == TASKS)

def main():
    imgs = 0

    with open('tasks.json') as f:
        raw = json.load(f)
    tests = []
    for i in range(raw['taskCount']):
        text = bs(raw['tasks'][i]['taskText'], features="html5lib")
        soup = bs(raw['tasks'][i]['html'], 'html.parser')
        if text.script:
            path = str(text.script.text)
            path = path.replace('"', "'").split("'")
            doc = None
            for token in path:
                if token[:5] == 'docs/':
                    doc = token
                    break
            if doc:
                # print(doc)
                img = soup.new_tag('img', src=f'{imgs}.png', align='ABSMIDDLE', alt='undefined', border=0)
                imgs += 1
                soup.find_all(id='text')[0].script.replace_with(img)
#                image_fetcher.save_image(doc)
        if ('answer' not in raw['tasks'][i]) or (len(raw['tasks'][i]['answer']) == 0):
            continue

        binput = bs('''
            <form action="/tasks" method="post">
                Ответ: <input id="answer_1" name="answer" placeholder="Введите ответ" type="text"/>
                <input type="submit" value="Submit">
            </form>
        ''', features="html5lib")
        res = soup.find_all(id='answer_1')
        if len(res):
            res[0].replace_with(binput)
        pretty = soup.prettify()
        with open(f'tasks/{i}.html', 'w') as f:
            f.write(pretty)

        raw['tasks'][i]['html'] = pretty
        themeNames = set()
        requirementNames = set()
        avail = [True for q in range(TASKS)]
        for s in raw['tasks'][i]['themeNames']:
            themeNames.add(s.split(' ')[0])
        for s in raw['tasks'][i]['requirementNames']:
            requirementNames.add(s.split(' ')[0])
        for theme in themeNames:
            for j in range(TASKS):
                if theme not in tasks[j][1]:
                    avail[j] = False
        for theme in requirementNames:
            for j in range(TASKS):
                if theme not in tasks[j][0]:
                    avail[j] = False
        first = -1
        for qq in range(TASKS):
            if avail[qq]:
                if first == -1:
                    first = qq
                else:
                    first = -2
        if first >= 0:
            raw['tasks'][i]['taskId'] = first
            raw['tasks'][i]['solved'] = probs[first]
            tests.append(raw['tasks'][i])
            
    with open('fixed.json', 'w') as f:
        f.write(json.dumps(raw, indent=4))

    with open('nice.json', 'w') as f:
        f.write(json.dumps(tests, indent=4))

if __name__ == '__main__':
    main()
