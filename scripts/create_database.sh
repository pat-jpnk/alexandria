db_name="${1:-alexandria}"      # default positional argument

cd ..
cat sql/create_db.sql | sqlite3 $db_name.db


# check permissions todd [ ]

