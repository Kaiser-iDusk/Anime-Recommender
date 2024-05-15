import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests

# def recommend_popularity(charts):
#     ret = []
#     for i in range(10):
#         name = charts['name'].iloc[i]
#         rating = charts['rating'].iloc[i]
#         genre = charts['tags'].iloc[i]

#         ret.append([name, rating, genre])
#     return ret

# def get_id(name, data):
#     return data[data['name']==name]['anime_id'].to_numpy()[0]
    
# def get_index(id, data):
#     return data[data['anime_id']==id].index[0]

# def knn(query, knowledge, frame):
#     train_vec = []
#     for i, s in knowledge:
#         train_vec.append([int(i), s, frame['rating'].iloc[int(i)], frame['members'].iloc[int(i)]])
#     query = np.array(query).reshape(1, -1)
#     train_vec = np.array(train_vec)
#     distances = []
#     for i in train_vec:
#         val = (0.65*(query[0][0]-i[1])**3 + 0.05*(query[0][1]-i[2])**3 + 0.3*(query[0][2]-i[3])**3)**(1/3)
#         # print(val)
#         distances.append([i[0], val])
#     return np.array(distances)

# def recommend(name, data, frame):
#     index = get_index(get_id(name, frame), frame)
#     anime_tr = data[index].reshape(-1,2)
#     print(anime_tr.shape)
#     final = np.array(sorted(knn([1.0, frame[frame['name'] == name]['rating'].to_numpy()[0], frame[frame['name'] == name]['members'].to_numpy()[0]], anime_tr, frame), key=lambda x: x[1]))
#     final = final[: 25]
#     final_list = sorted(final, key = lambda x: -frame['rating'].iloc[int(x[0])])[:11]
#     final_list = sorted(final_list, key = lambda x: -frame['members'].iloc[int(x[0])])
#     # for i, d in final_list:
#     #     print(f"Name: {frame['name'].iloc[int(i)]} | Tags: {frame['tags'].iloc[int(i)]} | Popularity: {frame['rating'].iloc[int(i)]} | Fans: {frame['members'].iloc[int(i)]}")
#     return final_list

class Anime_Recommender_System:
    paths = {
        'anime_data': 'anime_series.pkl',
        'popular_anime': 'popular_series.pkl',
        'distances': 'proto.pkl',
        'df': 'df.pkl'
    }

    home_page_posters = []
    home_page_recommendations = []

    def __init__(self):
        self.anime_data = pickle.load(open(self.paths['anime_data'], "rb"))
        self.popular_anime = pickle.load(open(self.paths['popular_anime'], "rb"))
        self.df = pickle.load(open(self.paths['df'], "rb"))
        self.data = pickle.load(open(self.paths['distances'], "rb"))
    
    def fetch_poster(self, given_name):
        url = f"https://api.jikan.moe/v4/anime?q={given_name}&nsfw"
        response = requests.get(url)
        # print(response.status_code)
        if response.status_code == 401 or response.status_code == 402 or response.status_code == 403 or response.status_code == 404:
            data_rec = {"data": [{"images": {"jpg": {"image_url": "https://th.bing.com/th/id/OIP.dXRPKVT4ML_eVnJzukJ8MQAAAA?rs=1&pid=ImgDetMain"}}}]}
        else:
            # print(url, given_name)
            data_rec = response.json()
        
        image_path = data_rec["data"][0]["images"]["jpg"]["image_url"]
        return image_path
    
    def make_home_page(self):
        recommendations = self.home_page_recommendations
        if len(recommendations) == 0:
            recommendations = self.recommend_popularity()
        
        posters_pop = []
        if len(self.home_page_posters) == 0:
            for n, r, g in recommendations:
                name = n.replace('&quot;', '')
                posters_pop.append(self.fetch_poster(name))
            self.home_page_posters = posters_pop
        else:
            posters_pop = self.home_page_posters
        
        return recommendations, posters_pop

    def recommend_popularity(self):
        ret = []
        for i in range(10):
            name = self.popular_anime['name'].iloc[i]
            rating = self.popular_anime['rating'].iloc[i]
            genre = self.popular_anime['tags'].iloc[i]

            ret.append([name, rating, genre])
        return ret
    
    def get_id(self, name, data):
        return data[data['name']==name]['anime_id'].to_numpy()[0]
        
    def get_index(self, id, data):
        return data[data['anime_id']==id].index[0]

    def knn(self, query, knowledge):
        train_vec = []
        for i, s in knowledge:
            train_vec.append([int(i), s, self.df['rating'].iloc[int(i)], self.df['members'].iloc[int(i)]])
        query = np.array(query).reshape(1, -1)
        train_vec = np.array(train_vec)
        distances = []
        for i in train_vec:
            val = (0.65*(query[0][0]-i[1])**3 + 0.05*(query[0][1]-i[2])**3 + 0.3*(query[0][2]-i[3])**3)**(1/3)
            # print(val)
            distances.append([i[0], val])
        return np.array(distances)

    def recommend(self, name):
        index = self.get_index(self.get_id(name, self.df), self.df)
        anime_tr = self.data[index].reshape(-1,2)
        print(anime_tr.shape)
        final = np.array(sorted(self.knn([1.0, self.df[self.df['name'] == name]['rating'].to_numpy()[0], self.df[self.df['name'] == name]['members'].to_numpy()[0]], anime_tr), key=lambda x: x[1]))
        final = final[: 25]
        final_list = sorted(final, key = lambda x: -self.df['rating'].iloc[int(x[0])])[:11]
        final_list = sorted(final_list, key = lambda x: -self.df['members'].iloc[int(x[0])])
        # for i, d in final_list:
        #     print(f"Name: {frame['name'].iloc[int(i)]} | Tags: {frame['tags'].iloc[int(i)]} | Popularity: {frame['rating'].iloc[int(i)]} | Fans: {frame['members'].iloc[int(i)]}")
        return final_list

system = Anime_Recommender_System()

# anime_data = pickle.load(open('anime_series.pkl', "rb"))
# popular_charts = pickle.load(open('popular_series.pkl', "rb"))
# similarity = pickle.load(open('proto.pkl', "rb"))
# df = pickle.load(open('df.pkl', "rb"))

st.title("Anime Recommendation Website")

anime_name = st.selectbox("Choose Anime", system.anime_data['name'].values)

if st.button("Submit"):
    cnt = 0
    recommended = system.recommend(anime_name)
    posters = []
    for i, s in recommended:
        name = system.df['name'].iloc[int(i)]
        name = name.replace('&quot;', '')
        posters.append(system.fetch_poster(name))

    with st.container():
        for r in range(2):
            cols = st.columns(5)
            for col in cols:
                with col:
                    # print(len(recommended))
                    cnt += 1
                    idx = 5*r + (cnt%5)
                    id = recommended[idx][0]
                    name = system.df['name'].iloc[int(id)]
                    name = name.replace('&quot;', '')
                    name = name.replace('&#039;', '')
                    # print(name, fetch_poster(name))
                    st.image(posters[idx])
                    st.write(f"Name: {name}")
                    pop = system.df['rating'].iloc[int(id)]
                    st.write(f"Rating: {pop}/10")
                    anime_id = system.df['anime_id'].iloc[int(id)]


with st.container():
    st.header("Popular Charts:")
    recommendations, posters_pop = system.make_home_page()

    counter = 0

    for r in range(2):
        cols = st.columns(5)
        for col in cols:
            with col:
                st.image(posters_pop[counter-1])
                st.write(f"{recommendations[counter][0]}")
                st.write(f"Rating: {recommendations[counter][1]} / 10")
                counter += 1
            