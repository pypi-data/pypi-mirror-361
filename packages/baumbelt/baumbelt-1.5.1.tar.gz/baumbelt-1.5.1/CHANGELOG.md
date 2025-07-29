# Changelog

## 1.1.0

- use Django's `connection.execute_wrapper` for SQL logging

## 1.2.0

- add s3 utils for django package

## 1.3.0

- add CdnBulkStaticStorage class to django package

## 1.3.1

- add utility management commands for s3 utils

## 1.5.1

- change the use of Django's `connection.execute_wrapper` to `connections[db_name].execute_wrapper` for SQL logging on
  non-default dbs
