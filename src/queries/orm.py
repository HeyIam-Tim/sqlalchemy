from sqlalchemy import text, insert, select, func, cast, Integer, and_, or_
from sqlalchemy.orm import aliased, joinedload, selectinload

from src.database import sync_engine, session_factory, async_session_factory, Base
from src.models import WorkersOrm, Resume, WorkLoad


# from src.models import metadata_obj, WorkersOrm


# async def get_async():
#     async with async_engine.connect() as conn:
#         res = await conn.execute(text('SELECT 1, 2, 3 union select 4, 5, 6'))
#         print(f'{res.first()=}')
#         # conn.commit()

class SyncORM:

    @staticmethod
    def create_tables():
        # sync_engine.echo = False
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)
        # sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with session_factory() as session:
            worker_bob = WorkersOrm(username='Bob')
            worker_volk = WorkersOrm(username='Volk')
            session.add_all([worker_bob, worker_volk])
            session.flush()
            session.commit()

    @staticmethod
    def select_workers():
        with session_factory() as session:
            # worker_id = 1
            # worker = session.get(WorkersOrm, worker_id)
            query = select(WorkersOrm)
            res = session.execute(query)
            workers_orm = res.scalars().all()
            print(f'{workers_orm=}')

    @staticmethod
    def update_worker(worker_id: int | None = None, new_username: str = 'MaxORM'):
        with session_factory() as session:
            worker_id = 1
            worker = session.get(WorkersOrm, worker_id)
            worker.username = new_username
            # session.expire_all()
            session.refresh(worker)
            session.commit()

    @staticmethod
    def insert_resumes():
        with session_factory() as session:
            resume1 = Resume(
                title='PYTHON DEVELOPER',
                compensation=150000,
                workload=WorkLoad.part_time,
                worker_id=1,
            )
            resume2 = Resume(
                title='BACKEND PYTHON DEVELOPER',
                compensation=200000,
                workload=WorkLoad.full_time,
                worker_id=1,
            )
            resume3 = Resume(
                title='JAVASCRIPT DEVELOPER',
                compensation=100000,
                workload=WorkLoad.part_time,
                worker_id=2,
            )
            resume4 = Resume(
                title='FRONTEND DEVELOPER',
                compensation=150000,
                workload=WorkLoad.full_time,
                worker_id=2,
            )
            session.add_all([resume1, resume2, resume3, resume4])
            session.commit()

    @staticmethod
    def select_resumes_avg_compensation():
        with session_factory() as session:
            query = (
                select(
                    Resume.workload,
                    cast(func.avg(Resume.compensation), Integer).label('avg_compensation'),
                )
                .select_from(Resume)
                .filter(
                    or_(
                        Resume.title.icontains('PYTHON'),
                        # Resume.title.contains('Python'),
                        Resume.title.icontains('BACKEND'),
                        # Resume.title.contains('Backend'),
                    ),
                    and_(
                        Resume.compensation > 90000,
                    ),
                )
                .group_by(Resume.workload)
                .having(cast(func.avg(Resume.compensation), Integer) > 70000)
            )
            print(query.compile(compile_kwargs={'literal_binds': True}))
            res = session.execute(query)
            result = res.all()
            print(result)

    @staticmethod
    def insert_additinal_resumes():
        with session_factory() as session:
            workers = [
                {"username": "Artem"},  # id 3
                {"username": "Roman"},  # id 4
                {"username": "Petr"},   # id 5
            ]
            resumes = [
                {"title": "Python программист", "compensation": 60000, "workload": "full_time", "worker_id": 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "part_time", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "part_time", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "full_time", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "full_time", "worker_id": 5},
            ]
            insert_workers = insert(WorkersOrm).values(workers)
            insert_resumes = insert(Resume).values(resumes)
            session.execute(insert_workers)
            session.execute(insert_resumes)
            session.commit()

    @staticmethod
    def join_cte_subquery_window_func(like_language: str = ''):
        """
        with helper2 as (
            select *, compensation - avg_compensation as compensation_diff from
                (select
                    w.id,
                    w.username,
                    r.compensation,
                    r.workload,
                    avg(r.compensation) over(partition by r.workload)::int as avg_workload_compensation
                from
                    resume r
                join workers w on r.worker_id = w.id) helper1
        )

        select * from helper2
        order by compensation_diff desc;
        :return:
        """

        like_language = 'Python'
        with session_factory() as session:
            r = aliased(Resume)
            w = aliased(WorkersOrm)

            subq = (
                select(
                    r,
                    w,
                    func.avg(r.compensation).over(partition_by=r.workload).cast(Integer).label('avg_workload_compensation')
                )
                .join(
                     r, r.worker_id == w.id
                ).subquery('helper1 ')
            )
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label('compensation_diff'),
                )
                .cte('helper2')
            )
            query = (
                select(cte)
                .order_by(cte.c.compensation_diff.desc())
            )
            res = session.execute(query)
            result = res.all()
            print(query.compile(compile_kwargs={'literal_binds': True}))
            print(result)

    @staticmethod
    def select_workers_with_lazy_relationship():
        with session_factory() as session:
            query = select(WorkersOrm)
            res = session.execute(query)
            result = res.scalars().all()
            worker_1_resumes = result[0].resumes
            print('WORKER_1_RESUMES: ', worker_1_resumes)

            worker_2_resumes = result[1].resumes
            print('WORKER_2_RESUMES: ', worker_2_resumes)

            return result

    @staticmethod
    def select_workers_with_joined_relationship():
        with session_factory() as session:
            query = select(WorkersOrm).options(joinedload(WorkersOrm.resumes))
            res = session.execute(query)
            result = res.unique().scalars().all()
            worker_1_resumes = result[0].resumes
            print('WORKER_1_RESUMES: ', worker_1_resumes)

            worker_2_resumes = result[1].resumes
            print('WORKER_2_RESUMES: ', worker_2_resumes)

            return result

    @staticmethod
    def select_workers_with_selectin_relationship():
        with session_factory() as session:
            query = select(WorkersOrm).options(selectinload(WorkersOrm.resumes))
            res = session.execute(query)
            result = res.unique().scalars().all()
            worker_1_resumes = result[0].resumes
            print('WORKER_1_RESUMES: ', worker_1_resumes)

            worker_2_resumes = result[1].resumes
            print('WORKER_2_RESUMES: ', worker_2_resumes)

            return result

# async def insert_data():
#     async with async_session_factory() as session:
#         worker_bob = WorkersOrm(username='Bob')
#         worker_volk = WorkersOrm(username='Volk')
#         session.add_all([worker_bob, worker_volk])
#         await session.commit()
