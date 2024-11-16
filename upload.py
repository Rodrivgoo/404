from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "rare-keep-441919-k9-655242ccdbdc.json"


# Configura el cliente de Azure
endpoint = "https://review-404.cognitiveservices.azure.com/"
api_key = "9C8gqUIbamr2cQF1mjHuTYAVZsAu6bPvCXFvOLah71D6tFa1PoD8JQQJ99AKACYeBjFXJ3w3AAALACOGW0Z5"

client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

# Ruta del archivo PDF
pdf_path = "Scan_UAI-1-13-14.pdf"

# Abrir el archivo PDF y procesarlo
with open(pdf_path, "rb") as f:
    poller = client.begin_analyze_document("Test2", f)

# Esperar a que se complete el análisis
result = poller.result()

# Guardar la respuesta directamente como JSON
with open("result.json", "w") as json_file:
    json.dump(result.to_dict(), json_file, ensure_ascii=False, indent=4)

with open("result.json", "r") as json_file:
    data = json.load(json_file)

# Filtrar los valores deseados
filtered_data = []
for document in data["documents"]:
    doc_info = {
        "fields": {}
    }
    
    # Iterar sobre los campos de cada documento
    for key, field in document.get("fields", {}).items():
        doc_info["fields"][key] = {
            "value": field.get("value"),
            "confidence": field.get("confidence")
        }
    
    filtered_data.append(doc_info)

# Convertir los datos filtrados a JSON string formateado
filtered_data_json = json.dumps(filtered_data, ensure_ascii=False, indent=4)

import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

def generate():
    vertexai.init(project="rare-keep-441919-k9", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-flash-002",
    )
    responses = model.generate_content(
        [text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    for response in responses:
        print(response.text, end="")


# Crear el texto dinámico
text1 = f"""*Grading Instruction for LLM*

### Input:
1. *Rubric*: Each question (e.g., p1, p2, p3) has an expected answer format and three possible scores:
  - *0 (Malo)*: Incorrect or missing answer.
  - *1 (Máscara o Dirección buena / Un extremo bueno)*: Partial but acceptable answer.
  - *2 (Bueno)*: Correct answer.
Think your results, do not compare it directly
Consider \\n a line break
  *Example for p1*: 
  - Expected answers: 10.11.2.0/24 or {{"red": "10.11.2.0", "mask": "24"}}.

2. *Student Answers*: Each answer includes:
  - *Qn*: Question text.
  - *An*: Answer text.
  - *Confidence*: OCR AI confidence (0 to 1).

### Grading Logic:
1. *Match the Answer*:
  - Compare student’s answer to the rubric's expected answers. For numeric answers like IPs and subnets, check for correct format and values.
  - If the answer is partially correct, assign a score of 1.
  - If the answer is fully correct, assign a score of 2.

2. *Points*: Assign points based on rubric alignment:
  - *0* for incorrect or missing answers.
  - *1* for partial correctness.
  - *2* for complete correctness.

3. *Confidence*:
  - Reflect OCR confidence in the grading confidence percentage:
   - *Low confidence (< 0.5)*: Lower grading confidence.
   - *High confidence (> 0.75)*: Higher grading confidence.

### Output Format:
json
{{
  "p1": {{
    "points": <score>,
    "confidence": <confidence_percentage>
  }}

Value the following response:

{filtered_data_json}
"""

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 2,
    "top_p": 0.95,
    "response_mime_type": "application/json",
    "response_schema": {"type":"OBJECT","properties":{"response":{"type":"STRING"}}},
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

generate()