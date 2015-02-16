/* Delete all rows from tables */
DELETE FROM jester_rating;
DELETE FROM jester_joke;
DELETE FROM jester_user;
DELETE FROM jester_recommendermodel;

/* Reset auto increment fields */
ALTER TABLE jester_user AUTO_INCREMENT = 1;
ALTER TABLE jester_joke AUTO_INCREMENT = 1;
ALTER TABLE jester_rating AUTO_INCREMENT = 1;
ALTER TABLE jester_recommendermodel AUTO_INCREMENT = 1;