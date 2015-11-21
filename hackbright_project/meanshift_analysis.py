import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from model import Ticket, Agent, Customer, Company, connect_to_db, db

def get_data(tickets):
    industries = {'media':1, 'financial services':2, 'consulting':3, 'transportation':4,
    'technology':5, 'energy':6}
    
    support_tiers = {'Gold':1, 'Silver':2, 'Bronze':3}
    
    pilot = {'Yes':1, 'No':0}

    locations = {'San Francisco, CA': 1, 'Redwood City, CA': 2, 'Foster City, CA': 3, 'Los Angeles, CA': 4,
                 'San Diego, CA': 5, 'Eugene, OR': 6, 'Seattle, WA': 7, 'Madison, WI': 8, 'Chicago, IL': 9, 
                 'Ann Arbor, MI': 10, 'Detroit, MI': 11, 'Syracuse, NY': 12, 'New York, NY': 13, 'Brooklyn, NY': 14, 
                 'Fairfield, CT': 15, 'Priceton, NJ': 16, 'Boston, MA': 17,  'London, UK': 19, 'Munich, Germany': 20,
                 'Berlin, Germany': 21 }

    agent_names = {'Xye Dagun': [0,1], 'Kayla Smith': [0,1], 'Stephanie Nguyen': [0,1], 'Christina Foran': [0,1],
              'Blake Gilmore': [0,1], 'Erica Johnson': [0,1], 'Brandi Day': [0,1], 'Julia Guenther': [0,1]}

    sentiment_numbers = {'neg': 1, 'neutral': 2, 'pos': 3}

    feature_list = []
    ticket_list = []
    sentiment_list = []
    certainty_list = []

    for ticket in tickets:
        ticket_customer = Customer.query.filter(ticket.customer_id == Customer.id).first()
        ticket_company = Company.query.filter(Company.id == ticket_customer.company_id).first()
        ticket_agent = Agent.query.filter(ticket.agent_id == Agent.id).first()
        #Get the number corresponding to the industry that each ticket is in 
        industry = ticket_company.industry
        industry_number = industries[industry]
        
        support_tier = ticket_company.support_tier
        support_number = support_tiers[support_tier]
        
        is_pilot = ticket_company.is_pilot
        pilot_number = pilot[is_pilot]

        location = ticket_company.location
        location_number = locations[location]

        ticket_list.append(ticket.ticket_id)

        sentiment = ticket.ticket_sentiment
        sentiment_number = sentiment_numbers[sentiment]
        sentiment_list.append(sentiment_number) 

        percent_certainty = ticket.percent_certainty
        certainty_list.append(percent_certainty)

        

        #text_score 

        ticket_agent = Agent.query.filter(Agent.id == ticket.agent_id).first()
        agent_name = ticket_agent.name
        agents_on_ticket = []
        for x in agent_names:
            if x == agent_name:
                agents_on_ticket.append(1)
            else:
                agents_on_ticket.append(0)
        print "Got to here!"
        features_per_ticket = []
        features_per_ticket.extend([industry_number, support_number, pilot_number, location_number])
        features_per_ticket.extend(agents_on_ticket)
        features_per_ticket.append(sentiment_number)

        feature_list.append(features_per_ticket)
    
    feature_list_np = np.array(feature_list, float)

    bandwidth = estimate_bandwidth(feature_list_np, quantile=0.2)
    print "BANDWIDTH:", bandwidth

    ms = MeanShift(bandwidth=bandwidth)
    ms.fit(feature_list_np)
    labels = ms.labels_
    print labels

    # make a label_count_dict, to osee distribution
    label_count_dict = {}
    for lab in list(labels):
        label_count_dict[lab] = label_count_dict.get(lab, 0) + 1

    print "LABELS DICT:", label_count_dict

    cluster_centers = ms.cluster_centers_

    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    print("number of estimated clusters : %d" % n_clusters_)


    processed_clusters = zip(labels, ticket_list, sentiment_list, certainty_list)
    
    data =process_clusters(processed_clusters)
    return data
    return processed_clusters


def process_clusters(ticket_details):
    cluster_1 = {'neg':0, 'neutral':0, 'pos':0}
    cluster_2 = {'neg':0, 'neutral':0, 'pos':0}
    cluster_3 = {'neg':0, 'neutral':0, 'pos':0}
    cluster_4 = {'neg':0, 'neutral':0, 'pos':0}

    cluster_dict = {}

    for ticket in ticket_details:
        cluster_label = ticket[0]
        ticket_id = ticket[1]
        sentiment = ticket[2]
        certainty = ticket[3]
        if cluster_label == 0:
            if sentiment == 1:
                cluster_1['neg'] += 1
            elif sentiment == 2:
                cluster_1['neutral'] += 1
            else:
                cluster_1['pos'] += 1
        elif cluster_label == 1:
            if sentiment == 1:
                cluster_2['neg'] += 1
            elif sentiment == 2:
                cluster_2['neutral'] += 1
            else:
                cluster_2['pos'] += 1
        elif cluster_label == 2:
            if sentiment == 1:
                cluster_3['neg'] += 1
            elif sentiment == 2:
                cluster_3['neutral'] += 1
            else:
                cluster_3['pos'] += 1
        elif cluster_label == 3:
            if sentiment == 1:
                cluster_4['neg'] += 1
            elif sentiment == 2:
                cluster_4['neutral'] += 1
            else:
                cluster_4['pos'] += 1
    
    cluster_dict = {'cluster1':cluster_1,'cluster2':cluster_2, 'cluster3':cluster_3, 'cluster4':cluster_4}

    return cluster_dict
    
    def create_scatterplot(ticket_details):
        pass
    





