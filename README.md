# collectives_reporting

This script is a first version of a set of functions to automatize reporting of activities for a mountineering club (Club Alpin Français d'Annecy).

Further, functions will be integrated in a webpage that allow easy reporting for direction members.

If you want to test the script please contact the chief of digital at CAF d'Annecy to get the datasets.

## About the creation and registration of events

There is two class of members : members and volunteers. The second can create event and all can register to. 

An event is the basic unit of the club offer. An event has a title, a time start, time end, a number of place, a leader, etc.

There is 7 kind of event's class (collective - i.e. an outdoor activity, party, classroom ...). An event has one and only one class.

However an event may have one or more activity attribut ("ski de randonnée", "escalade"...). An event may have a tag  ("mobilité douce", "formation"...) to specify some additionnal information.  


## About the information system

There are two main tables :
- `events` : list of events
- `users` : list of users

There are four cross-table (many to many) :
 - `registrations` : events and users registered to
 - `event_leaders` : events and leaders (main leader and coleader)
 - `event_activity_types` : events and activity types
 - `event_tags` : events and tags
 
 There is two tables with stable number of lines :
 - `activity_types` : all activities available
 - `event_types` : the 7 event types available
 
 ## Methodology of the reporting
 
As several tables have the event_id information, some aggregations are made on this key upon these tables and results are merged with the `events` table. 

There are two steps :
- building a complete `events` table
- doing several analysis on this table

To achieve this goal, there are four types of functions :
- extract functions : to generate some kind of informations (e.g. from gender and date of birth 6 class are made : "Femme <18", "Homme >25" etc.)
- get functions : to get transformed dataset or some information
- filtrations function : to filter over one attribut of the dataset
- analysis functions : to make the reporting per event, activity, leader, coleader

## Analysis in practice

First `upgrade_events` is applied to generate a complete dataset of events happened between two dates (e.g. from the october first to septembre the 30th the year after). upgrade_event requires functions : `extract_location`, `extract_title`, `location_correction` and `extract_age_gender`. The output is a complete dataset of event : 
- number lines : number of events
- number of colums : attributs (55 !)

To get a shorter version of this output, member can use function `get_events`  (same number of line, only 26 attributs). 
Output of upgrade_events is named EVENT.

Now, member could apply some filtration functions on EVENT :
- `filtration_by_camp` (e.g. "été" or "hiver")
- `filtration_by_tags` (e.g. "séjour")
- `filtration_by_parents_only`. This function requires to execute first `get_parents_only` to get the list of titles of event whose are parent event. This function is useful to generate all events linked to a parent event (e.g. all climbing event on a specific location and time).

All this filtered functions generate an filtered EVENT dataset.

Then analysis functions can be applied to the EVENT dataset (filtered or not).
- `events_analysis` : the agregation of members players, time duration per event type and activity type. There is two count methods in case of several activities : activity types are merged and counted one time or activity type are not merged and counted twice. Twice counting could be useful if nomenclotura of activity is important.
- `activity_leaders_analysis` : agregation of members players and time duration per event, activity type and leader id (main leader). There are two count methods too.
- `leaders_analysis` : agregation of members players and time duration per leader id (main leader). Only one count method.
- The same reporting is available for coleader analysis : first `get_coleaders` should be applied, then functions `activity_leaders_analysis` and `leaders_analysis` are applyed. `get_coleaders` list only coleaders and remove main leader. 

## Analysis of users' behavior

Previous functions were based on an population of events. The other side of our reporting is working on users' behavior. 

`get_users_registrations` makes a users population based dataset. For each user, 
features of the number of events done (Active), unregistered, etc.

`users_registrations_analysis` is based on the result of the previous function.
For each features, the distribution is computed and stored in the dataset. 
  
