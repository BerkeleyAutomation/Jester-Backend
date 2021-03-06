/* Delete all rows from tables */
DELETE FROM jester_userlog;
DELETE FROM jester_recommenderlog;
DELETE FROM jester_rating;
DELETE FROM jester_rater;
DELETE FROM jester_joke;
DELETE FROM jester_recommendermodel;
DELETE FROM auth_user;

/* Reset auto increment fields */
ALTER TABLE jester_rater AUTO_INCREMENT = 1;
ALTER TABLE jester_joke AUTO_INCREMENT = 1;
ALTER TABLE jester_rating AUTO_INCREMENT = 1;
ALTER TABLE jester_recommendermodel AUTO_INCREMENT = 1;
ALTER TABLE auth_user AUTO_INCREMENT = 1;
ALTER TABLE jester_userlog AUTO_INCREMENT = 1;
ALTER TABLE jester_recommenderlog AUTO_INCREMENT = 1;