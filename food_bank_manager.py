''' Food Bank Manager Scraper
    by Michael Pedersen

    Food Bank Manager (FBM) is an online platform that allows registering 
    and tracking of food based donations and waste. 

    This program creates functions to allow users to quickly pull reports
    from FBM and analyze them.
'''

from collections import defaultdict as dd
import datetime, requests, io, math
from urllib import parse
import pandas as pd
from bs4 import BeautifulSoup as bs
import re
import calendar

# open config file for username/password of FBM
with open('fbm.config','r') as file:
    config = {i.split('=')[0]:i.split('=')[1] for i in file.readlines()}

# pull FBM authorization from configs
auth = (config['username'],config['password'])

# TODO - move these to a config file
# food bank organziation tags
# Grocery stores might contain the following in their organization name
grocies = ['safeway', 'cvs', 'el super', "fry's", 'frys', 'market', 'foods', 
           'walmart', 'target', 'coffeehouse', 'starbucks', 'bashas', 'winco',
           'grubstak']
# Churched stores might contain the following in their organization name
churches = ['st. matthew', 'church', 'episcopal','jewish','father robert berra']
# Organizations stores might contain the following in their organization name
organizations = ['dental', 'health', 'school', 'realty', 'farm', 'group', 'usps', 
                 'kids', 'children', 'polytechnic', 'academy', 'llc', 'services', 
                 'promotions', 'hoa', 'medical', 'festival', 'curves', 'institute',
                 'bank', 'therapeutics', 'college', 'girl scout', 'intel team',
                 'boy scouts', 'cub scouts', 'troop', 'elementary', 'commerce',
                 'community', 'urgent care', 'center', 'yoga', 'club', 'shop',
                 'maintenance', 'fans across america', 'corp.', 'eyewear',
                 'edward jones', 'suites', 'builders', 'society', 'association',
                 'accounting', 'professionals', 'control', 'apartments', 'doctor',
                 'neighborhood', 'camp', 'intel', 'legion', 'team'
                ]

def write_csv(text, filename):
    ''' This function creates a csv file from given csv data in string form. 
    '''
    with open(filename, 'w') as file:
        file.write(text)

def csv_to_dataframe(text):
    ''' This function converts csv text to a dataframe. 
    '''
    csv_io = io.StringIO()
    csv_io.write(text)
    csv_io.seek(0)
    df = pd.read_csv(csv_io)
    return df

def csv_to_dictionary(text, transpose = False):
    ''' This function creates a dictionaru from csv file.
    '''
    df = csv_to_dataframe(text)
    if transpose:
        return df.T.to_dict()
    return df.to_dict()

def get_team_time_entry_parms():
    return {
        "fileName": "",
        "col[timeTrack.track_hours]": "1",
        "groups[volunteers.id]": "",
        "groups[volunteers.username]": "",
        "groups[volunteers.street_address]": "",
        "groups[volunteers.city]": "",
        "groups[volunteers.state]": "",
        "groups[volunteers.zipcode]": "",
        "groups[volunteers.blackball]": "",
        "col[volunteers.username]": "",
        "col[volunteers.email]": "",
        "col[volunteers.firstname]": "",
        "col[volunteers.lastname]": "",
        "col[volunteers.street_address]": "",
        "col[volunteers.city]": "",
        "col[volunteers.state]": "",
        "col[volunteers.zipcode]": "",
        "col[volunteers.middlename]": "",
        "col[volunteers.apartment]": "",
        "col[volunteers.phone]": "",
        "col[volunteers.workphone]": "",
        "col[volunteers.cellphone]": "",
        "col[volunteers.updated_at]": "",
        "col[volunteers.created_at]": "",
        "col[volunteers.blackball]": "",
        "col[volunteers.dob]": "",
        "conditions[type]": "And",
        "conditions[1][field]": "timeTrack.track_on",
        "conditions[1][action]": "dgte",
        "conditions[1][value]": "2018-08-01",
        "conditions[1][id]": "1",
        "conditions[1][blockType]": "item",
        "conditions[1][parent]": "",
        "conditions[2][field]": "timeTrack.track_on",
        "conditions[2][action]": "dlte",
        "conditions[2][value]": "2018-08-31",
        "conditions[2][id]": "2",
        "conditions[2][blockType]": "item",
        "conditions[2][parent]": "",
        "blockCount": "3"
    }



def get_visit_hist(start_date, end_date):
    pass

def get_default_options_map():
    return {
        "donor_donor_id": "col[donors.id]",
        "donor_donor_is_a_company": "col[donors.donors_965f466338]",
        "donor_company_organization_name": "col[donors.donors_79fe2d07e8]",
        "donor_title_prefix": "col[donors.donors_1f13985a81]",
        "donor_first_name": "col[donors.firstName]",
        "donor_middle_name": "col[donors.middleName]",
        "donor_last_name": "col[donors.lastName]",
        "donor_email_address": "col[donors.donors_e0feeaff84]",
        "donor_suffix": "col[donors.donors_730b308554]",
        "donor_spouse_name_first_last": "col[donors.donors_c42c9d40e7]",
        "donor_salutation_greeting_dear_so_and_so": "col[donors.donors_b4d4452788]",
        "donor_nick_name": "col[donors.donors_32bb7cac8a]",
        "donor_street_address": "col[donors.streetAddress]",
        "donor_apartment": "col[donors.apartment]",
        "donor_city_town": "col[donors.city]",
        "donor_state_province": "col[donors.state]",
        "donor_zip_postal_code": "col[donors.zipCode]",
        "donor_updated_at": "col[donors.updated_at]",
        "donor_created_at": "col[donors.created_at]",
        "donor_primary_phone_number": "col[donors.donors_6213775871]",
        "donor_department": "col[donors.donors_b5b26b9572]",
        "donor_secondary_phone_number": "col[donors.donors_f64c0a6975]",
        "donor_donor_type": "col[donors.donorType_id]",
        "donor_job_title": "col[donors.donors_ca3eab528a]",
        "donation_donation_type": "col[donations.donationType_id]",
        "donation_source_of_donation": "col[donations.donations_1b458b4e6a]",
        "donation_updated_at": "col[donations.updated_at]",
        "donation_created_at": "col[donations.created_at]",
        "donation_donated_on": "col[donations.donation_at]",
        "donation_designated_fund": "col[donations.donations_be547d16da]",
        "donation_tax_deductible_donation": "col[donations.donations_3f9a0026fb]",
        "donation_amount": "col[donations.donations_41420c6893]",
        "donation_check_number": "col[donations.donations_6092e999f4]",
        "donation_credit_card_type": "col[donations.donations_cc3b79a3ac]",
        "donation_soft_donation": "col[donations.donations_c682fe74bc]",
        "donation_soft_donation_donor_name": "col[donations.donations_a7cbfb7452]",
        "donation_batch_id": "col[donations.donations_3abbac390f]",
        "donation_food_item_category": "col[donations.donations_1704817e34]",
        "donation_name_of_food_item": "col[donations.donations_0968598e1b]",
        "donation_clothing_item_category": "col[donations.donations_14cb406f01]",
        "donation_goods_category": "col[donations.donations_6bc08b419a]",
        "donation_quantity": "col[donations.donations_b09ad16128]",
        "donation_quantity_type": "col[donations.donations_6af401c28c]",
        "donation_weight_lbs": "col[donations.donations_f695e975c6]",
        "donation_mileage": "col[donations.donations_14a9bdf34a]",
        "donation_value_approximate": "col[donations.donations_e0a1fae0a3]",
        "donation_gift_card": "col[donations.donations_8aa869cbca]",
        "donation_gift_card_type": "col[donations.donations_25a044ed83]",
        "donation_expiration_date": "col[donations.donations_bda7493c96]",
        "donation_service_performed_by": "col[donations.donations_e0b297f1a2]",
        "donation_service_performed": "col[donations.donations_f8fe28e928]",
        "donation_created_an_asset": "col[donations.donations_15c93726c9]",
        "donation_fair_market_value_of_asset": "col[donations.donations_efb28401ee]",
        "donation_expenses_associated_with_performed_servi": "col[donations.donations_34ed818c47]",
        "donation_fair_market_value_of_performed_services": "col[donations.donations_142c1f8e73]",
        "donation_net_value_of_service": "col[donations.donations_5204fdf0a9]",
        "donation_memo": "col[donations.donations_6058571536]",
        "start_date": "conditions[1][value]",
        "end_date": "conditions[2][value]"
    }

def get_default_search_args():
    ''' This function returns a pre-constructed search query 
        for FBM queries.
    '''
    return { 'donor_donor_id': '1',
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
                    'donation_memo': '1'}

def create_search_args(start_date, end_date):
    ''' 
    '''
    # parse the given start and end date
    if isinstance(start_date,str):
        start = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    elif isinstance(start_date, datetime):
        pass
    else:
        raise Exception('create_search_args: Please give a valid start date.')
    if isinstance(end_date,str):
        end = datetime.datetime.strptime(end_date,'%Y-%m-%d')
    elif isinstance(end_date, datetime):
        pass
    else:
        raise Exception('create_search_args: Please give a valid end date.')

    # get default args and update with start/end dates
    search_args = get_default_search_args()
    search_args.update({ 
        'end_date': '{}-{}-{}'.format(end.year, end.month, end.day),
        'start_date': '{}-{}-{}'.format(start.year, start.month, start.day) })
    return search_args

def create_fbm_querystring(options_map, **args):
    ''' This function creates the url encoded string to post to FBM in order to 
        pull the csv report of given parameters from FBM.
    '''
    try:
        # ensure that a start and end date are given
        start_date = args['start_date']
        end_date = args['end_date']
    except:
        raise Exception('Must include start and end dates.')
    try:
        # ensure that the start and end date are in YYYY-MM-DD form
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except:
        raise Exception('Dates must be in YYYY-MM-DD format')
        
    field = 'donations.donation_at'
    for k,v in options_map.items():
        if 'timeTrack' in v:
            field = 'timeTrack.track_on'
    
    # Create the base form parameters
    parameters = {
        'blockCount': '3',
        # Filter options
        # TODO - make filters options and dynamically added
        # - for now, it is the donated on start and end date 
        'conditions[1][action]': 'dgte',
        'conditions[1][blockType]': 'item',
        'conditions[1][field]': field,
        'conditions[1][id]': '1',
        'conditions[1][parent]': '',
        'conditions[1][value]': '', #start_date
        'conditions[2][action]': 'dlte',
        'conditions[2][blockType]': 'item',
        'conditions[2][field]': field,
        'conditions[2][id]': '2',
        'conditions[2][parent]': '',
        'conditions[2][value]': '', #end_date
        'conditions[type]': 'And',
        # Other options
        'donation_type': '1',
        'fileName': ''
    }
    
    # update the parameters with given arguments
    update_parms = {}
    for k,v in args.items():
        key = options_map[k]
        if v and 'donation' in k or 'donor' in k: 
            v = '1'
        update_parms[key] = v
    parameters.update(update_parms)
    
    # return the url encoded string 
    return parse.urlencode(parameters)


def get_guest_history():
    url = '/reports/guests/visits2/export/'

def fetch_csv_data(session, referer, search_args):
    # Load Team Time Entry Summary
    response = session.get(referer)
    soup = bs(response.content, 'lxml')
    inputs = soup.find_all('input',type='checkbox')
    # create the options_map to map input arguments to
    options_map = {}
    for i in inputs:
        section = i.find_parent('fieldset').legend.text.split(' ')[0]
        key = re.sub(r'[^A-z0-9]+',' ',i.parent.text).strip()
        key = section+'_'+key.replace(' ','_')
        key = key.lower()
        options_map[key] = i['name']
    options_map['start_date'] = 'conditions[1][value]'
    options_map['end_date'] = 'conditions[2][value]'
    
    session.headers.update({'referer':referer})
    payload = create_fbm_querystring(options_map, **search_args)
    r = session.post(referer+'csv/', data = payload)
    return r.text


def fetch_all_fbm_csv_data(search_args):
    ''' This function retrieves FBM reports in csv form.
    '''
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
        s.post('https://mcfb.soxbox.co/login/',data='username={}&password={}&location=1&action=Login'.format(user, passw))
        del s.headers['content-length']

        team_entry_search_args = {'sum_hours_worked': '1',
                              'start_date': search_args['start_date'],
                              'end_date': search_args['end_date']}

        entries = fetch_csv_data(s, 'https://mcfb.soxbox.co/reports/team/time-entry-summary/', team_entry_search_args)

        donations = fetch_csv_data(s, 'https://mcfb.soxbox.co/reports/donor/donations/', search_args)
    return donations, entries
        


def fetch_fbm_report_by_month(year, month, search_args=None):
    ''' This function fetches the FBM report for the given year and month.
        - If search arguments are not provided, then it will use default
          parameters.
    '''
    # validate year and month given
    assert isinstance(year, int), 'The given year must be an integer'
    assert isinstance(month, int), 'The given month must be an integer'
    this_year = datetime.datetime.now().year
    assert year>2000, 'The given year must be greater than 2000'
    assert year <= this_year, 'The given year must be less than or equal to {}'.format(this_year)
    this_month = datetime.datetime.now().month
    assert month>=1, 'The given year must be greater than or equal to 1'
    assert year!=this_year or month<=this_month, 'The given year must be less than or equal to {}'.format(this_year)

    # create a default set of search arguments if none are present
    if not search_args:
        search_args = get_default_search_args()

    # determine the total number of days in the given month
    total_days = calendar.monthrange(year,month)[1]
    search_args.update({ 
        'end_date': '{:04}-{:02}-{:02}'.format(year, month, total_days),
        'start_date': '{:04}-{:02}-01'.format(year, month) })
    return fetch_all_fbm_csv_data(search_args)

def fetch_last_fbm_report():
    ''' This function fetches the last month of FBM data
    '''
    # determine the previous month date
    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    year = int(lastMonth.strftime("%Y"))
    month = int(lastMonth.strftime("%m"))

    # Get the data
    return fetch_fbm_report_by_month(year, month)

def find_umatched_organizations(df):
    ''' This function is used to determine if any organizations where 
        not automatically matched with
    '''
    return df.loc[df['Source Type'].isnull()]

def map_organization_source_type(month_data_df, organizations_csv_filename='organizations.csv'):
    ''' This function takes the month of data and matches the each organization
        to a source type category.
    '''
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

def create_daily_total_dict(df):
    ''' This function creates a dictionary comparing the date donated on 
        to the weight donated.
    '''
    d = dd(float)
    for i,row in df.iterrows():
        d[row['Donated On']]+=row['Weight (lbs)']
    return d

def create_summary_dict(df, key, value):
    ''' This function creates a dictionary to summaries to categories in a dataframe.
        The column of value is summed by each type of key in the dataframe.

        Ex:
            create_summary_dict(
              df,                         # the dataframe
              key = 'Source Type',        # the column name to become keys
              value = 'Weight (lbs)' )    # the column to be summed by the keys
    '''
    d = {}
    for typ in set(df[key]):
        d[typ] = sum(df[df[key]==typ][value])
    return d

def process_sumamry(
    df, 
    year, 
    month, 
    starting_inv = 0, 
    ending_inv=0,
    volunteer_hours=0, 
    num_clients = 0, 
    new_clients=0, 
    total_served=0):
    ''' This function 
    '''
    # Located unmapped entries
    missing = find_umatched_organizations(df)
    if len(missing):
        print('The following Donation Ids are missing source type:')
        for i,row in missing.iterrows():
            print(row['Donation ID'], row['Company / Organization Name'])
    
    # process data as csv
    month_name = datetime.datetime(year=year, month=month, day=1).strftime("%b")
    summary_dict = create_summary_dict(df, key = 'Source Type', value = 'Weight (lbs)')

    result = 'Inventory {},Weight (lbs)\n'.format(month_name)
    sub_total = 0
    for k,v in summary_dict.items():
        if k!='Waste':
            result += '{},{}\n'.format(k,v)
            sub_total+=v
    result += 'Subtotal,{}\n'.format(sub_total)
    waste = summary_dict.get('Waste',0)
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


def create_summary_csv(csv_text):
    ''' This function creates a summary csv text that can be written to file.
    '''
    # Map organziations to their organization type
    df = csv_to_dataframe(csv_text)
    df = map_organization_source_type(df)
    min_date = datetime.datetime.strptime(min(df['Donated On']), '%Y-%m-%d')
    return process_sumamry(df, min_date.year, min_date.month)

