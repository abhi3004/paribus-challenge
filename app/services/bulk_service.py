import time
from app.storage.progress_store import progress_store

class BulkHospitalService:
    def __init__(self, hospital_client):
        self.hospital_client = hospital_client

    async def process_csv_rows(self, batch_id: str, hospitals: list[dict]):
        start = time.time()
        await progress_store.update(batch_id, status="processing")

        created_hospitals = []
        failed_hospitals = []

        try:
            for index, row in enumerate(hospitals, start=1):
                payload = {
                    "name": row["name"],
                    "address": row["address"],
                    "phone": row["phone"],
                    "creation_batch_id": batch_id,
                }

                try:
                    hospital = await self.hospital_client.create_hospital(payload)
                    created_hospitals.append({
                        "row": index,
                        "hospital_id": hospital["id"],
                        "name": hospital["name"],
                        "status": "created"
                        })
                except Exception as error:
                    failed_hospitals.append({
                        "row": index,
                        "name": row.get("name"),
                        "status": "failed",
                        "error": str(error)
                        })
                batch_activated = False
            current_progress = await progress_store.get(batch_id)
            if current_progress["failed_hospitals"] == 0:
                await self.hospital_client.activate_batch(batch_id)

                hospitals = current_progress["hospitals"]
                for hospital in hospitals:
                    hospital["status"] = "created_and_activated"

                await progress_store.update(
                    batch_id,
                    status="completed",
                    batch_activated=True,
                    hospitals=hospitals,
                    processing_time_seconds=round(time.time() - start, 2),
                )

            else:
                await self.hospital_client.delete_batch(batch_id)

                await progress_store.update(
                    batch_id,
                    status="failed",
                    batch_activated=False,
                    processing_time_seconds=round(time.time() - start, 2),
                )

        except Exception as error:
            await progress_store.update(
                batch_id,
                status="failed",
                error=str(error),
                processing_time_seconds=round(time.time() - start, 2),
            )

