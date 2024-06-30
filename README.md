**Anime Recommendation System**

Link: https://anime-recommender-proto-1.streamlit.app/

This project aims to provide users with the ease of recommending anime that matches the likes of the content of the anime they want to be recommended. This project utilises Content based filtering techniques to accomplish the job of recommendation.

Tech Stack:
1. Python (Obviously)
2. Streamlit (for deployment and interface)
3. Scikit Learn (for data preprocessing and inference)
4. Pandas (for data cleaning and preprocessing)
5. Numpy
6. Jikan API (for fetching posters)

Working:
This project utilises content based filter for filtering the vectorised tags of the anime. In simple words it finds top K closest neighbours of the vectorised tags and displays the output.
In the notebook we tried to implement the finding of the K nearest neighbours, but had to finally implement it using Scikit Learn because of the fast optimizations and processing of huge datasets.
Finally we used a custom function of form a1 * (likelihood metric) + a2 * (popularity metric) + a3 * (rating metric). This was done as a result to overcome the recommendation of the animes purely on the based of tags which led to recommendation of poorly rated animes.
Of course, a1 was given the highest weight and the other two were heuristically chosen.

Deployment:
This ML model was deployed on Streamlit with a functionality that always displayed the top 10 popular animes. Upon searching it displayed the top 10 most related anime.

Challenges:
On the initial run, streamlit always refreshed the page when ever search was clicked, or the search bar was emptied to incorporate new search, which led to hanging of the web app during this reload interval. The posters too took quite a long time to be fetched and depened upon the connection.
To overcome that, I cached the predictions and posters data in a dictionary which did increase the memory limit but atleast got rid of the hanging of the system during the reload period.

Afterword:
A more refined data structure could be implemented that would store the details of the most frequently queried anime along with its poster and any collaboration help would be highly appreciated.

Hope you like this project.
