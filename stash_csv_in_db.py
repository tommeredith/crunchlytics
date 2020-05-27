import psycopg2
from psycopg2.extensions import AsIs


def stash_in_db(list):
    print('=========== STASHING ==============')
    print('')
    print('')
    conn = psycopg2.connect("host='all-the-stats-bundes.chure6gtnama.us-east-1.rds.amazonaws.com' port='5432' "
                            "dbname='stats_data' user='bundesstats' password='bundesstats'")
    delete_statement = 'delete from full_match_stats_bundesliga;'
    cursor = conn.cursor()
    cursor.execute(delete_statement)
    for index in range(len(list)):
        list[index]["index"] = index
        columns = list[index].keys()
        values = [list[index][column] for column in columns]

        insert_statement = 'insert into full_match_stats_bundesliga (%s) values %s'

        cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))

    conn.commit()
    conn.close()
    print('=========== DONE STASHING ==============')
    print('')
    print('')
