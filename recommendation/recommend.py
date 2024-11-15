# import numpy as np
# import pandas as pd
# from datetime import datetime
# from sklearn.neighbors import NearestNeighbors
# from .models import UserSearch

# def get_search_data():
#     search_data = UserSearch.objects.values('user_id', 'search_query', 'created_at')
#     df = pd.DataFrame(search_data)

#     # Count frequency of each search query per user and get the most recent date for each query
#     frequency_df = df.groupby(['user_id', 'search_query']).size().reset_index(name='frequency')
#     frequency_df['created_at'] = df.groupby(['user_id', 'search_query'])['created_at'].max().values

#     return frequency_df

# def calculate_weighted_frequency(search_data):
#     # Current time for calculating recency
#     now = pd.Timestamp.now()

#     # Calculate recency weight based on time decay
#     search_data['recency_weight'] = (now - search_data['created_at']).dt.total_seconds()
#     search_data['recency_weight'] = np.exp(-search_data['recency_weight'] / (60 * 60 * 24))  # Decay over days

#     # Weighted frequency = frequency * recency weight
#     search_data['weighted_frequency'] = search_data['frequency'] * search_data['recency_weight']

#     return search_data

# def generate_recommendations(user_id):
#     # Step 1: Get search data and calculate weighted frequency
#     df = get_search_data()

#     if df.empty:
#         print("No user search data available.")
#         return []

#     weighted_df = calculate_weighted_frequency(df)

#     # Step 2: Convert to pivot table with weighted frequencies
#     search_matrix = weighted_df.pivot_table(index='user_id', columns='search_query', values='weighted_frequency', fill_value=0)
#     print("Pivoted Search Matrix with Weighted Frequencies:\n", search_matrix)

#     if user_id not in search_matrix.index:
#         print("User ID not found in search matrix.")
#         return []

#     # Step 3: Fit the Nearest Neighbors model
#     model = NearestNeighbors(metric='cosine', algorithm='brute')
#     model.fit(search_matrix)

#     # Step 4: Find nearest neighbors
#     user_index = search_matrix.index.get_loc(user_id)
#     n_neighbors = min(5, search_matrix.shape[0] - 1)

#     if n_neighbors <= 0:
#         print("Not enough neighbors for recommendation.")
#         return []

#     distances, indices = model.kneighbors(search_matrix.iloc[user_index].values.reshape(1, -1), n_neighbors=n_neighbors + 1)
#     recommended_indices = indices.flatten()[1:]  # Skip first index (user’s own)

#     # Step 5: Collect recommended queries from similar users
#     recommended_queries = []
#     for idx in recommended_indices:
#         similar_user_id = search_matrix.index[idx]
#         user_queries = df[df['user_id'] == similar_user_id]['search_query'].unique()
#         recommended_queries.extend(user_queries)

#     recommended_queries = list(set(recommended_queries))  # Ensure unique recommendations
#     print("Recommended Queries:", recommended_queries)
#     return recommended_queries

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from .models import UserSearch

def get_search_data():
    search_data = UserSearch.objects.values('user_id', 'search_query', 'created_at')
    df = pd.DataFrame(search_data)

    # Count frequency of each search query per user and get the most recent date for each query
    frequency_df = df.groupby(['user_id', 'search_query']).size().reset_index(name='frequency')
    frequency_df['created_at'] = df.groupby(['user_id', 'search_query'])['created_at'].max().values

    return frequency_df

def calculate_weighted_frequency(search_data):
    # Current time for calculating recency
    now = pd.Timestamp.now()

    # Calculate recency weight based on time decay
    search_data['recency_weight'] = (now - search_data['created_at']).dt.total_seconds()
    search_data['recency_weight'] = np.exp(-search_data['recency_weight'] / (60 * 60 * 24))  # Decay over days

    # Weighted frequency = frequency * recency weight
    search_data['weighted_frequency'] = search_data['frequency'] * search_data['recency_weight']

    return search_data

def generate_recommendations(user_id):
    # Step 1: Get search data and calculate weighted frequency
    df = get_search_data()

    if df.empty:
        print("No user search data available.")
        return []

    weighted_df = calculate_weighted_frequency(df)

    # Step 2: Convert to pivot table with weighted frequencies
    search_matrix = weighted_df.pivot_table(index='user_id', columns='search_query', values='weighted_frequency', fill_value=0)
    print("Pivoted Search Matrix with Weighted Frequencies:\n", search_matrix)

    if user_id not in search_matrix.index:
        print("User ID not found in search matrix.")
        return []

    # Step 3: Fit the Nearest Neighbors model
    model = NearestNeighbors(metric='cosine', algorithm='brute')
    model.fit(search_matrix)

    # Step 4: Find nearest neighbors
    user_index = search_matrix.index.get_loc(user_id)
    n_neighbors = min(5, search_matrix.shape[0] - 1)

    if n_neighbors <= 0:
        print("Not enough neighbors for recommendation.")
        return []

    distances, indices = model.kneighbors(search_matrix.iloc[user_index].values.reshape(1, -1), n_neighbors=n_neighbors + 1)
    recommended_indices = indices.flatten()[1:]  # Skip first index (user’s own)

    # Step 5: Collect recommended queries from similar users, excluding the current user's own queries
    user_queries = set(df[df['user_id'] == user_id]['search_query'].unique())  # Current user's own queries
    recommended_queries = []
    
    for idx in recommended_indices:
        similar_user_id = search_matrix.index[idx]
        # Filter out queries that the user has already searched
        similar_user_queries = set(df[df['user_id'] == similar_user_id]['search_query'].unique())
        new_queries = similar_user_queries - user_queries  # Exclude current user's own queries
        recommended_queries.extend(new_queries)

    # Ensure unique recommendations and sort by frequency in descending order
    recommended_queries = list(set(recommended_queries))
    print("Recommended Queries:", recommended_queries)
    return recommended_queries

