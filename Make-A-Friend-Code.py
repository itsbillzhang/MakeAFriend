# In[403]:


import pandas as pd

df = pd.read_csv (r'C:\Users\BillPC\Desktop\CS Fun\Operation Cordial\data.csv') 
#print(df)
participants = len(df.index)
print(participants)


# In[418]:


#given 2 rows, find absolute value of differences of A <-> AD, known as similarities
# The lower the score, the better
def similarity_calculate(p1, p2):
    differences = 0
    #ID_different_with = p2['ID']
    first_column_index = df.columns.get_loc("A")
    last_column_index = df.columns.get_loc("Hobbies")
    for index in range(first_column_index, last_column_index):
        differences += abs(p1[index] - p2[index])
    return differences

similarity_calculate(bill, p2)


# In[238]:


# given 2 rows, find the difference in age, and apply an age compatibility
# forumla. The lower the score, the better. 
def age_similarity_calculate(p1,p2):
    age_index = df.columns.get_loc("Age")
    age_weighting = 15
    if p1[age_index] == ">23":
        p1_age = 24
    else:
        p1_age = int(p1[age_index])
    if p2[age_index] == ">23":
        p2_age = 24
    else:
        p2_age = int(p2[age_index])
    age_gap = abs(p1_age - p2_age)
    age_gap_score = age_weighting * age_gap
    return age_gap_score

age_similarity_calculate(bill, p2)
    

# In[247]:


#Testing logic for hobbies_to_list on an individual user

ptest = df.iloc[0, -2]
df.iloc[0]
hobbies_as_string = df.iloc[0, -2]
hobbies_as_list = hobbies_as_string.split(' ,')
df.at[0, "Hobbies"] = hobbies_as_list
ptest = df.iloc[0]
ptest


# In[405]:


# given a person's info represented by a row in the df, change the 
# string representing hobbies seperated by a comma, 
# into a list with individual hobbies 
# e.g.: "reading, playing league" -> ["reading", "playing league"]

def hobbies_to_list(df):
    #hobbies_index = df.columns.get_loc("Hobbies")
    for i in range(0, participants):
        hobbies_as_string = df.at[i, "Hobbies"]
        hobbies_as_list = hobbies_as_string.split(', ')
        df.at[i, "Hobbies"] = hobbies_as_list


# In[406]:


#changing the 'Hobbies' part to all list of strings
hobbies_to_list(df)


# In[483]:


# given 2 people (rows), calculate a rating based on the 
# number of matching hobbies. This will be used in the finally
# compatibility calculation

def hobby_similarity_calculate(p1,p2):
    hobby_multiplier = 25
    p1_copy = p1.copy()
    p2_copy = p2.copy()
    hobbies_matched = 0
    hobby_index = df.columns.get_loc("Hobbies")
    p1_hobby_list = p1_copy[hobby_index]
    p2_hobby_list = p2_copy[hobby_index]
    
    for p1_hobby in p1_hobby_list:
        for p2_hobby in p2_hobby_list:
            #print(f"Checking if {p1_hobby} is in {p2_hobby}")
            if p1_hobby in p2_hobby:
                if p1_hobby.isspace() or (not (p1_hobby.strip())): continue
                hobbies_matched += 1
                p1_hobby_list = [x for x in p1_hobby_list if x != p1_hobby]
                
    #checking for converse
    for p2_hobby in p2_hobby_list:
        for p1_hobby in p1_hobby_list:
            if p2_hobby.isspace() or (not (p2_hobby.strip())):
                continue
            #print(f"Checking if {p2_hobby} is in {p1_hobby}")
                hobbies_matched += 1
                p2_hobby_list = [x for x in p2_hobby_list if x != p2_hobby]
            #else: print("no")
    rating_from_hobbies = hobby_multiplier * hobbies_matched
    return rating_from_hobbies


# In[491]:


# given a person and the dataframe, return a dictionary with the 
# calculations are applied on everyone:

def one_with_all_similarity(p, df):
    compatibility_with_p = {}
    p_id = p['ID']
    for potential_match in range(participants):
        participant_info = df.iloc[potential_match]
        pm_id = participant_info[df.columns.get_loc("ID")]
        if p_id != pm_id: # potential match cannot be yourself
            hobby_rating = hobby_similarity_calculate(p, participant_info)
            similarity_rating = similarity_calculate(p, participant_info)
            age_rating = age_similarity_calculate(p, participant_info)
            compatibility_with_p[pm_id] = similarity_rating + age_rating - hobby_rating
            
    #sorting dictionary keys from least to greatest
    sorted_dict = {k: v for k, v in sorted(compatibility_with_p.items(), key=lambda item: item[1])}
    return sorted_dict

one_with_all_similarity(bill, df)
            


# In[492]:


# given a dataframe, apply the similarity calculator on every possible pair
# the result should be returned as a list

def all_with_all_similarity(df):
    all_calculation = []
    for participant in range(participants):
        p = df.iloc[participant]
        compatibility_dictionary = one_with_all_similarity(p, df)
        all_calculation.append(compatibility_dictionary)
    return all_calculation

#the index 0 is the first person's dictionary, and on..
sim_list = all_with_all_similarity(df)


# In[493]:


sim_list[0]


# In[500]:


# We must now get the list of dictionary into the form 
# {"idp1": ["idpx",...,],
#  "idp2: [,..,..]"}
# where the list ids are sorted from least to greatest
# This is required for the stable roomate algorithm

def stable_roomate_dict(df):
    SRA_dictionary = {} #DF to return as a dictionary, with key prefererences
    for participant in range(participants):
        participant_info = df.iloc[participant]
        participant_id = participant_info[df.columns.get_loc("ID")]
        matches_list = list(sim_list[participant].keys())
        SRA_dictionary[participant_id] = matches_list
        SRA_style = {'preferences' : SRA_dictionary}
    return SRA_style
        


# In[501]:


stable_roomate_dict(df)


# In[504]:


import Algorithmia

input = stable_roomate_dict(df)
client = Algorithmia.client('simw65xPuCyNjcKbutaoIbjo6Va1')
algo = client.algo('matching/StableRoommateAlgorithm/0.1.1')
SRA_result = algo.pipe(input).result
print(algo.pipe(input).result)


# In[558]:


participant_info = df.index[df['ID'] == '5e9a40e5b40d506d0a276d33'].tolist()[0]
print(participant_info)
#match_hobbies = participant_info[["Hobbies"]]
#print(match_hobbies)


# In[586]:

# Produces a dictionary with keys being email address to be sent, and values
# consisting of the message to be sent 
emails_to_send = {}
for participant_ID, match_ID in SRA_result.items():
    
    participant_index = df.index[df['ID'] == participant_ID].tolist()[0]
    match_index = df.index[df['ID'] == match_ID].tolist()[0]
    participant_info = df.iloc[participant_index]
    match_info = df.iloc[match_index]
    
    participant_name = participant_info["Name"]
    participant_email = participant_info["Email"]
    match_name = match_info["Name"]
    match_hobbies = match_info["Hobbies"]
    match_hobbies_as_str = ", ".join(match_hobbies)
    match_email = match_info["Email"]
    message = f"""Hi {participant_name},
The data has been crunched through, and a friend has been found!
Their information is as follows:
    
Name: {match_name}
Hobbies: {match_hobbies_as_str}
Email: {match_email}
    
Your match has also been send an email with your information. Whatever happens next is up to you guys!

Have fun and stay safe,
Operation Cordial"""
    
    emails_to_send[participant_email] = message
        

# In[589]:


emails_to_send


# In[564]:

# An email to test the email sending function
test_name = "Bobby"
test_emails = {'...@gmail.com': f"""
Hello, this is a test!
Lol
HAve fun {test_name}
The email is ..

Stay Safe,
Operation Cordinal
"""}


# In[590]:

#sending the actual emails
import smtplib

for email, message in emails_to_send.items():
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        SENDER = 'operationcordial@gmail.com'
        reciever = email
        smtp.login('operationcordial@gmail.com', 'PASSWORD')
        subject = "Your Operation Cordial Match!"
        body = message
        msg = f'Subject: {subject}\n\n{body}'
        smtp.sendmail(SENDER, reciever, msg)


# In[ ]:




