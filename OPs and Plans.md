# Planning - (Future README)
# First stage: - Getting started...
  CSV to Excel
   - [x] create a CSV of all organizations and their types
     - [x] match each organziation with a source type
   - [x] read in organizations into DataFrame - organizations_df
   - [x] read in Month data into DataFrame - month_data_df
   - [x] assign each Organization in month_data_df a Source from organizations_df
   - [x] notify for each organization without source type
     - [ ] automatically make the best guess
     - [ ] update csv with changes
   - [ ] POSTPONED: convert weights to dollar
   - [ ] create summary for each source type by dollar
   - [ ] write to file

  Github
   - [x] working repository
   - [x] upload file
   - [x] link with IDE
   - [x] link with pythonanywhere.com

# Second Stage: - "Did you even graduate?" stage
   - [ ] Private web app - Converting given Data
   - [x] Start with PIE chart comparing inventory sources
   - [ ] Then compare month to month of the data and plot changes over time

# Third Stage - complete stage
  - [ ] Web scraping Food Bank Manager
  - [x] Web server deployment
  - [x] Public web app - Visualization
  - [ ] Listing results (of organizations) by type/source
  - [ ] Find information about federal food pounds to dollar conversion
  - [ ] "Compound Food Donations" minimum based child poverty rates (higher around 60K)

# Fourth stage - bo-bo-bonus stage
  metrics:
    donators who are down yty mtm on donations, rank them by % down, especially if inventory is down for the month
  visualization - donations meeting goals
  visualization - metrics
  by donating to this organization, how much food waste is mitigated
  month-by-month bubble plot Visualization

# Fifth Stage - wow 'em stage
  notification system

# Sixth Stage - OTHER PROBLEM STATEMENTS
  Paz de Christo: ignoring Salesforce, we build a notification system (text) using Twilio that outputs to a CSV
