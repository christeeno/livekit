from __future__ import annotations
import sqlite3
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager
import os
import json
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


@dataclass
class Patient:
    id: str
    name: str
    age: int
    gender: str
    contact_information: str
    blood_group: str
    height: int
    weight: int


class DatabaseDriver:
    def __init__(self, db_path: str = "patient_db.sqlite"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    contact_information TEXT NOT NULL,
                    blood_group TEXT NOT NULL,
                    height INTEGER NOT NULL,
                    weight INTEGER NOT NULL
                )
            """)
            conn.commit()

    def create_patient(
        self,
        id: str,
        name: str,
        age: int,
        gender: str,
        contact_information: str,
        blood_group: str,
        height: int,
        weight: int,
    ) -> Patient:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO patients (id, name, age, gender, contact_information, blood_group, height, weight) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (id, name, age, gender, contact_information, blood_group, height, weight)
            )
            conn.commit()
            return Patient(
                id=id, name=name, age=age, gender=gender,
                contact_information=contact_information,
                blood_group=blood_group, height=height, weight=weight
            )

    def get_patient_by_id(self, id: str) -> Optional[Patient]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE id = ?", (id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Patient(
                id=row[0],
                name=row[1],
                age=row[2],
                gender=row[3],
                contact_information=row[4],
                blood_group=row[5],
                height=row[6],
                weight=row[7]
            )


async def send_patient_to_gemini(patient: Patient, output_path: str = "gemini_output.json"):
    """
    Sends patient data to the Gemini API and saves the response to a JSON file.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"Patient Data:\n"
                            f"ID: {patient.id}\n"
                            f"Name: {patient.name}\n"
                            f"Age: {patient.age}\n"
                            f"Gender: {patient.gender}\n"
                            f"Contact: {patient.contact_information}\n"
                            f"Blood Group: {patient.blood_group}\n"
                            f"Height: {patient.height}\n"
                            f"Weight: {patient.weight}"
                        )
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()

            # Save the Gemini response to a JSON file
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return data


# Demo usage
async def main():
    db = DatabaseDriver()

    # Uncomment to create a sample patient
    # db.create_patient(
    #     id="1234",
    #     name="John Doe",
    #     age=35,
    #     gender="Male",
    #     contact_information="john.doe@example.com",
    #     blood_group="O+",
    #     height=175,
    #     weight=70
    # )

    patient = db.get_patient_by_id("1234")
    if patient:
        response = await send_patient_to_gemini(patient, output_path="patient_1234_gemini.json")
        print("Gemini API response saved:", response)
    else:
        print("Patient not found")


if __name__ == "__main__":
    asyncio.run(main())
