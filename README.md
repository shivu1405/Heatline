# HeatLine

**Heat-safety reporting and escalation for outdoor and informal workers, including workers with no smartphone.**

Built for the Amazon Environmental Hack (Bharat Global Tour).

HeatLine lets a worker, a trusted helper, or an organization report unsafe heat conditions at a worksite. It scores the risk with a transparent point model, stores every report, and emails an alert when the risk is High or Extreme. The checks follow the Water. Rest. Shade. approach: cool drinking water, shade or a cool rest area, and regular breaks.

## The problem

Heat stress can cause dizziness and fainting and, at its worst, heat stroke. The people who work longest in the heat (construction, delivery, waste collection, street vending, agriculture) are often the least able to report unsafe conditions. Most reporting tools assume a smartphone, mobile data, and comfort with reading and typing in English.

## What works today

- **Three ways to report**, all feeding the same backend (table below).
- **A risk score** (0 to 130) and level (Low, Moderate, High, Extreme) returned instantly.
- **Persistent storage** of every report in DynamoDB.
- **Email alerts** through SNS for High and Extreme reports.
- **A consent check** for reports filed on a worker's behalf.
- **A reports tracker** (optional, see below) that lists stored reports and lets responders mark them open, in progress or resolved.

| Mode | Who uses it | What happens |
| --- | --- | --- |
| Worker self-report | A worker with a smartphone | The worker answers the questions in the web app |
| Phone-assisted report | A supervisor, volunteer, NGO worker or family member | The helper calls the worker, asks the questions, confirms the worker's consent, and files the report |
| Organization report | A student group, NGO, union, company or government team | The group reports a worksite, names the person responsible (the "fixer") and the action needed |

## Reaching workers without a smartphone

Phone-assisted reporting is how HeatLine reaches workers with a basic phone or low literacy today. Every question is a yes or no, or a number, so nothing has to be typed or read by the worker. The helper must confirm that the worker agreed before the report is saved.

A direct call line (the worker presses 1 for yes and 2 for no) is **designed and simulated, not live**. See [Phone line prototype](#phone-line-prototype-not-live).

## Architecture

```
Streamlit app  --HTTPS JSON-->  API Gateway  -->  Lambda (heatline-api)
                                                      |            |
                                                      v            v
                                               DynamoDB        SNS email alert
                                             (HeatReports)   (High / Extreme only)
```

1. The Streamlit app (`app.py`) collects the report and posts it as JSON.
2. API Gateway receives the request.
3. The `heatline-api` Lambda validates the report, calculates the score and level, and saves it.
4. DynamoDB stores every report permanently.
5. SNS emails an alert when the level is High or Extreme.

## Risk scoring

The score is a simple sum of points, so anyone can see why a report scored the way it did.

| Condition | Points |
| --- | --- |
| Temperature 34 to 36.9 C | +20 |
| Temperature 37 to 39.9 C | +30 |
| Temperature 40 C or above | +40 |
| Humidity 55 to 69% | +10 |
| Humidity 70% or above | +20 |
| No drinking water | +20 |
| No shade or rest area | +15 |
| No recent rest break | +10 |
| Worker reports symptoms | +25 |

| Score | Level | Response |
| --- | --- | --- |
| 0 to 34 | Low | Saved |
| 35 to 54 | Moderate | Saved |
| 55 to 74 | High | Saved and email alert |
| 75 and above | Extreme | Saved and email alert |

Example: 41 C, 75% humidity, no water, no shade, no break, and dizziness scores 40 + 20 + 20 + 15 + 10 + 25 = 130 (Extreme).

The weights are a simplified model chosen for transparency. They have **not been clinically validated**.

The web form also shows a "feels-like" heat index. It is for reference only and does not feed the score.

## API

`POST` a JSON report to the API endpoint (`API_URL` in `app.py`).

Request fields:

```json
{
  "channel": "web | phone_assisted | organization",
  "reportedBy": "self | field_agent | organization",
  "workerPhone": "",
  "agentName": "",
  "organization": "",
  "reporterName": "",
  "fixerName": "",
  "fixerContact": "",
  "consentConfirmed": true,
  "actionNeeded": "",
  "workType": "Construction",
  "location": "Chennai",
  "temperature": 41,
  "humidity": 75,
  "waterAvailable": false,
  "shadeAvailable": false,
  "restBreakTaken": false,
  "symptoms": true
}
```

Response fields: `riskLevel`, `riskScore`, `reportId`, `alertSent`.

Failure behaviour:

| Situation | Result |
| --- | --- |
| Body is not valid JSON | 400, nothing saved, no alert |
| DynamoDB write fails | 500, the app shows an error, no report is treated as submitted |
| SNS publish fails | The report is saved, the response has `alertSent: false`, and the app warns that the alert was not sent |

## Run the app locally

```bash
git clone <this-repo-url>
cd <repo-folder>
pip install streamlit requests
streamlit run app.py
```

`app.py` points at a deployed endpoint through the `API_URL` constant. To use your own AWS deployment, change that value (see below).

## Deploy the AWS side

1. **DynamoDB:** create a table named `HeatReports` with `reportId` as the partition key.
2. **SNS:** create a topic for alerts, subscribe an email address, and **confirm the subscription from the email**. Until it is confirmed, no email is delivered even though the publish succeeds.
3. **Lambda:** create the `heatline-api` function with permission to write to the table and publish to the topic.
4. **API Gateway:** expose the function over HTTPS and set `API_URL` in `app.py` to its URL.

## Reports tracker (optional)

`heatline_admin.py` is a separate Lambda that lists stored reports and updates their status. The Streamlit app shows it on the Track reports page when configured, and otherwise falls back to a list of this session's reports.

To enable it:

1. Create a Python 3.12 Lambda from `heatline_admin.py` with environment variable `ADMIN_KEY` set to a long random secret.
2. Give its role `dynamodb:Scan` and `dynamodb:UpdateItem` on the `HeatReports` table.
3. Create a Function URL for it.
4. In `.streamlit/secrets.toml` (never commit this file), add:

```toml
ADMIN_URL = "https://<your-function-url>/"
ADMIN_KEY = "<the same secret>"
```

The tracker masks worker phone numbers, but it is protected only by a shared key. Treat it as a prototype.

## Phone line prototype (not live)

- `connect_lambda.py` is a Lambda that converts keypad answers from an Amazon Connect call flow into a HeatLine report. It was tested locally with a mocked API only.
- `heatline-phone-demo.html` is an interactive simulation of the call and SMS flow.

Amazon Connect was not available on the AWS account used for this project, so no real number or call flow is deployed.

## Limitations

- The questions are English-only. For workers who cannot read them, the helper reads them aloud.
- Submitting a report requires no login, so anyone with the app link can submit one.
- The tracker uses a single shared key and scans the whole table, which does not scale.
- Alert delivery depends on a confirmed SNS email subscription. The app can only report what the API returns.
- The organization form collects the organization type and additional details, but they are not yet sent to the API.
- The scoring model has not been validated against clinical or field data.

## Roadmap

- Fixer dashboard for open High and Extreme reports
- Tamil and Hindi support
- SMS reporting with AWS End User Messaging
- Voice reporting with Amazon Connect
- Public heat-risk map by location
- Login for fixers and responders

## Project files

```
app.py                     Streamlit web app
heatline_admin.py          Admin Lambda: list reports, update status (optional)
connect_lambda.py          Amazon Connect bridge Lambda (prototype, not deployed)
heatline-phone-demo.html   Simulated call and SMS demo
```

Add the `heatline-api` Lambda source to the repository if it is not already there.

## Team Members

Shivasri S
Yashaswini S 
Shri Raama Krishnan J
