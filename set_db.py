from sqlalchemy import *

#Initialise a local database
engine = create_engine('sqlite:///wallet.db', connect_args={'check_same_thread': False})
meta = MetaData()

wallet = Table(
    'wallet', meta,
    Column('id', Integer, primary_key=True),
    Column('user', Text),
    Column('stock', String),
    Column('amount', Integer),
    Column('price', Float),
)

meta.create_all(engine)
