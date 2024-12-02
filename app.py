from flask import Flask, render_template, request, abort
import os

app = Flask(__name__)

DAILY_UT_COVERAGE_DIR = 'daily-ut-coverage'
UI_TEST_COVERAGE_DIR = 'UItest-coverage'

def build_sidebar(current_path):
    # Remove trailing slash for consistency
    current_path = current_path.rstrip('/')
    
    sidebar = [
        {
            'label': 'trend',
            'url': '#',
            'children': [],
            'active': False
        },
        {
            'label': 'uitest',
            'url': '#',
            'children': [],
            'active': False
        },
        {
            'label': 'daily-ut',
            'url': '#',
            'children': [],
            'active': False
        }
    ]
    
    # Populate uitest children
    uitest_dir = UI_TEST_COVERAGE_DIR
    for dir_name in sorted(os.listdir(uitest_dir), reverse=True):
        if os.path.isdir(os.path.join(uitest_dir, dir_name)):
            date_str = '-'.join(dir_name.split('-')[2:5])
            url = f'/uitest/{dir_name}/'.rstrip('/')
            active = current_path == url
            sidebar[1]['children'].append({'label': date_str, 'url': url, 'children': [], 'active': active})
    
    # Populate daily-ut children
    daily_ut_dir = DAILY_UT_COVERAGE_DIR
    dates = set()
    for dir_name in os.listdir(daily_ut_dir):
        if os.path.isdir(os.path.join(daily_ut_dir, dir_name)):
            date_str = '-'.join(dir_name.split('-')[3:])
            dates.add(date_str)
    for date in sorted(dates, reverse=True):
        date_item = {
            'label': date,
            'url': '#',
            'children': [],
            'active': False
        }
        for dir_name in os.listdir(daily_ut_dir):
            if os.path.isdir(os.path.join(daily_ut_dir, dir_name)):
                if '-'.join(dir_name.split('-')[3:]) == date:
                    url = f'/daily-ut/{dir_name}/'.rstrip('/')
                    active = current_path == url
                    date_item['children'].append({'label': dir_name, 'url': url, 'children': [], 'active': active})
        # Set date_item active if any of its children is active
        if any(child['active'] for child in date_item['children']):
            date_item['active'] = True
        sidebar[2]['children'].append(date_item)
    
    # Set 'uitest' and 'daily-ut' active if any of their children is active
    if any(child['active'] for child in sidebar[1]['children']):
        sidebar[1]['active'] = True
    if any(child['active'] for child in sidebar[2]['children']):
        sidebar[2]['active'] = True
    
    return sidebar

@app.route('/')
def index():
    sidebar = build_sidebar(request.path)
    return render_template('base.html', sidebar=sidebar, content='', current_path=request.path)

@app.route('/daily-ut/<path:directory_path>/')
def daily_ut(directory_path):
    sidebar = build_sidebar(request.path)
    full_path = os.path.join(DAILY_UT_COVERAGE_DIR, directory_path)
    if not os.path.commonprefix([full_path, DAILY_UT_COVERAGE_DIR]) == DAILY_UT_COVERAGE_DIR:
        abort(404)
    if not os.path.isdir(full_path):
        abort(404)
    index_html_path = os.path.join(full_path, 'index.html')
    if not os.path.exists(index_html_path):
        abort(404)
    with open(index_html_path, 'r') as f:
        content = f.read()
    return render_template('base.html', sidebar=sidebar, content=content, current_path=request.path)

@app.route('/uitest/<path:directory_path>/')
def uitest(directory_path):
    sidebar = build_sidebar(request.path)
    full_path = os.path.join(UI_TEST_COVERAGE_DIR, directory_path)
    if not os.path.commonprefix([full_path, UI_TEST_COVERAGE_DIR]) == UI_TEST_COVERAGE_DIR:
        abort(404)
    if not os.path.isdir(full_path):
        abort(404)
    index_html_path = os.path.join(full_path, 'index.html')
    if not os.path.exists(index_html_path):
        abort(404)
    with open(index_html_path, 'r') as f:
        content = f.read()
    return render_template('base.html', sidebar=sidebar, content=content, current_path=request.path)

if __name__ == '__main__':
    app.run(debug=True)