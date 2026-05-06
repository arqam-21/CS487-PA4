App Service is the right choice for the web frontend because it is a long-running, stateful HTTP server that needs to be persistent and non manual CI/CD. Unlike serverless options, it serves the UI instantly without cold-start delays.

Durable Functions is used for orchestration because the pipeline has multiple  steps (validate → report) that can take a lot of time. Plain HTTP functions would time out and lose state. Durable Functions checkpoint state after each activity,  automatic replay and retry on failure.

I was not able to do this part so i am not exactly sure how it works practically however from my attempts to do it and through the manual, there is declarative commands and a stable loadbalancer which helps control the pods.

3. Durable Functions vs Plain HTTP

1. Timeout: The outer function would need to wait synchronously for the report job , hitting the default 230-second HTTP timeout and failing on slow runs.
2. No retry/checkpoint: If the report activity threw an exception, there would be no automatic retry or checkpoint, enture progress will be lost

The orchestrator in durable checkpoints after validate_activity succeeds, so a failed report_activity retries without re-validating, and the async pattern means no HTTP connection is held open during the wait.

 Challenges Faced

1. ACR Pull 401 / Unauthorized: After pushing images to ACR, the AKS cluster initially failed to pull them with a 401 error. The fix was to attach the ACR to the AKS cluster using az aks update --attach-acr so the cluster had the correct pull credentials.

2. GitHub Actions Deployment Failure: The first GitHub Actions workflow run failed (Deployment ID 8b02d17, visible in the Deployment Center logs). Re-configuring the Deployment Center settings and updating the workflow file resolved it and the subsequent run succeeded.



<img width="697" height="349" alt="16" src="https://github.com/user-attachments/assets/9a7bd9e2-515e-4f8e-8f6a-73d356107629" />
<img width="532" height="371" alt="15" src="https://github.com/user-attachments/assets/785408d2-6ba8-450e-b2c4-65f59d56963e" />
<img width="960" height="506" alt="14" src="https://github.com/user-attachments/assets/eb2a5fda-3666-4db9-9ecd-bb4bec6b8c29" />
<img width="561" height="353" alt="13" src="https://github.com/user-attachments/assets/4dd10777-bad9-4e54-b9fb-1afd52fbc680" />
<img width="649" height="332" alt="12" src="https://github.com/user-attachments/assets/a8b16adc-e874-4041-be74-bb98bad3ba35" />
<img width="724" height="448" alt="11" src="https://github.com/user-attachments/assets/2c8fa787-98ac-41ef-8631-a1d859bae099" />
<img width="726" height="260" alt="10" src="https://github.com/user-attachments/assets/8ff19759-e288-40db-9d88-3a4d17326867" />
<img width="449" height="448" alt="9" src="https://github.com/user-attachments/assets/05d22698-e241-4c2f-9847-49af9f1476bd" />
<img width="960" height="509" alt="8" src="https://github.com/user-attachments/assets/bba3a99a-026c-43dc-bf01-5204362d0401" />
<img width="960" height="511" alt="7" src="https://github.com/user-attachments/assets/4e06bcc5-e15a-4276-b8df-99d4480ab8d2" />
<img width="960" height="508" alt="6" src="https://github.com/user-attachments/assets/5164c30b-91a8-4741-b6bd-e688072dd877" />
<img width="595" height="128" alt="5" src="https://github.com/user-attachments/assets/dee1eea2-a1a2-4386-8d80-089c6c84f25f" />
<img width="931" height="427" alt="4" src="https://github.com/user-attachments/assets/c569b4fd-a1af-49a5-9b41-2833d9246ede" />
<img width="960" height="510" alt="3" src="https://github.com/user-attachments/assets/0616f166-c0d7-4a52-92bb-465dedc4aaaa" />
<img width="960" height="509" alt="2" src="https://github.com/user-attachments/assets/eb89f844-65bc-4891-aa97-8027cffd4ae1" />
<img width="882" height="221" alt="1" src="https://github.com/user-attachments/assets/7e00635c-7225-4899-a908-189f4a47f898" />
<img width="918" height="92" alt="22" src="https://github.com/user-attachments/assets/f449efe5-c34e-42b5-a13b-f9e0d65b6f48" />
<img width="931" height="234" alt="21" src="https://github.com/user-attachments/assets/db1a52eb-fe49-4c71-9ac8-8c9406b11bfb" />
<img width="959" height="458" alt="20" src="https://github.com/user-attachments/assets/24afef1a-6136-4beb-8f92-583d7375c41a" />
<img width="960" height="510" alt="19" src="https://github.com/user-attachments/assets/11249084-66ac-4fcc-8f13-dd6e8332af36" />
<img width="960" height="509" alt="18" src="https://github.com/user-attachments/assets/c9ff5251-7679-4e21-b47c-d5183835ecc3" />
<img width="921" height="108" alt="17" src="https://github.com/user-attachments/assets/6ccf0e87-2ce4-4592-8e08-82e8cd576c96" />
