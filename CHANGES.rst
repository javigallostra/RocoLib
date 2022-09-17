Changelog
=========


0.1.0 - (unreleased)
======================


Features
--------

- #172 Add left/right arrow buttons on PC to indicate that the user can change the problem by clicking
- #168 Add a query builder to ease the handling of MongoDB queries
- #168 Add API endpoint to get logged in user preferences
- #168 Add user preferences (default gym, hold detection, show only latest wall sets) and page to edit them
- #149 #150 When viewing a problem, swipe left or right to go to next or previous problem  
- #146 Add endpoint to public API to mark a boulder as done
- #138 Enable changing gym from problems list page & UI improvements
- #134 #140 #142 #144 #151 UI improvements
- #133 Include repetitions as part of the data of a problem. Enable sorting by repetitions.
- #129 Refactor DDBB connection handling
- #127 Show problems as collapsible cards in problem lists
- #125 Add wall versioning, list only latest sets for problem creation
- #123 Add changelog
- #121 API endpoint to rate boulders
- #116 Add language support and french translation
- #114 Display time since creation in boulders list
- #113 Use command-line arguments for setting DOCKER_ENV
- #100 Add more API endpoints
- #86 #91 #94 Public API
- #93 Add test framework
- #87 #88 Style changes and type hinting
- #75 Enable setting multiple climb dates
- #63 Add option to export problem as image
- #61 Add functionality to find nearest gym
- #58 Add notes field to boulders
- #45 Migrate DDBB from firebase to MongoDB
- #40 Add option for users to register and ticklists
- #38 Enable drag and drop of hold markers when creating problems on PC
- #28 #31 #32 User sign up and login
- #20 Support for multiple gyms
- #10 Problem drawing


Fixes
-----

- #189 Fix section and gym not being shown on some ticklist problems
- Enable CORS on API endpoints
- #185 Fix downloading a problem as an image 
- #184 Spacing between radio button and text in hold selection options when creating a problem
- #183 Display correct text in hold detection text label on the problem creation page 
- #170 Take into account latest wall set flag when swiping problems
- #162 Optimize DDBB queries
- #161 Fix page header on error templates
- #159 Keep scroll status after problem load due to swipe
- #153 Add heursitics to filter non horizontal swipes on problem view
- #136 Fix visualization of action buttons on problem view footer
- #132 Fix malformed HTML element IDs in problem lists
- #128 Fix fields rendering in user's ticklist problem cards
- #118 Remove production DDBB credentials from Docker image
- #117 Fix `get_time_since_creation` function
- #112 Fix going back from `random_problem` page
- #111 Fix hardcoded gym id when none selected
- #99 Increase max length of boulder name and creator
- #98 Fix visualization of dates climbed
- #73 Ignore gyms without location when searching for nearest gym


Changes
-------

- #178 Use integers for difficulties instead of strings
- #173 Use same error schema for all API endpoints & errors 