import asyncio
import os
import sys

# import uvicorn
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(1, os.path.join(sys.path[0], '..'))

# from queries.core import create_tables, insert_data
from queries.core import SyncCore
from queries.orm import SyncORM
# from queries.orm import insert_data, create_tables

# create_tables()
# insert_data()

# asyncio.run(insert_data())


SyncORM.create_tables()
SyncORM.insert_workers()

# SyncCore.select_workers()
# SyncCore.update_worker()

SyncORM.select_workers()
SyncORM.update_worker()

SyncORM.insert_resumes()
SyncORM.insert_additinal_resumes()
# SyncORM.select_resumes_avg_compensation()
# SyncORM.join_cte_subquery_window_func()
# SyncORM.select_workers_with_lazy_relationship()
# SyncORM.select_workers_with_joined_relationship()
SyncORM.select_workers_with_selectin_relationship()
