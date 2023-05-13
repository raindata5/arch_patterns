-- begin transaction;
commit transaction;
truncate  "batch" cascade ;
truncate  "order" cascade;
truncate  "order_line" cascade ;
truncate "allocation" cascade;
-- truncate  "_Production".businessholding cascade ;
-- truncate  "_Production".businesscategorybridge cascade ;
-- truncate  "_Production".countygrowth cascade;
-- truncate  "_Production".business cascade;
-- truncate "_Production".businesscategory cascade;
-- truncate "_Production".city cascade;
-- truncate "_Production".county cascade;
-- truncate "_Production".eventcategory cascade;
-- truncate "_Production".paymentlevel cascade;
-- truncate "_Production".state cascade;
-- truncate "_Production".country cascade;
-- truncate "_Production".transactiontype cascade;
-- truncate "_Production".user cascade;
-- truncate "_Production".authuser cascade;
commit transaction;












-- pytest -x -v -s --disable-warnings tests/tests_api.py
-- from sqlalchemy import create_engine, select
-- from sqlalchemy.orm import registry, relationship, sessionmaker
-- engine = create_engine("postgresql://postgres:example@postgres:5432")
-- Session = sessionmaker(bind=engine, expire_on_commit=False)
-- s = Session()
-- list(s.execute("select * from order_line"))