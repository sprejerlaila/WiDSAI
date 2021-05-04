#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 08:03:28 2020

@author: lsprejer
"""
import json
import numpy as np
import pandas as pd
import datetime

def profile_stats(profiles):
    id, debug_idx, names = [], [], []
    contacts, n_skills = [], []
    ages = []
    linkedin_locations = []
    
    for idx, profile in enumerate(profiles):
        p = json.loads(profile)
        id.append(p['id'])
        debug_idx.append(str(idx))
        names.append(p['name'])
        try:
            contacts.append(int(p['contacts'].replace('connections',"").replace('+',"").strip()))
        except:
#             print(idx)
            contacts.append(np.nan)
        
        try:
            skills = []
            for key, values in p['skills'].items():
                for skill in values:
                    skills.append(skill[0])
            n_skills.append(len(set(skills)))
        except:
            n_skills.append(len(set(p['skills'])))
        
        age = 0
        educations = p['education']
        for education in educations[::-1]:
            if any(b in education['degree'] for b in ["Bachelor", "\\bBA\\b", "BS"]):
                try:
                    age = 2020 - int(education['date_range'][:4]) + 18
                    break
                except:
                    #print(p['id'])
                    pass
        ages.append(age)
        l_idx = 0
        while l_idx < len(p['jobs']):
            try:
                loc = p['jobs'][l_idx]['location']
                if loc != "":
                    break
            except:
                pass
            l_idx += 1

        linkedin_locations.append(loc)
    
    df = pd.DataFrame({"debug":debug_idx, "id":id,"name":names, "age":ages,
                         "contacts":contacts, "n_skills":n_skills, 'linkedin_loc':linkedin_locations})

    return df.drop_duplicates('id')

def process_skills(profiles):
    ### TODO reclasify top_skills into one of the other categories!!
    id, debug_idx, names = [], [], []
    top_skills, industry_knowledge, tools, interpersonal, other, languages = [], [], [], [], [], []
    n_skills_industry, n_skills_tools, n_skills_interp, n_skills_other, n_skills_languages = [], [], [], [], []
    
    for idx, profile in enumerate(profiles):
        p = json.loads(profile)
        if 'top_skills' not in p['skills']: 
            continue
        id.append(p['id'])
        debug_idx.append(str(idx))
        names.append(p['name'])
        
        top_skills.append(p['skills']['top_skills'])
        
        if 'Industry Knowledge' in p['skills']:
            industry_knowledge.append(p['skills']['Industry Knowledge'])
            n_skills_industry.append(len(p['skills']['Industry Knowledge']))
            
        else:
            industry_knowledge.append([])
            n_skills_industry.append(0)
        
        if 'Tools & Technologies' in p['skills']:
            tools.append(p['skills']['Tools & Technologies'])
            n_skills_tools.append(len(p['skills']['Tools & Technologies']))
        else:
            tools.append([])
            n_skills_tools.append(0)
        
        if 'Interpersonal Skills' in p['skills']:
            interpersonal.append(p['skills']['Interpersonal Skills'])
            n_skills_interp.append(len(p['skills']['Interpersonal Skills']))

        else:
            interpersonal.append([])
            n_skills_interp.append(0)
            
        if 'Other Skills ' in p['skills']:
            other.append(p['skills']['Other Skills '])
            n_skills_other.append(len(p['skills']['Other Skills ']))

        else:
            other.append([])
            n_skills_other.append(0)
            
        if 'Languages' in p['skills']:
            languages.append(p['skills']['Languages'])
            n_skills_languages.append(len(p['skills']['Languages']))

        else:
            languages.append([])
            n_skills_languages.append(0)
            
    df = pd.DataFrame({"debug":debug_idx, "id":id,"name":names, 
                         "top_skills":top_skills, "industry_knowledge":industry_knowledge, "tools":tools, \
                       "interpersonal":interpersonal, "other":other, "languages":languages, \
                       "n_skills_industry":n_skills_industry, "n_skills_tools":n_skills_tools, "n_skills_interp":n_skills_interp,
                       "n_skills_other":n_skills_other, "n_skills_languages":n_skills_languages})
    
    df['n_skills'] = df.n_skills_industry + df.n_skills_tools + df.n_skills_interp + df.n_skills_other + df.n_skills_languages

    return df.drop_duplicates('id')


def get_long_jobs(profiles):
    id, debug_idx, names = [], [], []
    position, company, industry, employees = [], [], [], []
    start_date, end_date, duration = [], [], []

    collected_ids = set()
    remove_ids = []
    
    for idx, profile in enumerate(profiles):
        p = json.loads(profile)
        if 'id' not in p or p['id'] in collected_ids:
            continue
        collected_ids.add(p['id'])
            
        jobs = p['jobs']
        for job in jobs:
            if job['position'] == '':
                remove_ids.append(p['id'])
                continue
            if job['company'] == "":
                remove_ids.append(p['id'])
            try:
                date1, date2 = job['date_range'].split("–")
            except:
                continue
            if date2.strip() == "Present":
                date2 = "Nov 2020"
            try:
                date1 = datetime.datetime.strptime(date1.strip(), "%b %Y")
            except:
                date1 = datetime.datetime.strptime(date1.strip(), "%Y")
                #continue
            try:
                date2 = datetime.datetime.strptime(date2.strip(), "%b %Y")
            except:
                date2 = datetime.datetime.strptime(date2.strip(), "%Y")
                #continue
                
            n_months = (date2.year - date1.year) * 12 + (date2.month - date1.month)
            n_months = 0 if n_months < 0 else n_months ## When jobs last less than a year they sometimes don't specify an end date.
                
            
            position.append(job['position'])
            company.append(job['company']['name'])
            industry.append(job['company']['industry'])
            employees.append(job['company']['employees'])
            start_date.append(date1)
            end_date.append(date2)
            duration.append(n_months)
            id.append(p['id'])
            debug_idx.append(idx)
            names.append(p['name'])
    
    df = pd.DataFrame({"debug":debug_idx, "id":id,"name":names, 
                         "role":position, "company":company, "industry":industry, \
                         'employees':employees, "start_date":start_date, "end_date":end_date,\
                        "duration":duration})
#    print(len(df))
    df = df[~df.id.isin(remove_ids)]
#    print(len(df))
    return df

def get_long_education(profiles):
    id, debug_idx, names = [], [], []
    institution, degree, discipline, location = [], [], [], []
    start_date, end_date, duration = [], [], []

    collected_ids = set()
    remove_ids = []
    
    for idx, profile in enumerate(profiles):
        p = json.loads(profile)
        if 'id' not in p or p['id'] in collected_ids:
            continue
        collected_ids.add(p['id'])
            
        jobs = p['education']
        for job in jobs:
            if job['institution'] == '':
            #    remove_ids.append(p['id'])
                continue
            # if job['degree'] == "":
            #     remove_ids.append(p['id'])
            try:
                date1, date2 = job['date_range'].split("–")
            except:
                continue
            
            try:
                date1 = datetime.datetime.strptime(date1.strip(), "%b %Y")
            except:
                date1 = datetime.datetime.strptime(date1.strip(), "%Y")
                #continue
            try:
                date2 = datetime.datetime.strptime(date2.strip(), "%b %Y")
            except:
                date2 = datetime.datetime.strptime(date2.strip(), "%Y")
                #continue
                
            n_months = date2.year - date1.year
            n_months = 0 if n_months < 0 else n_months ## When jobs last less than a year they sometimes don't specify an end date.
                
            
            institution.append(job['institution'])
            degree.append(job['degree'])
            discipline.append(job['discipline'])
            location.append(job['location'])
            start_date.append(date1)
            end_date.append(date2)
            duration.append(n_months)
            id.append(p['id'])
            debug_idx.append(idx)
            names.append(p['name'])
    
    df = pd.DataFrame({"debug":debug_idx, "id":id,"name":names, 
                         "institution":institution, "degree":degree, "discipline":discipline, \
                         'location':location, "start_date":start_date, "end_date":end_date,\
                        "duration":duration})
#    print(len(df))
    df = df[~df.id.isin(remove_ids)]
#    print(len(df))
    return df
    
    