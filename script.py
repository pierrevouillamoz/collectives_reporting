#coding: latin-1 
import pandas as pd
import demoji

#dataloading
activityTypes=pd.read_csv("data/activity_types.csv", sep=',', encoding="latin")
eventTags=pd.read_csv("data/event_tags.csv", sep=',')
eventTypes=pd.read_csv("data/event_types.csv", sep=',')
events=pd.read_csv("data/events.csv", sep=',',
                   low_memory=False,
                   parse_dates=["start","end"])
                   #encoding="latin")
eventActivity=pd.read_csv("data/event_activity_types.csv", sep=',')
registrations=pd.read_csv("data/registrations.csv", sep=',', low_memory=False)
users=pd.read_csv("data/users.csv", sep=',')
eventLeaders=pd.read_csv("data/event_leaders.csv", sep=',')

#datacleaning
events=events.drop(labels=["rendered_description", "photo"], axis=1)
events=events.drop_duplicates()
activityTypes=activityTypes.drop(labels=["order"], axis=1)
eventTypes=eventTypes.drop(labels=["terms_title","terms_file"], axis=1)
eventActivity=eventActivity.drop_duplicates()
registrations=registrations.drop(labels="id", axis=1)
eventTags.type=eventTags.type.replace({1:"Mobilité douce",
                                       2:"Connaissance et protection de la montagne",
                                        3:"Séjour",
                                        4:"Formation",
                                        5:"Randonnée alpine",
                                        6:"Handicaf",
                                        7:"Groupe Jeunes Alpinistes",
                                        8:"Evènement",
                                        9:"Cycle découverte",
                                        10:"Rando Cool",
                                        11:"Achat"})

#enrichissement des données

def extract_title(title):

    """This function cleans the title from emoji
    """
    dem = demoji.findall(title)
    for item in dem.keys():
        title=title.replace(item,'')

    title=title.strip()

    return title

def extract_location(description):

    """This function extracts the location of the event
    """
    
    if type(description)==str:

        description=description.lower()

        #Volunteer set the location after the word "secteur"
        if "secteur" in description:
            A=description.split("\r\n")
            i=0
            while "secteur" not in A[i]:
                i=i+1

            if ":" in A[i]:    
                a=A[i].split(":")[1].strip()
                a=a.strip(".")
            else:
                a=A[i].replace("secteur", "").strip()
                a=a.strip(".")
                a=a.replace("*","")
                a=a.replace("**","")

            return a

        #Sometime the word "lieu" is used to set the location
        if ("lieu" in description) and ("secteur" not in description):
            A=description.split("\r\n")
            
            for i in range(0,len(A)):

                #Unfortunately, "lieu" can be used for departure
                if ("lieu" in A[i]) and (("départ" or "depart")not in  A[i]) and ("lieux" not in A[i]):
                    break
                
            #Second check, because loop may not break and A[end] can exist without the word 'lieu'
                
            if ('lieu' in A[i] and (("départ" or "depart")not in  A[i])):       

                if ":" in A[i]:    
                    a=A[i].split(":")[1].strip()
                    a=a.strip(".")
                else:
                    a=A[i].replace("lieu", "").strip()
                    a=a.strip(".")
                    a=a.replace("*","")
                    a=a.replace("**","")
                return a

            else:
                return ""
            
        
        else:
            return ""

    else:
        return ""

def location_correction(location):

    """This function will merge some location to reduce the number of possibilities

    """

    if ("lauzière" in location) or ("lauziere" in location):
        return "Lauzière"

    if ("semnoz" in location) and ("visitation" in location):
        return "Semnoz - Visitation"

    if ("semnoz" in location) and ("visitation" not in location):
        return "Semnoz"

    if "visitation" in location:
        return "Semnoz - Visitation"

    if ("aravis" in location) and ("bornes" in location):
        return "Bornes - Aravis"
    
    if ("aravis" in location) and ("bornes" not in location):
        return "Aravis"

    if ("bornes" in location) and ("aravis" not in location):
        return "Bornes"
    

    if ("beaufortain" in location) or ("baufortain" in location) or ("beaufortin" in location):
        return "Beaufortain"

    if "veyrier" in location:
        return "Mont Veyrier"

    if ("chablais" in location) and ("faucigny" in location):
        return "Chablais - Faucigny"
    
    if ("chablais" in location) and ("faucigny" not in location):
        return "Chablais"
    
    if ("faucigny" in location) and ("chablais" not in location):
        return "Faucigny"
    
    else:
        return location.capitalize()
    
def extract_duration(timedelta):

    """This function converts a timedelay in yyyy-mm-dd h-m-s into float for a
    day duration. Minimum unit is half day

    """
    a=timedelta.days
    if timedelta.seconds/86400>0.5:
        b=1
    else:
        b=0.5
    return a+b

def extract_age_gender(date_of_birth, gender, year):

    """
    This function converts date of birth and gender to a class age and gender
    """
    
    date1= "{}-10-01".format(float(year)-18)
    date2= "{}-10-01".format(float(year)-25)
    
    if (date_of_birth>=date1)&(gender=="Woman"):
        return "Femme -18"
    
    if (date_of_birth>=date1)&(gender=="Man"):
        return "Homme -18"
    
    if (date_of_birth>=date2)&(date_of_birth<date1)&(gender=="Woman"):
        return "Femme -25"
    
    if (date_of_birth>=date2)&(date_of_birth<date1)&(gender=="Man"):
        return "Homme -25"
    
    if (date_of_birth<date2)&(gender=="Woman"):
        return "Femme +25"
    
    if (date_of_birth<date2)&(gender=="Man"):
        return "Homme +25"
    else:
        pass

def upgrade_events(start="2021-10-01", end="2022-09-30", event_status='Confirmed'):

    """
    The very step of our analysis is adding more informations to the event table.
    To ensure this task, from other table we do pivot table or agregation with event_id as index
    and then we merge the reducted table with the event table.

    In the code, some intern variable name will appear : A,B for a list, X, Y for a restricted dataset
    """
    global activityTypes, eventTags, eventTypes, events, eventActivity, registrations, users, eventLeaders

          
    #Step 1 : duration of activity
    events["number_days"]=events["end"]-events["start"]
    events["number_days"]=events["number_days"].apply(extract_duration)

    #Step 2 : registration status in count (active, canceled, nho-show...)
    registrations1=pd.pivot_table(registrations, values='is_self', index='event_id', columns='status', aggfunc='count').fillna(0)
    EVENT=pd.merge(events, registrations1, left_on="id", right_on="event_id", how="left")
    EVENT=EVENT.rename(columns={"id":"event_id"})
    
    #Step 3 : age and gender class 

    year=start[:4]#Pay attention, year is extracted from a string object

    A=[]
    for i,e in users.iterrows():
        A.append(extract_age_gender(e.date_of_birth, e.gender, year))
    users["gender_age"]=pd.Series(A)
    users=users.drop(labels=["date_of_birth","gender"], axis=1)
    del A
    
    registration=registrations[registrations["status"]=="Active"] #Only active registrations matters
    registrations2=pd.merge(registration, users, left_on="user_id", right_on="id", how="left")
    registrations2=pd.pivot_table(registrations2, values="status",index="event_id", columns="gender_age", aggfunc="count").fillna(0)
    EVENT=pd.merge(EVENT, registrations2, on="event_id", how="left")
      
    #Step 4 : activity
    #As event can associated with several activity, we create one column per activity whose contain is 0 or 1
    eventActivity2=pd.merge(eventActivity,activityTypes, left_on="activity_id", right_on="id", how="outer")
    eventActivity2=pd.pivot_table(eventActivity2, values='id', index='event_id', columns="name", aggfunc='count').fillna(0)
    EVENT=pd.merge(EVENT, eventActivity2, on="event_id", how="left")

    #Step 5 : multi activity fusion
    #As some event are associated with many activity, we fusion sting of activities to create unique
    #combination
    X=pd.merge(eventActivity, activityTypes, left_on="activity_id", right_on="id", how="outer").drop(labels=['activity_id',"short","trigram","deprecated","email"], axis=1)
    A=[]

    for i in X["event_id"].unique():
    
        #i refers to event_id
        a=""
    
        for e in X[X["event_id"]==i]["name"]:
            a+=e+" "
        a=a.rstrip()    
        A.append([i,a])
        del a

    activityMultitypes=pd.DataFrame(A, columns=["event_id","multi_activity"])
    EVENT=pd.merge(EVENT, activityMultitypes, on="event_id", how="left")
    EVENT["multi_activity"]=EVENT["multi_activity"].fillna("Non classé")
    del X, A

    #Step 6 : we specify if event is a parent event
    X=EVENT[EVENT["parent_event_id"]>0][["parent_event_id"]]
    X=X.drop_duplicates()
    X=X.rename(columns={"parent_event_id":"id"})
    X["is_parent"]=1 
    EVENT=pd.merge(EVENT, X, left_on="event_id", right_on="id", how="left").fillna(0)
    EVENT=EVENT.drop(labels="id", axis=1)
    del X
    
    #Step 7 : adding event type name
    eventTypes=eventTypes[["id","name"]]
    EVENT=pd.merge(EVENT, eventTypes, left_on="event_type_id", right_on="id", how="left")
    EVENT=EVENT.rename(columns={"name":"eventType"})
    EVENT=EVENT.drop(labels="id", axis=1)

    #Step 8 : Correction bad event type assigantion
    #There is several event type, seven actualy. One of them "Inscription en ligne" can be
    #interpretered as a first step for registration to a parent event before child event registration
    #But there is no technical limitation. So we correct parent event that are not a "Inscription
    #en ligne"
    
    idx=EVENT[(EVENT.eventType=="Collective")&(EVENT.is_parent==1)].index 
    if len(idx)!=0:
        EVENT_=EVENT.loc[idx]
        EVENT=EVENT.drop(labels=idx, axis=0)
        EVENT_=EVENT_.drop(labels="eventType", axis=1)
        EVENT_["eventType"]="Inscription en ligne"
        EVENT=pd.concat([EVENT, EVENT_], axis=0)

    #Step 9 : extract location
    EVENT["location"]=EVENT["description"].apply(extract_location)
    EVENT["location"]=EVENT["location"].apply(location_correction)

    #Step 10 : coleader number

    """This function upgrade event with coleader only
    """
    X=pd.merge(eventLeaders, EVENT, on="event_id", how="inner")
    A=[]

    for i in range(0,len(X)):
        
        if X.iloc[i]["user_id"]==X.iloc[i]["main_leader_id"]:
            A.append(i)

    X=X.drop(index=A)

    X=X.drop(labels="main_leader_id", axis=1)
    X=X["event_id"].value_counts()
    X=X.rename("Nb coleaders")
    X=pd.merge(EVENT.event_id,X, left_on="event_id", right_on=X.index,
               how="outer").fillna(0)
    
    EVENT=pd.merge(EVENT, X, on="event_id", how="outer")
    EVENT["Nb leader"]=1

    #Step 11 : add "mobilité douce" tag
    X=eventTags[eventTags["type"]=="Mobilité douce"]
    X=X[["event_id","type"]]
    X["type"]=X["type"].replace(to_replace="Mobilité douce", value="oui")
    X=X.rename(columns={"type":"Mobilité douce"})
    EVENT=pd.merge(EVENT, X, on="event_id", how="outer")
    
    
    #Time filtration occurs at the end  to avoid trouble with the order of some items
    EVENT=EVENT[(EVENT.start>=start)&(EVENT.end<=end)]

    #Filtration on "Confirmed event status". Other status is "canceled"
    if event_status == "Confirmed":
        EVENT=EVENT[EVENT.status=="Confirmed"]
    else:
        pass

    #title cleaning
    #EVENT["title"]=EVENT["title"].apply(extract_title)

    
    return EVENT

def get_users_registrations (EVENTS, registrations, activity_filter=None,
                             eventType_filter=None):

    """
    This function makes a users population based dataset.
    The function needs the EVENT file previously computed to frame the result
    between two dates.
    By default, all events are taken into account, but two kind of filter are possible
    
    """
    

    X=EVENTS[["event_id","eventType","multi_activity"]]

    if activity_filter in X["multi_activity"].unique():

        X=X[X["multi_activity"]==activity_filter]

    if eventType_filter in X["eventType"].unique():

        X=X[X["eventType"]==eventType_filter]

    Y=pd.merge(registrations, X, on="event_id", how="right")

    users_registration=pd.pivot_table(Y, values="event_id", index="user_id", columns="status",
                   aggfunc='count').fillna(0)

    return users_registration

def users_registrations_analysis(users_registration):

    """
    For each features we compute the distribution
    """
    
    A=[]

    for i in users_registration.columns:

        a=users_registration[i].value_counts()
        A.append(a)

    A=pd.concat(A, axis=1).fillna(0)

    A.columns=Z.columns

    A=A.sort_index() 

    A=A.drop(index=0)

    return A

def get_events(EVENT):

    """
    This function provides a clean dataset for human analysis 
    """

    X=EVENT[["event_id",
             "eventType",
             "multi_activity",
             "title",
             "location",
             "Mobilité douce",
             "start",
             "end",
             "number_days",
             "location",
             "num_slots",
             "Nb leader",
             "Nb coleaders",
             "Active",
             "Femme -18",
             "Homme -18",
             "Femme -25",
             "Homme -25",
             "Femme +25",
             "Homme +25",
             "SelfUnregistered",
             "Rejected",
             "JustifiedAbsentee",
             "UnJustifiedAbsentee",
             "Waiting",
             "PaymentPending"]]

   
    
    X=X.rename(columns={"multi_activity":"Activity",
                "Active":"Participants (hors encadrants)",
                "num_slots":"Places ouvertes"})
    
    return X

def events_analysis(EVENT, methode='simple'):


    """
    The goal of this function is producing data on event agregated by event type and activity.
    There is two methods :
    - "double" uses the fact activity information is stored on several columns (one per activity)
    and event can have many activity. The inconvenient is activity will be counted twice
    - "simple" uses the multi_activity column : there is more activity due to activity fusion
    but there is no double count.
    """

    global eventType
    
    X=EVENT #X to make code shorter
    A=[] #List to store data
    
           
    #Iterations to filter
    for eventType in eventTypes["name"]:
        
        X1=X[X["eventType"]==eventType] #X1 is a restricted version of X
        
        if methode=='double':
            
            S=activityTypes["name"]   
            
            for activity in S: #Iterations on activity

                Y=X1[X1[activity]==1] #Iterations are made on column'names. 

                A.append([eventType, #A stores data
                          activity,
                            Y[activity].sum(),
                          Y["number_days"].sum(),
                          Y['Active'].sum(),
                          Y['Femme +25'].sum(),
                          Y['Homme +25'].sum(),
                          Y['Femme -25'].sum(),
                          Y['Homme -25'].sum(),
                          Y['Femme -18'].sum(),
                          Y['Homme -18'].sum()])
    
        if methode=='simple':
            
            S=X1["multi_activity"].unique()  
            
            for activity in S: #Iterations on activity as a modality of one columns
                Y=X1[X1["multi_activity"]==activity] #Restriction of the dataset to  

                A.append([eventType, #list object to store row of futur dataframes
                          activity,
                            len(Y["multi_activity"]),
                          Y["number_days"].sum(),
                          Y['Active'].sum(),
                          Y['Femme +25'].sum(),
                          Y['Homme +25'].sum(),
                          Y['Femme -25'].sum(),
                          Y['Homme -25'].sum(),
                          Y['Femme -18'].sum(),
                          Y['Homme -18'].sum()])
    
    #End of loop
    
    #Make dataframe
    OUT=pd.DataFrame(A,  columns=["eventType",
                                "activity",
                                "Nombre d'évènements",
                                "Nombre de jours",
                                "Nb pratiquants",
                                'Femme +25',
                                'Homme +25',
                                'Femme -25',
                                'Homme -25',
                                'Femme -18', 
                                'Homme -18',     
                                    ])
    
    return OUT


def activity_leaders_analysis(EVENT, methode='simple'):

    
    
    global eventTypes
    
    X=EVENT #On utilisera X pour simplifier les notations
    A=[] #Cette liste va stocker les données qui seront à la fin dans un DataFrame
    
    #Il y a deux méthodes de comptage, double qui compte deux fois les activités
    #et simple qui les compte une fois mais considère les multiactivités (ex Ski de randonnée et Surf de randonnée)
    #comme des activités à part entière  
   
       
    #Boucle pour filtrer. Nous allons créer un tableau qui classe les évènements par type (collective, soirée) puis par
    #activité
    for eventType in eventTypes["name"]:
        
        X1=X[X["eventType"]==eventType] #X1 est une version réduite de X (restriction au type d'évènement)
        
        if methode=='double':
            
            S=activityTypes["name"]
            
            for activity in S: #Boucle sur les activités qui sont un ensemble de colonnes

                Y=X1[X1[activity]==1] #Y est la version réduite de X (restriction au type d'activité)
                                      #Pour chaque colonne, on s'intéresse à celle où la valeur vaut 1
                    
                for leader in Y["main_leader_id"].unique():
                    
                    Z=Y[Y["main_leader_id"]==leader]
                    A.append([eventType, #A est une liste, et contient les futures lignes du tableau final
                                    activity,
                                    leader,
                                    Z[activity].sum(),
                                    Z["number_days"].sum(),
                                    Z['Active'].sum()])
                              
    
        if methode=='simple':
            
            S=X1["multi_activity"].unique()
            
            for activity in S: #Boucle sur les activités qui est une colonne qui a différentes valeurs

                Y=X1[X1["multi_activity"]==activity] #Y est la version réduite de X (restriction au type d'activité)
                                                    #Simple filtre pour les différentes valeurs de "multiactivity"
                for leader in Y["main_leader_id"].unique():
                    
                    Z=Y[Y["main_leader_id"]==leader] 
                    A.append([eventType, #A est une liste, et contient les futures lignes du tableau final
                              activity,
                              leader,
                             len(Z["multi_activity"]),
                              Z["number_days"].sum(),
                              Z['Active'].sum()])
                              
    #La boucle est terminée
    
    #Création du DataFrame à partir de A
    OUT=pd.DataFrame(A,  columns=["eventType",
                                "activity",
                                  "leader",
                                  "Nombre d'évènements",
                                  "Nombre de jours",
                                  "Nb pratiquants",    
                                    ])
    #Variable de sortie : le dataframe
    return OUT


def leaders_analysis(EVENT):
    
    Nb_event=pd.pivot_table(EVENT, values="Active", index='main_leader_id', aggfunc="count")
    Nb_days=pd.pivot_table(EVENT, values="number_days", index='main_leader_id', aggfunc="sum")
    Nb_pers=pd.pivot_table(EVENT, values="Active", index='main_leader_id', aggfunc="sum")
    
    OUT=pd.concat([Nb_event,Nb_days,Nb_pers], axis=1)
    OUT.columns=["Nombre d'évènements","Nombre de jours","Nb pratiquants"]
    return OUT

def get_coleaders(EVENT):

    """This function upgrade event with coleader only.
    After use leader_analysis or activity leader_analysis
    """
    X=pd.merge(eventLeaders, EVENT, on="event_id", how="inner")
    A=[]

    for i in range(0,len(X)):
        
        if X.iloc[i]["user_id"]==X.iloc[i]["main_leader_id"]:
            A.append(i)

    X=X.drop(index=A)

    X=X.drop(labels="main_leader_id", axis=1)

    #We change the name to use functions like leader_analysis further, but real
    #main leaders are dropped
    X=X.rename({"user_id":"main_leader_id"}, axis=1)
    
    
    return X

def filtration_by_camp(EVENT, season='été'):

    """ from the upgraded event dataset we do restriction to event with the mention "camp d'été" or
    "camps d'hiver". Then we can apply functions like event_analysis or leader_analysis

    """
        
    if season == 'été':
        A=[]#to store iloc 
        
        for i in range(0,len(EVENT)):
            if (("camp" or "camps") in EVENT.iloc[i].title.lower()) and (("été" or "ete" or "éte" or "eté") in EVENT.iloc[i].title.lower()):
                A.append(i)

        EVENT = EVENT.iloc[A]
        del A
        
    if season == 'hiver':
        A=[]#To store iloc 
        
        for i in range(0,len(EVENT)):
            if (("camp" or "camps") in EVENT.iloc[i].title.lower()) and ("hiver" in EVENT.iloc[i].title.lower()):
                A.append(i)
                
        EVENT=EVENT.iloc[A]
        del A
        
    if season == None:
        pass
    
    else:
        pass
    return EVENT

def get_parents_only(EVENT):

    """This function will return a pandas Series of title. This is restriction of parent event.
    Further the function "filtration by title" will be apply to produce only child event  dataset
    """
    X=EVENT[EVENT["is_parent"]==1]

    #This part of code is a way to drop line that refers to "camp d'été" or
    #"camp d'hiver" because filtration_by_camp already exist
    X1=filtration_by_camp(X, season='été')
    if len(X1)!=0:
        X=X.drop(index=X1.index)

    X2=filtration_by_camp(X, season='hiver')
    if len(X2)!=0:
        X=X.drop(index=X2.index)

    return X.title


def filtration_by_parents_only(EVENT,title):

    """
    Thank to the title get with function get_parent_only, we can do a restriction to the child event
    Then we can apply other analysis function
    """
    
    idx=EVENT[EVENT["title"]==title].index
    
    if len(idx)==0:
        return "Aucunes activités"
    if len(idx)==1:
        idx=idx[0] 
        event_id=EVENT.loc[idx]["event_id"]
        A=EVENT[EVENT["parent_event_id"]==event_id]
        return A
    if len(idx)>1:
        B=[]
        for i in idx:
            event_id=EVENT.loc[i]["event_id"]
            A=EVENT[EVENT["parent_event_id"]==event_id]
            B.append(A)
        C=pd.concat(B, axis=0)
        return C
    
def filtration_by_tags(EVENT, tag="Séjour"):

    """
    We do a restiction to event with a tag. tag can be :"Mobilité douce",
    "Connaissance et protection de la montagne", "Séjour", "Formation",
    "Randonnée alpine", "Handicaf", "Groupe Jeunes Alpinistes", "Evènement",
    "Cycle découverte", "Rando Cool", "Achat"
    """
    global eventTags

    event_id=eventTags[eventTags.type==tag].event_id #Récupération de event_id correspondants au tag
    
    A=[]  #Initialisation d'une liste
    
    for i in event_id: #Boucle pour récupérer les lignes où event_id correspond
        A.append(EVENT[EVENT["event_id"]==i])
    EVENT=pd.concat(A, axis=0)
    return EVENT

#test des fonctions

EVENT=upgrade_events(start="2021-10-01", end="2022-09-30", event_status="Confirmed")


##EVENT=filtration_by_camp(EVENT)

EVENT.to_csv("resultats/liste.csv", sep=";", decimal=",", encoding="latin",
             errors='ignore')
get_events(EVENT).to_csv("resultats/liste_light.csv", sep=";", decimal=",",
                         encoding="latin", errors="ignore")

if len(EVENT)!=0:
    events_analysis(EVENT, methode="simple").to_csv("resultats/participation.csv",
                                                    sep=";", decimal=",",encoding="latin",errors="ignore")
    activity_leaders_analysis(EVENT, methode="simple").to_csv("resultats/leaders.csv",
                                                              sep=";", decimal=",",encoding="latin",errors="ignore")
    leaders_analysis(EVENT).to_csv("resultats/leaders_light.csv",
                                   sep=";", decimal=",",encoding="latin",errors="ignore")
    
if len(EVENT)==0:
    print("Aucune activité")
    
Z=get_users_registrations (EVENT, registrations, activity_filter=None,
                             eventType_filter=None)

A=users_registrations_analysis(Z)

A.to_csv("users_analysis.csv", sep=";", decimal=",")

Z.to_csv("users_registrations.csv", sep=";", decimal=",")
