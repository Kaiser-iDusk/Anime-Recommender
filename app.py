import streamlit as st
import numpy as np
import pickle
import requests
import time
import pandas as pd

class Anime_Recommender_System:
    paths = {
        'anime_data': 'anime_series.pkl',
        'popular_anime': 'popular_series.pkl',
        'distances': 'proto.pkl',
        'df': 'df.pkl',
        'posters': 'posters.csv',
        'pop_rec': 'pop_rec.csv'
    }

    def __init__(self):
        self.anime_data = pickle.load(open(self.paths['anime_data'], "rb"))
        self.popular_anime = pickle.load(open(self.paths['popular_anime'], "rb"))
        self.df = pickle.load(open(self.paths['df'], "rb"))
        self.data = pickle.load(open(self.paths['distances'], "rb"))
    
    def fetch_poster(self, given_name):
        url = f"https://api.jikan.moe/v4/anime?q={given_name}&nsfw"
        response = requests.get(url)
        # print(response.status_code)
        if response.status_code >= 400 and response.status_code <= 404:
            data_rec = {"data": [{"images": {"jpg": {"image_url": "https://th.bing.com/th/id/OIP.dXRPKVT4ML_eVnJzukJ8MQAAAA?rs=1&pid=ImgDetMain"}}}]}
        elif response.status_code == 429:
            time.sleep(1)
            print(f"Looping for: {given_name}")
            return self.fetch_poster(given_name)
        else:
            # print(url, given_name)
            data_rec = response.json()
        
        image_path = data_rec["data"][0]["images"]["jpg"]["image_url"]
        return image_path
    
    def make_home_page(self): 
        print("Here")
        recommendations = pd.read_csv(self.paths['pop_rec'], skiprows=0)
        # print(len(self.home_page_recommendations))
        if len(recommendations) < 10:
            print("Working 1")
            recommendations = self.recommend_popularity()
            recommendations = pd.DataFrame(recommendations)
            print(recommendations)
            recommendations.to_csv(self.paths['pop_rec'], header = True, index=False)
        
        recommendations = recommendations.to_numpy()
        
        print(recommendations)
        posters_pop = pd.read_csv(self.paths['posters'], skiprows=0)

        if len(posters_pop) < 10:
            print("Working 2")
            temp = []
            for n, r, g in recommendations:
                name = n.replace('&quot;', '')
                temp.append(self.fetch_poster(name))
            posters_pop = temp
            posters_pop = pd.DataFrame(posters_pop)
            posters_pop.to_csv(self.paths['posters'], header = True, index=False)
        
        posters_pop = posters_pop.to_numpy().reshape(-1,)
        print(posters_pop.shape)
        
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
    print("Home")
    recommendations, posters_pop = system.make_home_page()

    counter = 0

    for r in range(2):
        cols = st.columns(5)
        for col in cols:
            with col:
                st.image(posters_pop[counter])
                st.write(f"{recommendations[counter][0]}")
                st.write(f"Rating: {recommendations[counter][1]} / 10")
                counter += 1
            