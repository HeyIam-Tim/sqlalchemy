from sqlalchemy import text, insert, select, update

from src.database import sync_engine, session_factory
from src.models import metadata_obj, workers_table


# async def get_async():
#     async with async_engine.connect() as conn:
#         res = await conn.execute(text('SELECT 1, 2, 3 union select 4, 5, 6'))
#         print(f'{res.first()=}')
#         # conn.commit()


class SyncCore:

    @staticmethod
    def create_tables():
        sync_engine.echo = False
        metadata_obj.drop_all(sync_engine)
        metadata_obj.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with sync_engine.connect() as conn:
            # stmt = '''INSERT INTO workers (username) VALUES ('Bob'), ('Jonh');'''
            stmt = insert(workers_table).values([
                {'username': 'Jessica'},
                {'username': 'Ivan'},
            ])
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def select_workers():
        # with sync_engine.connect() as conn:
        #     query = select(workers_table)
        #     res = conn.execute(query)
        #     workers = res.all()
        #     print(f'{workers=}')
        with session_factory() as session:
            query = select(workers_table)
            res = session.execute(query)
            workers = res.all()
            print(f'{workers=}')

    @staticmethod
    def update_worker(worker_id: int = 1, new_username: str = 'Max'):
        with sync_engine.connect() as conn:
            # stmt = text("""UPDATE workers SET username=:username WHERE id=:id""")
            # stmt = stmt.bindparams(username=new_username, id=worker_id)
            # stmt = update(workers_table).values(username=new_username).where(workers_table.c.id==worker_id)
            # stmt = update(workers_table).values(username=new_username).filter(workers_table.c.id==worker_id)
            stmt = update(workers_table).values(username=new_username).filter_by(id=worker_id)
            conn.execute(stmt)
            conn.commit()
