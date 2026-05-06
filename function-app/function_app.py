import azure.functions as func
import azure.durable_functions as df
import requests
import os
import time
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (
    ContainerGroup, Container, ResourceRequirements,
    ResourceRequests, ImageRegistryCredential, OperatingSystemTypes,
    ContainerGroupRestartPolicy, EnvironmentVariable
)

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="orchestrators/{functionName}")
@app.durable_client_input(client_name="client")
async def http_starter(req: func.HttpRequest, client):
    function_name = req.route_params.get("functionName")
    payload = req.get_json()
    instance_id = await client.start_new(function_name, None, payload)
    return client.create_check_status_response(req, instance_id)

@app.orchestration_trigger(context_name="context")
def my_orchestrator(context: df.DurableOrchestrationContext):
    order = context.get_input()
    validation = yield context.call_activity("validate_activity", order)
    if not validation.get("valid"):
        return {"status": "rejected", "reason": validation.get("reason", "unknown")}
    report_url = yield context.call_activity("report_activity", order)
    return {"status": "completed", "report_url": report_url}

@app.activity_trigger(input_name="order")
def validate_activity(order: dict) -> dict:
    validate_url = os.environ["VALIDATE_URL"]
    response = requests.post(validate_url, json=order, timeout=30)
    return response.json()

@app.activity_trigger(input_name="order")
def report_activity(order: dict) -> str:
    subscription_id     = os.environ["SUBSCRIPTION_ID"]
    resource_group      = os.environ["REPORT_RG"]
    location            = os.environ["REPORT_LOCATION"]
    report_image        = os.environ["REPORT_IMAGE"]
    acr_server          = os.environ["ACR_SERVER"]
    acr_username        = os.environ["ACR_USERNAME"]
    acr_password        = os.environ["ACR_PASSWORD"]
    storage_account_url = os.environ["STORAGE_ACCOUNT_URL"]
    azure_client_id     = os.environ["AZURE_CLIENT_ID"]

    order_id = order["order_id"]
    container_name = f"ci-report-{order_id}".lower().replace("_", "-")

    credential = DefaultAzureCredential(managed_identity_client_id=azure_client_id)
    aci_client = ContainerInstanceManagementClient(credential, subscription_id)

    container_group = ContainerGroup(
        location=location,
        os_type=OperatingSystemTypes.linux,
        restart_policy=ContainerGroupRestartPolicy.never,
        image_registry_credentials=[
            ImageRegistryCredential(server=acr_server, username=acr_username, password=acr_password)
        ],
        containers=[
            Container(
                name="report-job",
                image=report_image,
                resources=ResourceRequirements(
                    requests=ResourceRequests(cpu=1.0, memory_in_gb=1.5)
                ),
                environment_variables=[
                    EnvironmentVariable(name="ORDER_ID", value=order_id),
                    EnvironmentVariable(name="ORDER_JSON", value=str(order)),
                    EnvironmentVariable(name="STORAGE_ACCOUNT_URL", value=storage_account_url),
                    EnvironmentVariable(name="AZURE_CLIENT_ID", value=azure_client_id),
                ]
            )
        ]
    )

    aci_client.container_groups.begin_create_or_update(
        resource_group, container_name, container_group
    ).result()

    deadline = time.time() + 300
    while time.time() < deadline:
        cg = aci_client.container_groups.get(resource_group, container_name)
        state = cg.containers[0].instance_view.current_state.state if cg.containers[0].instance_view else "Unknown"
        logging.info(f"ACI state: {state}")
        if state == "Terminated":
            break
        time.sleep(10)

    aci_client.container_groups.begin_delete(resource_group, container_name)
    return f"https://pa426100095.blob.core.windows.net/reports/{order_id}.pdf"
