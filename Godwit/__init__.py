from os import listdir
import os.path
from datetime import datetime as dt
import argparse

class Migrate:
    def __init__(self, conn, migration_dir, commit=True):
        self.conn = conn
        self.migration_dir = migration_dir
        self.commit = commit

    def get_current_version(self):
        cur = self.conn.cursor()
        try:
            try:
                cur.execute(self.query_curr_version)
                return cur.fetchone()[0]
            except:
                conn.rollback()
                return None
        finally:
            cur.close()

    def migrate(self, to_version):
        cur = self.conn.cursor()
        try:
            for migration_script in self._get_migration_scripts(self.get_current_version(), to_version):
                with open(os.path.join(self.migration_dir, migration_script), 'r') as script_file:
                    try:
                        print "Migrating to %s" % migration_script
                        cur.execute(script_file.read())
                        cur.execute(self.query_insert_version, (os.path.splitext(migration_script)[0], dt.now()))
                    except Exception, e:
                        conn.rollback()
                        print "Migration failed in script %s"
                        raise

            if self.commit:
                conn.commit()
            else:
                conn.rollback()
                print "Migration was rolled back since running in dry-run mode."
        finally:
            cur.close()

    def _get_migration_scripts(self, from_version, to_version):
        if from_version != None:
            scripts = [x for x in listdir(self.migration_dir)
                if x.endswith('.sql') and (x > ("%s.sql" % from_version) and x <= ("%s.sql" % to_version))]
        else:
            scripts = [x for x in listdir(self.migration_dir)
                if x.endswith('.sql') and x <= ("%s.sql" % to_version)]

        scripts.sort()
        return scripts

class MigratePostgres(Migrate):
    query_curr_version = 'select version from _version order by version desc limit 1'
    query_insert_version = 'insert into _version (version, datetime) values (%s, %s)'

    def __init__(self, conn, migration_dir, commit):
        Migrate.__init__(self, conn, migration_dir, commit)

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='If set, will rollback any migrations after they complete.')
    parser.add_argument('host')
    parser.add_argument('database')
    parser.add_argument('user')
    parser.add_argument('password')
    parser.add_argument('migrationdir')
    parser.add_argument('version')

    args = parser.parse_args(argv[1:len(argv)])

    conn = psycopg2.connect(host=args.host, database=args.database, user=args.user, password=args.password)
    try:
        m = MigratePostgres(conn, args.migrationdir, commit=not args.dry_run)
        m.migrate(args.version)
    finally:
        conn.close()

if __name__ == '__main__':
    import psycopg2
    from sys import argv

    main(argv)
