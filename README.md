# collectives_reporting

This script is a first version of a set of functions to automatize reporting of activities for a mountineering club (Club Alpin Français d'Annecy).

Further, functions will be integrated in a webpage that allow easy reporting for direction members.

If you want to test the script please contact the chief of digital at CAF d'Annecy to get the datasets.

## About the creation and registration to event

There is two class of members : members and volunteers. The second can create event and all can register to. 

An event is the basic unit of the club offer. An event has a title, a time start, time end, a number of place, a leader, etc.

There is 7 kind of event's class (collective - i.e. an outdoor activity, party, classroom ...). An event has one and only one class.

However an event may have one or more activity attribut ("ski de randonnée", "escalade"...). An event may have a tag  ("mobilité douce", "formation"...) to specify some additionnal information.  


## About the information system

There are two main tables :
- event : list of event
- user : list of users

There are four cross-table (many to many) :
 - registration : events and users registered to
 - event_leaders : events and leaders (main leader and coleader)
 - eventactivity_types : events and activity types
 - event_tags : events and tags
 
 There is two tables with stable number of lines :
 - activity_type : all activity available
 - event_type : the 7 event type available
 
 
