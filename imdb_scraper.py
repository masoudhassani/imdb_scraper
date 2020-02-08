from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

'''
get the content of a url as text. in case of error, returns None
'''
def _get_content(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if _is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

'''
    check if url text content is html
'''
def _is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

''' 
    function to extract metascore from an imdb url
    metascore is converted to the range of 0~10
    returns N/A if metascore is not found
'''
def get_metascore(url):
    score = 'N/A'
    content = _get_content(url)
    soup = BeautifulSoup(content, features='html.parser')

    div = (soup.find_all('div', class_='titleReviewBarItem'))
    score_list = div[0].span.contents

    if len(score_list) == 1:
        score = int(score_list[0]) / 10
    else:
        score = None

    return score

''' 
    function to extract metascore from a pandas data frame with column labeled 'URL'
    metascore is converted to the range of 0~10
    metascore is returned as list 
'''
def generate_metascore_list(df):
    meta_score = []
    print ('Extracting meta score from IMDB. This may take several minutes ...')

    num_data = len(df.index)
    for i in range(num_data):
        url = df.loc[i,'URL']
        score = get_metascore(url)
        print (url, '  ', score, '  ', int(i*100/num_data), '% completed')
        # use imdb rating for data that do not have meta score
        if score == None:
            score = df.loc[i,'IMDb Rating']
        meta_score.append(score)

    return meta_score

'''
    extracts data related to a movie title from imdb.com
    data includes imdb rating, meta score, name, genre, year
'''
def get_movie_data(url):
    print ('fetching movie data from IMDB')
    content = _get_content(url)
    soup = BeautifulSoup(content, features='html.parser')

    # find imdb rating
    div = (soup.find_all('div', class_='ratingValue'))
    rating_list = div[0].span.contents
    if len(rating_list) == 1:
        imdb_rating = float(rating_list[0])
    else:
        imdb_rating = None

    # find movie title
    title = (soup.find_all('h1', class_=''))
    movie_title = title[0].contents[0]

    # find meta score
    div = (soup.find_all('div', class_='titleReviewBarItem'))
    score_list = div[0].span.contents
    if len(score_list) == 1:
        meta_score = int(score_list[0]) / 10
    else:
        meta_score = None

    # find movie gnere, production year and release date
    div = (soup.find_all('div', class_='title_wrapper'))
    soup = BeautifulSoup(str(div), features='html.parser')
    a_list = (soup.find_all('a', class_=''))
    genres = []
    for i in range(len(a_list)):
        if i == 0:
            movie_year = a_list[i].contents[0]
        elif i != len(a_list)-1 :
            genres.append(a_list[i].contents[0])
        else:
            release_date = a_list[i].contents[0]

    return imdb_rating, movie_title, meta_score, genres

