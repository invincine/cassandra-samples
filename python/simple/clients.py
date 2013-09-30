# -*- coding: utf-8 -*-

from cassandra.cluster import Cluster
from cassandra.query import PreparedStatement
import logging

class SimpleClient:
    """
    A simple Cassandra client illustrating how to use the DataStax 
    Python driver.
    """

    session = None

    @classmethod
    def connect(self, nodes):
        cluster = Cluster(nodes)
        metadata = cluster.metadata
        self.session = cluster.connect()
        print('Connected to cluster: ', metadata.cluster_name)

    @classmethod
    def create_schema(self):
        self.session.execute("""
            CREATE KEYSPACE simplex WITH replication
                = {'class':'SimpleStrategy', 'replication_factor':3};
        """)
        self.session.execute("""
            CREATE TABLE simplex.songs (
                id uuid PRIMARY KEY,
                title text,
                album text,
                artist text,
                tags set<text>,
                data blob
            );
        """)
        self.session.execute("""
            CREATE TABLE simplex.playlists (
                id uuid,
                title text,
                album text,
                artist text,
                song_id uuid,
                PRIMARY KEY (id, title, album, artist)
            );
        """)
        print('Simplex keyspace and schema created.')

    @classmethod
    def load_data(self):
        self.session.execute("""
            INSERT INTO simplex.songs (id, title, album, artist, tags)
            VALUES (
                756716f7-2e54-4715-9f00-91dcbea6cf50,
                'La Petite Tonkinoise',
                'Bye Bye Blackbird',
                'Jos�phine Baker',
                {'jazz', '2013'}
            );
        """)
        self.session.execute("""
            INSERT INTO simplex.songs (id, title, album, artist, tags)
            VALUES (
                f6071e72-48ec-4fcb-bf3e-379c8a696488,
                'Die M�sch',
                'In Gold',
                'Willi Ostermann',
                {'k�lsch', '1996', 'birds'}
            );
        """)
        self.session.execute("""
            INSERT INTO simplex.songs (id, title, album, artist, tags)
            VALUES (
                fbdf82ed-0063-4796-9c7c-a3d4f47b4b25,
                'Memo From Turner',
                'Performance',
                'Mick Jager',
                {'soundtrack', '1991'}
            );
        """)
        self.session.execute("""
            INSERT INTO simplex.playlists (id, song_id, title, album, artist)
            VALUES (
                2cc9ccb7-6221-4ccb-8387-f22b6a1b354d,
                756716f7-2e54-4715-9f00-91dcbea6cf50,
                'La Petite Tonkinoise',
                'Bye Bye Blackbird',
                'Jos�phine Baker'
            );
        """)
        self.session.execute("""
            INSERT INTO simplex.playlists (id, song_id, title, album, artist)
            VALUES (
                2cc9ccb7-6221-4ccb-8387-f22b6a1b354d,
                f6071e72-48ec-4fcb-bf3e-379c8a696488,
                'Die M�sch',
                'In Gold',
                'Willi Ostermann'
            );
        """)
        self.session.execute("""
            INSERT INTO simplex.playlists (id, song_id, title, album, artist)
            VALUES (
                3fd2bedf-a8c8-455a-a462-0cd3a4353c54,
                fbdf82ed-0063-4796-9c7c-a3d4f47b4b25,
                'Memo From Turner',
                'Performance',
                'Mick Jager'
            );
        """)
        print('Data loaded.')

    @classmethod
    def query_schema(self):
        results = self.session.execute("""
            SELECT * FROM simplex.playlists
            WHERE id = 2cc9ccb7-6221-4ccb-8387-f22b6a1b354d;
        """)
        print("%-30s\t%-20s\t%-20s\n%s" %
            ("title", "album", "artist",
                "-------------------------------+-----------------------+--------------------") )
        for row in results:
            print("%-30s\t%-20s\t%-20s" % (row.title, row.album, row.artist) )

    @classmethod
    def update_schema(self):
        self.session.execute("""
            UPDATE simplex.songs
            SET tags = tags + { 'entre-deux-guerres' }
            WHERE id = 756716f7-2e54-4715-9f00-91dcbea6cf50;
        """)
        results = self.session.execute("""
            SELECT * FROM simplex.songs
            WHERE id = 756716f7-2e54-4715-9f00-91dcbea6cf50;
        """)
        print("%-30s\t%-20s\t%-20s%-30s\n%s" %
            ("title", "album", "artist",
                "tags", "-------------------------------+-----------------------+--------------------+-------------------------------") )
        for row in results:
            print("%-30s\t%-20s\t%-20s%-30s" %
                (row.title, row.album, row.artist, row.tags) )

    @classmethod
    def drop_schema(self, keyspace):
        self.session.execute("DROP keyspace " + keyspace + ";")
        print("Dropped keyspace " + keyspace)

    @classmethod
    def close(self):
        self.session.cluster.shutdown()
        self.session.shutdown()

class BoundStatementsClient(SimpleClient):
    @classmethod    
    def loadData(self):
        """
        Overload SimpleClient's method to use bound t=statements.
        """
        statement = self.session.prepare("""
            INSERT INTO songs
            (id, title, album, artist, tags)
            VALUES (?, ?, ?, ?, ?);
        """)
        boundStatement = BoundStatement(statement)
        tags = set(['jazz', '2013'])
        self.session.execute(boundStatement.bind(
            UUID("756716f7-2e54-4715-9f00-91dcbea6cf50"),
            "La Petite Tonkinoise",
            "Bye Bye Blackbird",
            "Jos�phine Baker",
            tags )
        )
        tags = set(['1996', 'birds'])
        self.session.execute(boundStatement.bind(
            UUID("f6071e72-48ec-4fcb-bf3e-379c8a696488"),
            "Die M�sch",
            "In Gold'", 
            "Willi Ostermann",
            tags )
        )
        tags = set(['1970', 'soundtrack'])
        self.session.execute(boundStatement.bind(
            UUID("fbdf82ed-0063-4796-9c7c-a3d4f47b4b25"),
            "Memo From Turner",
            "Performance",
            "Mick Jager",
            tags )
        )
        statement = getSession().prepare("""
            INSERT INTO playlists
            (id, song_id, title, album, artist)
            VALUES (?, ?, ?, ?, ?);
        """)
        boundStatement = BoundStatement(statement)
        getSession().execute(boundStatement.bind(
            UUID("2cc9ccb7-6221-4ccb-8387-f22b6a1b354d"),
            UUID("756716f7-2e54-4715-9f00-91dcbea6cf50"),
            "La Petite Tonkinoise",
            "Bye Bye Blackbird",
            "Jos�phine Baker") 
        )
        getSession().execute(boundStatement.bind(
            UUID("2cc9ccb7-6221-4ccb-8387-f22b6a1b354d"),
            UUID("f6071e72-48ec-4fcb-bf3e-379c8a696488"),
            "Die M�sch",
            "In Gold",
            "Willi Ostermann")
        )
        getSession().execute(boundStatement.bind(
            UUID("3fd2bedf-a8c8-455a-a462-0cd3a4353c54"),
            UUID("fbdf82ed-0063-4796-9c7c-a3d4f47b4b25"),
            "Memo From Turner",
            "Performance",
            "Mick Jager")
        )

# callback functions for the AsynchronousExample class

def print_errors(errors):
    print(errors)
    
def print_results(results):
    print("%-30s\t%-20s\t%-20s%-30s\n%s" %
        ("title", "album", "artist",
            "tags", "-------------------------------+-----------------------+--------------------+-------------------------------") )
    for row in results:
        print("%-30s\t%-20s\t%-20s%-30s" %
            (row.title, row.album, row.artist, row.tags) )


class AsynchronousExample(SimpleClient):
    @classmethod
    def query_schema(self):
        future_results =  self.session.execute_async("SELECT * FROM simplex.songs;")
        future_results.add_callbacks(print_results, print_errors)
            
# 

def main():
    logging.basicConfig()
    # client = SimpleClient()
    # client = BoundStatementsClient()
    client = AsynchronousExample()
    client.connect(['127.0.0.1'])
    client.create_schema()
    client.query_schema()
    client.update_schema()
    client.drop_schema("simplex")
    client.close()

if __name__ == "__main__":
    main()
