CREATE TABLE usr_table (idx INTEGER PRIMARY KEY, usr_id varchar(20) NOT NULL, usr_pw varchar(20) NOT NULL, usr_mail varchar(40), usr_phone varchar(20));
CREATE TABLE board (idx INTEGER PRIMARY KEY, b_title varchar(20) NOT NULL, b_data TEXT, b_writer varchar(20) NOT NULL,b_filename TEXT, b_filepath TEXT, dt datetime default current_timestamp);
CREATE TABLE board_reply (idx INTEGER PRIMARY KEY, rep_parent INTEGER NOT NULL, req_depth INTEGER NOT NULL, req_order INTEGER NOT NULL, board_idx INTEGER NOT NULL, req_data TEXT, req_writer varchar(20), dt datetime default current_timestamp);
CREATE TABLE board_file (idx INTEGER PRIMARY KEY, board_idx INTEGER, file_path TEXT, dt datetime default current_timestamp)
