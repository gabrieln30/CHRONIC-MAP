# scripts/listar_modelos.py
import boto3

client = boto3.client("bedrock", region_name="us-east-1")
perfis = client.list_inference_profiles()["inferenceProfileSummaries"]
for p in perfis:
    if "claude" in p["inferenceProfileId"].lower():
        print(p["inferenceProfileId"])