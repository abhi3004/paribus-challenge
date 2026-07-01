import asyncio
from copy import deepcopy


class ProgressStore:
    def __init__(self):
        self._store = {}
        self._lock = asyncio.Lock()

    async def create(self, batch_id: str, total: int):
        async with self._lock:
            self._store[batch_id] = {
                "batch_id": batch_id,
                "status": "queued",
                "total_hospitals": total,
                "processed_hospitals": 0,
                "failed_hospitals": 0,
                "batch_activated": False,
                "hospitals": [],
                "errors": [],
            }

    async def update(self, batch_id: str, **kwargs):
        async with self._lock:
            if batch_id not in self._store:
                return

            self._store[batch_id].update(kwargs)

    async def add_hospital(self, batch_id: str, hospital: dict):
        async with self._lock:
            self._store[batch_id]["hospitals"].append(hospital)
            self._store[batch_id]["processed_hospitals"] += 1

    async def add_error(self, batch_id: str, error: dict):
        async with self._lock:
            self._store[batch_id]["errors"].append(error)
            self._store[batch_id]["failed_hospitals"] += 1

    async def get(self, batch_id: str):
        async with self._lock:
            data = self._store.get(batch_id)
            return deepcopy(data) if data else None


progress_store = ProgressStore()