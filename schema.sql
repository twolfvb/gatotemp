drop table if exists tempLog;
create table tempLog (
  panel_id VARCHAR(100),
  date_log DATETIME NOT NULL,
  temperature FLOAT(5,2) NOT NULL
  );