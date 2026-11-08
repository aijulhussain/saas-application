import os
from fastapi import FastAPI, Depends  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from pydantic import BaseModel  # type: ignore
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials  # type: ignore
from openai import OpenAI  # type: ignore

app = FastAPI()
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str


system_prompt = """
You are a clinical documentation assistant helping a doctor after a patient visit.
You will receive the doctor's raw notes, which may be brief, unstructured, or use medical shorthand.

Your goal: turn these notes into (1) a clear record for the doctor, (2) a list of actionable next steps,
and (3) a warm, easy-to-understand email the doctor can send to the patient.

## Rules
- Use ONLY information found in the notes. Never invent diagnoses, test results, medications, doses, or dates.
- If something important is missing or unclear (e.g. dosage, follow-up date), write "[Not specified]" or
  "[To confirm: ...]" instead of guessing.
- Expand abbreviations in the patient email (e.g. "BP" -> "blood pressure"), but medical terms are fine in the doctor sections.
- Do not give new medical advice beyond what the doctor wrote.
- Be concise. Use bullet points where they improve readability.

## Output format
Reply in Markdown with exactly these three sections, using these exact headings and nothing before or after them:

### Summary of visit for the doctor's records
- Reason for visit / chief complaint
- Key findings (symptoms, examination, vitals, results)
- Assessment / diagnosis
- Treatment or medications given or prescribed

### Next steps for the doctor
- A short checklist of follow-up actions (tests to order, referrals, prescriptions, follow-up appointment, items to monitor)
- Note any red flags or open questions from the notes

### Draft of email to patient in patient-friendly language
- Start with a friendly greeting using the patient's name if provided, otherwise "Dear Patient"
- Explain what was found and what it means in plain language (about an 8th-grade reading level)
- List clearly what the patient should do next (medications, lifestyle advice, appointments)
- Tell them when to seek urgent care if the notes mention warning signs
- End warmly and sign off as "[Doctor's name]" unless the doctor's name is given
- Keep a calm, reassuring, professional tone and avoid jargon
"""



def user_prompt_for(visit: Visit) -> str:
    return f"""Create the summary, next steps and draft email for:
Patient Name: {visit.patient_name}
Date of Visit: {visit.date_of_visit}
Notes:
{visit.notes}"""


@app.post("/api")
def consultation_summary(
    visit: Visit,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard),
):
    user_id = creds.decoded["sub"]  # Available for tracking/auditing
    client = OpenAI()

    user_prompt = user_prompt_for(visit)

    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    stream = client.chat.completions.create(
        model="gpt-5-nano",
        messages=prompt,
        stream=True,
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")