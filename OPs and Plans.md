# Planning - (Future README)
# First stage: - Getting started
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

# Second Stage: - Did you even graduate? stage
   - [ ] Private web app - Visualizing given Data
   - [x] Start with PIE chart comparing inventory sources
   - [ ] Then compare month to month of the data and plot changes over time

# Third Stage - complete stage
  - [ ] Web scraping Food Bank Manager
  - [x] Web server deployment
  - [x] Public web app - Visualization
  - [ ] Listing organizations by source 0
  - [ ] Find information about federal food pounds to dollar conversion

# Fourth stage - bonus stage
  metrics:
    donators who are down yty mtm on donations, rank them by % down, especially if inventory is down for the month
  visualization - donations meeting goals
  visualization - metrics
  by donating to this organization, how much food waste is mitigated
  month-by-month bubble plot Visualization

# Fifth Stage - wow stage
  notification system
