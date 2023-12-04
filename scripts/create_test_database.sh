db_name="${1:-alexandria_test}"      # default positional argument

cat ../sql/create_test_db.sql | sqlite3 ../$db_name.db