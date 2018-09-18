CREATE TABLE usr_table (idx INTEGER PRIMARY KEY, usr_id varchar(20), usr_pw varchar(20), usr_mail varchar(40));
CREATE TABLE board (idx INTEGER PRIMARY KEY, b_title varchar(20), b_data TEXT, b_writer varchar(20), dt datetime default current_timestamp);
CREATE TABLE board_reply (idx INTEGER PRIMARY KEY, rep_parent INTEGER, req_depth INTEGER, req_order INTEGER, board_idx INTEGER, req_data TEXT, req_writer varchar(20), dt datetime default current_timestamp);
