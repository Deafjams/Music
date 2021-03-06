"""Load lastfm api data into neo4j"""
import py2neo

GRAPH = py2neo.Graph('bolt://neo4j:neo4j@localhost:7687')

def load_user_info(user):
    """Stores a lastfm user in neo4j

    Args:
        user (dict): lastfm user
    """
    user_node = GRAPH.find_one('User', property_key='name', property_value=user['name'])
    if user_node is None:
        user_node = py2neo.Node('User', **user)
        GRAPH.create(user_node)


def load_friendship(user, friend):
    """Stores a lastfm user's friend in neo4j

    Args:
        user (str): lastfm user name
        friend (str): lastfm user name
    """
    user_node = GRAPH.find_one('User', property_key='name', property_value=user)
    friend_node = GRAPH.find_one('User', property_key='name', property_value=friend)
    friendship = GRAPH.match_one(
        start_node=user_node,
        rel_type='FRIENDS',
        end_node=friend_node,
        bidirectional=True
    )

    if friendship is None:
        friendship = py2neo.Relationship(user_node, 'FRIENDS', friend_node)
        GRAPH.create(friendship)


def load_friendships(user, friends):
    """Convenience method for loading many lastfm friends

    Args:
        user (str): lastfm user name
        friends (list): list of lastfm user dicts
    """
    for friend in friends:
        load_user_info(friend)
        load_friendship(user, friend['name'])


def load_artist(artist):
    """Stores a lastfm artist in neo4j

    Args:
        artist (dict): lastfm artist
    """
    artist_node = GRAPH.find_one('Artist', property_key='url', property_value=artist['url'])

    if artist_node is None:
        artist_node = py2neo.Node('Artist', **artist)
        GRAPH.create(artist_node)


def load_plays(user, artist, playcount):
    """Stores a user's plays of an artist in neo4j

    Args:
        user (str): lastfm user name
        artist (dict): lastfm artist
    """
    user_node = GRAPH.find_one('User', property_key='name', property_value=user)
    artist_node = GRAPH.find_one('Artist', property_key='url', property_value=artist['url'])
    plays = GRAPH.match_one(
        start_node=user_node,
        rel_type='PLAYS',
        end_node=artist_node
    )

    if plays is None:
        plays = py2neo.Relationship(user_node, 'PLAYS', artist_node, **{'plays': playcount})
        GRAPH.create(plays)

    else:
        plays['playcount'] += playcount
        GRAPH.push(plays)


def load_user_weekly_artist_chart(user, artists):
    """Stores lastfm artists and players in neo4j

    Args:
        user (str): lastfm username
        artists (list): list of lastfm artists with playcount
    """
    for artist in artists:
        playcount = artist.pop('playcount', 0)

        load_artist(artist)
        load_plays(user, artist, playcount)
