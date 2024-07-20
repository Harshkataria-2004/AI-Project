import streamlit as st
import pickle
import numpy as np
import pandas as pd  # Import pandas

# Load data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

# Set up the Streamlit app
st.set_page_config(page_title="Book Recommender System", page_icon=":books:", layout="wide")
st.markdown("""
    <style>
        .text-white {
            color: white;
        }
        .card-home, .card-recommend {
            background-color: #343a40;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: 0.3s;
            padding: 20px;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            height: 350px; /* Fixed height for uniformity */
            margin: 20px 0; /* Added top and bottom margin */
        }
        .card-home{
            height:420px
        }
        .card-home:hover, .card-recommend:hover {
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        }
        .card-img-top {
            border-radius: 10px 10px 0 0;
            max-width: 100%;
            height: 200px; /* Adjust as needed */
            object-fit: cover; /* Ensure images cover the area */
            display: block;
            margin: 0 auto; /* Center the image */
        }
        .card-title {
            text-transform: capitalize;
            font-weight: bold;
            margin-top: 10px;
        }
        .navbar-custom {
            background-color: #00a65a;
        }
        .navbar-custom .navbar-brand, 
        .navbar-custom .nav > li > a {
            color: white;
        }
        body {
            background-color: #212529;
            color: white;
        }
        .card-body {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

def index():
    st.markdown("<h1 style='font-size:50px; margin-top:20px;' class='text-white'>Top 50 Books</h1>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            for j in range(i, len(popular_df), 4):
                # Check if image URL is available
                if pd.notna(popular_df['Image-URL-M'].values[j]):
                    st.markdown(f"""
                        <div class="card-home">
                            <img class="card-img-top img-responsive" src="{popular_df['Image-URL-M'].values[j]}" alt="{popular_df['Book-Title'].values[j]}">
                            <div class="card-body">
                                <p class="card-title">{popular_df['Book-Title'].values[j]}</p>
                                <p>{popular_df['Book-Author'].values[j]}</p>
                                <p>Votes - {popular_df['num_ratings'].values[j]}</p>
                                <p>Rating - {popular_df['avg_rating'].values[j]:.2f}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

def recommend_ui():
    st.markdown("<h1 style='font-size:50px; margin-top:20px;' class='text-white'>Recommend Books</h1>", unsafe_allow_html=True)

    # Create a list of book titles for the dropdown
    book_titles = list(pt.index)
    
    # Create a text input for search with dropdown suggestions
    user_input = st.selectbox("Select a book:", options=book_titles)
    
    if st.button("Recommend") and user_input:
        recommend_books(user_input)

def recommend_books(user_input):
    try:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]
        
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            
            # Ensure 'avg_rating' exists in temp_df before accessing it
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            if 'avg_rating' in temp_df.columns:
                item.extend(list(temp_df.drop_duplicates('Book-Title')['avg_rating'].values))
            else:
                item.extend([None])  # Handle missing 'avg_rating'
            
            if pd.notna(item[2]):  # Only include items with an image URL
                data.append(item)
        
        st.markdown("<h1 style='font-size:50px; margin-top:20px;' class='text-white'>Recommended Books</h1>", unsafe_allow_html=True)
        cols = st.columns(4)
        for i, col in enumerate(cols):
            with col:
                for j in range(i, len(data), 4):
                    st.markdown(f"""
                        <div class="card-recommend">
                            <img class="card-img-top img-responsive" src="{data[j][2]}" alt="{data[j][0]}">
                            <div class="card-body">
                                <p class="card-title">{data[j][0]}</p>
                                <p>{data[j][1]}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
    except IndexError:
        st.error("Book not found. Please check the spelling or try another book.")

# Streamlit page navigation
page = st.sidebar.selectbox("Navigate", ["Home", "Recommend"])
if page == "Home":
    index()
else:
    recommend_ui()
