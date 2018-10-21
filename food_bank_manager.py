from collections import defaultdict as dd
import datetime, requests, io, math
from urllib import parse
import pandas as pd
from bs4 import BeautifulSoup as bs
import re
import calendar

grocies = ['safeway', 'cvs', 'el super', "fry's", 'frys', 'market', 'foods', 'walmart', 'target', 
           'coffeehouse', 'starbucks', 'bashas', 'winco','grubstak']
churches = ['st. matthew', 'church', 'episcopal','jewish','father robert berra']
organizations = ['dental', 'health', 'school', 'realty', 'farm', 'group', 'usps', 'kids', 'children', 
                 'polytechnic', 'academy', 'llc', 'services', 'promotions', 'hoa','medical','festival',
                 'curves','institute','bank','therapeutics','college','girl scout','intel team',
                 'boy scouts','cub scouts','troop','elementary','commerce','community','urgent care',
                 'center','yoga','club','shop','maintenance','fans across america','corp.','eyewear',
                 'edward jones','suites','builders','society','association','accounting','professionals',
                 'control','apartments','doctor','neighborhood','camp','intel','legion','team'
                ]
with open('fbm.config','r') as file:
    config = {i.split('=')[0]:i.split('=')[1] for i in file.readlines()}

auth = (config['username'],config['password'])


def get_request_parms(options_map, **args):
    try:
        start_date = args['start_date']
        end_date = args['end_date']
    except:
        raise Exception('Must include start and end dates.')
    try:
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except:
        raise Exception('Dates must be in YYYY-MM-DD format')
    
    # Create the base form parameters
    parameters = {
        'blockCount': '3',
        # Filter options
        # TODO - make filters options and dynamically added
        # - for now, it is the donated on start and end date 
        'conditions[1][action]': 'dgte',
        'conditions[1][blockType]': 'item',
        'conditions[1][field]': 'donations.donation_at',
        'conditions[1][id]': '1',
        'conditions[1][parent]': '',
        'conditions[1][value]': '', #start_date
        'conditions[2][action]': 'dlte',
        'conditions[2][blockType]': 'item',
        'conditions[2][field]': 'donations.donation_at',
        'conditions[2][id]': '2',
        'conditions[2][parent]': '',
        'conditions[2][value]': '', #end_date
        'conditions[type]': 'And',
        # Other options
        'donation_type': '1',
        'fileName': ''
    }
    
    # update the parameters
    update_parms = {}
    for k,v in args.items():
        key = options_map[k]
        if v and 'donation' in k or 'donor' in k: 
            v = '1'
        update_parms[key] = v
    
    parameters.update(update_parms)
    
    return parse.urlencode(parameters)



def get_csv_data(search_args):
    global auth
    with requests.Session() as s:
        ''' - TODO - make it optional '''
        # get cookies for Food Back Manager
        s.get('https://mcfb.soxbox.co/login/')
        s.headers.update(
            {
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding':'gzip, deflate, br',
            'accept-language':'en-US,en;q=0.9',
            'cache-control':'max-age=0',
            'content-length':'58',
            'content-type':'application/x-www-form-urlencoded',
            'origin':'https://mcfb.soxbox.co',
            'referer': 'https://mcfb.soxbox.co/login/',
            'upgrade-insecure-requests':'1',
            'user-agent':'Mozilla/5.0 Bot'
            }
        )
        user,passw = auth

        # log into Food Bank Manager
        s.post('https://mcfb.soxbox.co/login/',data=f'username={user}&password={passw}&location=1&action=Login')
        del s.headers['content-length']

        # load the page before requesting csv
        # TODO - get the presaved reports
        donations_response = s.get('https://mcfb.soxbox.co/reports/donor/donations/')
        soup = bs(donations_response.content, 'lxml')
        inputs = soup.find_all('input',type='checkbox')

        # create the options_map to map input arguments to
        global options_map
        options_map = {}
        for i in inputs:
            section = i.find_parent('fieldset').legend.text.split(' ')[0]
            key = re.sub(r'[^A-z0-9]+',' ',i.parent.text).strip()
            key = section+'_'+key.replace(' ','_')
            key = key.lower()
            options_map[key] = i['name']
        options_map['start_date'] = 'conditions[1][value]'
        options_map['end_date'] = 'conditions[2][value]'

        # requesting csv
        s.headers.update({'referer':'https://mcfb.soxbox.co/reports/donor/donations/?template=3'})
        payload = get_request_parms(options_map, **search_args)
        r = s.post('https://mcfb.soxbox.co/reports/donor/donations/csv/',
                   data = payload)
    return r.text

def write_csv(text, filename):
    ''' This function creates a csv file for the  '''
    with open(filename, 'w') as file:
        file.write(text)

def convert_csv_to_dataframe(text):
    csv_io = io.StringIO()
    csv_io.write(text)
    csv_io.seek(0)
    df = pd.read_csv(csv_io)
    return df

def convert_to_json(text, transpose = False):
    df = convert_csv_to_dataframe(text)
    if transpose:
        return df.T.to_dict()
    return df.to_dict()

def food_donations_by_month(year, month, search_args=None):
    assert isinstance(year, int), 'The given year must be an integer'
    assert isinstance(month, int), 'The given month must be an integer'
    this_year = datetime.datetime.now().year
    assert year>2000, 'The given year must be greater than 2000'
    assert year <= this_year, 'The given year must be less than or equal to {}'.format(this_year)
    this_month = datetime.datetime.now().month
    assert month>=1, 'The given year must be greater than or equal to 1'
    assert year!=this_year or month<=this_month, 'The given year must be less than or equal to {}'.format(this_year)
    days = calendar.monthrange(year,month)[1]
    if not search_args:
        search_args = { 'donor_donor_id': '1',
                    'donor_company_organization_name': '1',
                    'donor_first_name': '1',
                    'donor_middle_name': '1',
                    'donor_last_name': '1',
                    'donor_email_address': '1',
                    'donor_street_address': '1',
                    'donor_state_province': '1',
                    'donor_zip_postal_code': '1',
                    'donation_donated_on': '1',
                    'donation_donation_type': '1',
                    'donation_food_item_category': '1',
                    'donation_name_of_food_item': '1',
                    'donation_quantity': '1',
                    'donation_quantity_type': '1',
                    'donation_source_of_donation': '1',
                    'donation_value_approximate': '1',
                    'donation_weight_lbs': '1',
                    'donor_apartment': '1',
                    'donor_city_town': '1',
                    'donor_donor_type': '1',
                    'donor_salutation_greeting_dear_so_and_so': '1',
                    'donor_spouse_name_first_last': '1',
                    'donation_memo': '1',
                    'end_date': '{}-{}-{}'.format(year, month, days),
                    'start_date': '{}-{}-01'.format(year, month)}
    
    return get_csv_data(search_args)



def get_info(df, **args):
    pass

def find_umatched(df):
    return df.loc[df['Source Type'].isnull()]

def map_organization_source_type(month_data_df, organizations_csv_filename='organizations.csv'):
    organizations_df = pd.read_csv(organizations_csv_filename)
    df = month_data_df.copy()
    df = df.join(organizations_df.set_index('Company / Organization Name'), 
                 on='Company / Organization Name')
    for i,row in df.iterrows():
        # if there is no source type
        if isinstance(row['Source Type'], float) and math.isnan(row['Source Type']):
            
            # if there isn't a company name
            if isinstance(row['Company / Organization Name'], float):
                # assume the entrie is from an Individual Donor
                df.loc[i,'Source Type'] = 'Individual Donor'
                continue
            
            if any(i in row['Company / Organization Name'].lower() for i in grocies):
                df.loc[i,'Source Type'] = 'Grocery'
            elif any(i in row['Company / Organization Name'].lower() for i in churches):
                df.loc[i,'Source Type'] = 'Church'
            elif any(i in row['Company / Organization Name'].lower() for i in organizations):
                df.loc[i,'Source Type'] = 'Organization'
            
    return df

def summary_dict(df, _type = 'Source Type', _sum = 'Weight (lbs)'):
    d = {}
    for typ in set(df[_type]):
        d[typ] = sum(df[df[_type]==typ][_sum])
    return d


def daily_total(df):
    d = dd(float)
    for i,row in df.iterrows():
        d[row['Donated On']]+=row['Weight (lbs)']
    return d

def summary_csv(data, month_name, starting_inv = 0, ending_inv=0, volunteer_hours=0,
               num_clients = 0, new_clients=0, total_served=0):
    result = 'Inventory {},Weight (lbs)\n'.format(month_name)
    sub_total = 0
    for k,v in data.items():
        if k!='Waste':
            result += '{},{}\n'.format(k,v)
            sub_total+=v
    result += 'Subtotal,{}\n'.format(sub_total)
    waste = data.get('Waste',0)
    result += 'Waste,{}\n'.format(waste)
    total = sub_total-waste
    result += 'Total,{}\n,\n,\n'.format(total)
    result += 'Starting Inventory,{}\n'.format(starting_inv)
    result += 'Ending Inventory,{}\n,\n'.format(ending_inv)
    result += 'Amount distributed,{}\n,\n,\n'.format(total-ending_inv+starting_inv)
    result += 'Volunteer hours,{}\n,\n'.format(volunteer_hours)
    result += 'Number of clients,{}\n'.format(num_clients)
    result += 'Number of new clients,{}\n'.format(new_clients)
    result += 'Total served,{}\n'.format(total_served)
    
    return result

def get_month_mapped(year, month, 
                     organizations_csv_filename='organizations.csv'):
    data = food_donations_by_month(year, month)
    month_data_df = convert_csv_to_dataframe(data)
    return map_organization_source_type(month_data_df, 
                                        organizations_df, 
                                        organizations_csv_filename)
    
def get_sumamry(df, year, month, starting_inv = 0, ending_inv=0,
                volunteer_hours=0, num_clients = 0, new_clients=0, total_served=0):

    # Located unmapped entries
    missing = find_umatched(df)
    if len(missing):
        print('The following Donation Ids are missing source type:')
        for i,row in missing.iterrows():
            print(row['Donation ID'], row['Company / Organization Name'])
    
    # process data as csv
    month_name = datetime.datetime(year=year, month=month, day=1).strftime("%b")
    summary = summary_dict(df, _type = 'Source Type', _sum = 'Weight (lbs)')
    summary = summary_csv(summary, month_name, starting_inv)
    return summary
    

today = datetime.date.today()
first = today.replace(day=1)
lastMonth = first - datetime.timedelta(days=1)
year = int(lastMonth.strftime("%Y"))
month = int(lastMonth.strftime("%m"))

# Get the data
csv_text = food_donations_by_month(year, month)

# Map organziations to their organization type
month_data_df = convert_csv_to_dataframe(csv_text)
df = map_organization_source_type(month_data_df)


summary = get_sumamry(df, year, month)


