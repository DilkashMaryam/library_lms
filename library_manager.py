import streamlit as st
import pandas as pd
import json
import os
import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

#set page config
st.set_page_config(page_title="Personal Library Manager",
                   page_icon="📚",
                   layout="wide",
                   initial_sidebar_state="expanded")

#custom css
st.markdown("""
<style>
    .main-header {
        background-color: #00008B;
        font-size: 2rem !important;
        color: #FFFFFF;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    .sub-header {
        font-size: 1.5rem !important;
        color: #FFFFFF;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #008000;
        padding: 1rem;
        border-radius: 0.375rem;
        border-left: 5px solid #808000;
        color: #FFFFFF;
        font-weight: 500;
    }
    .warning-message {
        background-color: #FFA500;
        padding: 1rem;
        border-radius: 0.375rem;
        border-left: 5px solid #808000;
        color: #FFFFFF;
        font-weight: 500;
    }
    .error-message {
        background-color: #FF0000;
        padding: 1rem;
        border-radius: 0.375rem;
        border-left: 5px solid #808000;
    }
    .book-card {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #808000;
        transition: transform 0.3s ease-in-out;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .read-progress {
        background-color: #008000;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        color: #FFFFFF;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .unread-progress {
        background-color: #FF0000;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        color: #FFFFFF;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .book-card-title {
        font-size: 1.25rem !important;
        font-weight: 600;
    }
    .action-button {
        margin-right: 0.5rem;
    }
    .stButton>button {
</style>
""", unsafe_allow_html=True)

#function to load data
def load_lottieurl(url):
    """Load and parse a Lottie animation from a URL.
    
    Args:
        url (str): The URL of the Lottie animation JSON.
        
    Returns:
        dict: The parsed Lottie animation data, or None if loading fails.
    """
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
                return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

#save library
def save_library():
    """Save the current library state to a JSON file.
    
    Returns:
        bool: True if save was successful, False otherwise.
    """
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
            return True
        return False
    except (IOError, OSError) as e:
        st.error(f"Error saving library: {e}")
        return False

#add a book to the library
def add_book(title, author, published_year, status, genre):
    book = {
        'title': title,
        'author': author,
        'published_year': published_year,
        'status': status if status in ["Read", "Unread"] else "Unread",
        'genre': genre,
        'added_date': datetime.datetime.now().strftime('%Y-%m-%d'),
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5) #animation delay

#remove a book from the library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

#search for a book
def search_book(search_query, search_type):
    search_query = search_query.lower()
    results = []
    for book in st.session_state.library:
        if search_type == 'title' and search_query in book['title'].lower():
            results.append(book)
        elif search_type == 'author' and search_query in book['author'].lower():
            results.append(book)
        elif search_type == 'genre' and search_query in book['genre'].lower():
            results.append(book)

    st.session_state.search_results = results

#calculate reading statistics
def calculate_reading_stats():
    if "library" not in st.session_state:
        return {"total_books": 0, "read_books": 0, "unread_books": 0}

    total_books = len(st.session_state.library)
    st.write(st.session_state.library)

    read_books = sum(1 for book in st.session_state.library if book.get('status', 'Unread').lower() == 'read')
    percent_read = round((read_books / total_books) * 100) if total_books > 0 else 0

    genre_counts = {}
    author_counts = {}
    decade_counts = {}

    for book in st.session_state.library:
        if 'status' not in book:
            book['status'] = "unread"  # Default value

        save_library()

        #genre counts
        if book['genre'] in genre_counts:
            genre_counts[book['genre']] += 1
        else:
            genre_counts[book['genre']] = 1

        #author counts
        if book['author'] in author_counts:
            author_counts[book['author']] += 1
        else:
            author_counts[book['author']] = 1

        #decade counts
        year = (book.get('published_year') // 10) * 10
        decade = str(year)[:3] + '0s'
        if decade in decade_counts:
            decade_counts[decade] += 1
        else:
            decade_counts[decade] = 1

    #sort by count
    genre_counts = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True))
    author_counts = dict(sorted(author_counts.items(), key=lambda x: x[1], reverse=True))
    decade_counts = dict(sorted(decade_counts.items(), key=lambda x: x[1], reverse=True))

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genre_counts': genre_counts,
        'author_counts': author_counts,
        'decade_counts': decade_counts
    }

def create_visualizations(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=.4,
            marker_color=['#008000', '#FF0000']
        )])
        fig_read_status.update_layout(
            title='Read Status Distribution',
            showlegend=True,
            height=400,
        )
        st.plotly_chart(fig_read_status, use_container_width=True)

        #genre bar chart
        if stats['genre_counts']:
            genres_df = pd.DataFrame(
                list(zip(stats['genre_counts'].keys(), stats['genre_counts'].values())),
                columns=['Genre', 'Count']
            )
            fig_genre = px.bar(
                genres_df,
                x='Genre',
                y='Count',
                color='Count',
                color_continuous_scale='px.colors.sequential.Viridis',
            )
            fig_genre.update_layout(
                title='Book by published decade',
                xaxis_title='Genres',
                yaxis_title='Number of Books',
                height=400,
            )
            st.plotly_chart(fig_genre, use_container_width=True)

    if stats['decade_counts']:
        decade_df = pd.DataFrame(
            list(zip([f"{decade}s" for decade in stats['decade_counts'].keys()], 
                    stats['decade_counts'].values())),
            columns=['Decade', 'Count']
        )
        fig_decade = px.line(
            decade_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape="spline",
        )
        fig_decade.update_layout(
            title='Books by published decade',
            xaxis_title='Decade',
            yaxis_title='Number of Books',
            height=400,
        )
        st.plotly_chart(fig_decade, use_container_width=True)

#load library
load_library()
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets.lottielibrary.com/l/book.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key='book_animation')

nav_options = st.sidebar.radio("Select an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"])

if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add_book"
elif nav_options == "Search Books":
    st.session_state.current_view = "search"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "statistics"

st.markdown("<h1 class='main-header'>Personal Library Manager</h1>", unsafe_allow_html=True)
if st.session_state.current_view == "add_book":
    st.markdown("<h2 class='sub-header'>Add a new book➕</h2>", unsafe_allow_html=True)
    
    with st.form(key='add_book_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title", placeholder="Enter the book title", max_chars=100)
            author = st.text_input("Author", placeholder="Enter the author's name", max_chars=100)
            year_input = st.number_input("Published Year", min_value=1000, max_value=datetime.datetime.now().year, step=1, value=2023)


    with col2:
        status = st.radio("Status", ["Read", "Unread"], horizontal=True)
        genre = st.selectbox("Genre", [
            "Fiction", "Non-Fiction", "Biography", "Science Fiction", 
            "Fantasy", "Mystery", "Romance", "Thriller", "Horror", 
            "Self-Help", "History", "Travel", "Cooking", "Art", "Programming", "Other"])

        submit_button = st.form_submit_button("Add Book")
        read_bool = status == "Read"

    if submit_button:
        if title and author and year_input:
            add_book(title, author, year_input, read_bool, genre)
            st.success("Book added successfully!")

    if st.session_state.book_added:
        st.markdown("<div class='success-message'>✅Book added successfully!</div>", unsafe_allow_html=True)
        st.balloons()
        st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>Your Library📚</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>No books in your library yet. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3 class='book-card-title'>{book['title']}</h3>
                    <p class='book-card-author'>{book['author']}</p>
                    <p class='book-card-year'>{book.get('published_year', 'N/A')}</p>
                    <p class='book-card-genre'>{book['genre']}</p>
                    <p><span class='{"read-badge" if book ["read_status"] else "unread-badge"}'>{
                        "Read" if book["read_status"] else "Unread"
                    }</span></p>
                    <button class='action-button' onclick="remove_book({i})">Remove</button>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Remove Book", key=f"remove_book_{i}"):
                        if remove_book(i):
                            st.rerun()

                with col2:
                    new_status = not book['status', 'Unread']
                    status_label = "Mark as read" if not book.get('status', 'Unread') == 'Unread' else "Mark as unread"
                    if st.button(status_label, key=f"status_{i}", use_container_width=True):
                        st.session_state.library[i]['status'] = "Read" if new_status else "Unread"
                        save_library()
                        st.rerun()

    if st.session_state.book_removed:
        st.markdown("<div class='sucess-message'>✅Book removed successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_removed = False

elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>Search for a book🔍</h2>", unsafe_allow_html=True)

    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter a search term:")

    if st.button("Search", use_container_width=False):
        if search_term:
            with st.spinner("Searching..."):
                time.sleep(0.5)
                search_book(search_term, search_by)

    if hasattr(st.session_state, 'search_results'):
        if st.session_state.search_results:
            st.markdown(f"<h2>Found {len(st.session_state.search_results)} results:</h2>", unsafe_allow_html=True)

            for i, book in enumerate(st.session_state.search_results):
                st.markdown(f"""
                <div class='book-card'>
                    <h3 class='book-card-title'>{book['title']}</h3>
                    <p class='book-card-author'>{book['author']}</p>
                    <p class='book-card-year'>{book['published_year']}</p>
                    <p class='book-card-genre'>{book['genre']}</p>
                    <p><span class='{"read-badge" if book ["read_status"] else "unread-badge"}'>{
                        "Read" if book["read_status"] else "Unread"
                    }</span></p>
                    <button class='action-button' onclick="remove_book({i})">Remove</button>
                </div>
                """, unsafe_allow_html=True)

        elif search_term:
            st.markdown("<div class='warning-message'>No results found. Try a different search term.</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "statistics":
    st.markdown("<h2 class='sub-header'>Library Statistics📊</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'>No books in your library yet. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        stats = calculate_reading_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats['total_books'])
        with col2:
            st.metric("Books Read", stats['read_books'])
        with col3:
            st.metric("Percentage Read", f"{stats['percent_read'] :.1f}%")

        create_visualizations(stats)

        if stats['authors']:
            st.markdown("<h3 class='sub-header'>Top Authors📚</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['author_counts'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}** : {count} books{'s' if count > 1 else ''}")

st.markdown("---")
st.markdown("Copyright @ 2025 Personal Library Manager. All rights reserved.", unsafe_allow_html=True)

                
