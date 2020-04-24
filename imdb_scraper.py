from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import logging
import json

class ImdbScraper:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.soup = ''

    """
    Attempts to get the content at `url` by making an HTTP GET request.
    returns text if it works, otherwise none
    note: function is copied from another source
    """
    def _get_content(self, url):
        try:
            with closing(get(url, stream=True)) as resp:
                if self._is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            logging.info('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    """
    Returns True if the response seems to be HTML, False otherwise.
    note: function is copied from another source
    """
    def _is_good_response(self, resp):
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)

    
    def _create_url(self, imdb_id):
        return 'https://www.imdb.com/title/' + imdb_id


    '''
    main function to return all data for a provided imdb id
    '''
    def get_movie_data(self, imdb_id):
        #logging.info('fetching data for movie with imdb id %s' %imdb_id)
        url = self._create_url(imdb_id)
        raw = None

        movie_data = {
            'genres': '',
            'image_url': '',
            'language': '',
            'content_rating': '',
            'num_votes': None,
            'imdb_rating': None,
            'meta_score': None,
            'summary': '',
            'synopsis': '',
            'production_year': None,
            'tags': ''
        }

        try:
            content = self._get_content(url)
            self.soup = BeautifulSoup(content, features='html.parser')
            raw = self.soup.find_all('script', type="application/ld+json")
            raw = raw[0].text.strip()
        except:
            logging.warn('content not found for %s' %imdb_id)

        if raw != None:
            json_table = json.loads(raw)
            try:
                movie_data['genres'] = json_table["genre"]
            except:
                pass
            
            try:
                movie_data['image_url'] = json_table["image"]
            except:
                pass

            try:
                movie_data['content_rating'] = json_table["contentRating"]
            except:
                pass

            try:
                movie_data['num_votes'] = int(json_table["aggregateRating"]["ratingCount"])
            except:
                pass

            try:
                movie_data['imdb_rating'] = float(json_table["aggregateRating"]["ratingValue"])
            except:
                pass

            try:
                movie_data['tags'] = json_table["keywords"]
            except:
                pass

            try:
                movie_data['synopsis'] = json_table["description"]
            except:
                pass

            try:
                date_published = json_table["datePublished"]
                year = date_published[:4]
                movie_data['production_year'] = year 
            except:
                pass

        try:
            raw = self.soup.find_all(class_='article', id="titleStoryLine")
            div = raw[0].find('div', class_='inline canwrap')
            summary = div.find('span').text.strip()
            movie_data['summary'] = summary
        except:
            pass

        metascore = self.get_metascore(soup=self.soup)
        movie_data['meta_score'] = metascore

        return movie_data

    '''
    returns metascore for a provided imdb id 
    '''
    def get_metascore(self, imdb_id=None, soup=None):
        if soup == None:
            url = self._create_url(imdb_id)
            content = self._get_content(url)
            soup = BeautifulSoup(content, features='html.parser')

        if imdb_id != None:
            logging.info('fetching metascore for movie with imdb id %s' %imdb_id)

        try:
            div = soup.find_all('div', class_='titleReviewBarItem')
            score_list = div[0].span.contents

            if len(score_list) == 1:
                score = int(score_list[0])
            else:
                score = None
        except:
            score = None

        return score

    '''
    returns imdb rating for a provided imdb id 
    '''
    def get_imdb_rating(self, imdb_id=None, soup=None):
        if soup == None:
            url = self._create_url(imdb_id)
            content = self._get_content(url)
            soup = BeautifulSoup(content, features='html.parser')

        if imdb_id != None:
            logging.info('fetching imdb rating for movie with imdb id %s' %imdb_id)

        div = (soup.find_all('div', class_='ratingValue'))
        rating_list = div[0].span.contents

        if len(rating_list) == 1:
            imdb_rating = float(rating_list[0])
        else:
            imdb_rating = None

        return imdb_rating

    '''
    returns movies generes, production year and release date
    '''
    def get_genre_year(self, imdb_id=None, soup=None):
        if soup == None:
            url = self._create_url(imdb_id)
            content = self._get_content(url)
            soup = BeautifulSoup(content, features='html.parser')

        if imdb_id != None:
            logging.info('fetching genre and year for movie with imdb id %s' %imdb_id)

        div = (soup.find_all('div', class_='title_wrapper'))
        new_soup = BeautifulSoup(str(div), features='html.parser')
        a_list = (new_soup.find_all('a', class_=''))

        genres = []
        production_year = None 
        release_date = None
        for i in range(len(a_list)):
            if i == 0:
                production_year = a_list[i].contents[0]
            elif i != len(a_list)-1 :
                genres.append(a_list[i].contents[0])
            else:
                release_date = a_list[i].contents[0]

        return genres, production_year, release_date
